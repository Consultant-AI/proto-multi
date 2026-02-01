"""Payment API endpoints using Stripe"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import stripe
import logging

from app.db.connection import get_db
from app.db.models import User, Subscription
from app.auth.middleware import get_current_user
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize Stripe
if settings.stripe_secret_key:
    stripe.api_key = settings.stripe_secret_key


class CreateCheckoutRequest(BaseModel):
    plan_type: str  # 'starter', 'pro', 'enterprise'
    success_url: str
    cancel_url: str


class CreateCheckoutResponse(BaseModel):
    checkout_url: str
    session_id: str


class SubscriptionResponse(BaseModel):
    id: str
    plan_type: str
    status: str
    instance_type: str
    max_workers: int
    current_period_end: Optional[datetime]


# Plan configuration
PLAN_CONFIG = {
    "starter": {
        "instance_type": "t3.medium",
        "max_workers": 2,
        "price_id_key": "stripe_price_id_starter",
    },
    "pro": {
        "instance_type": "t3.large",
        "max_workers": 5,
        "price_id_key": "stripe_price_id_pro",
    },
    "enterprise": {
        "instance_type": "t3.xlarge",
        "max_workers": 10,
        "price_id_key": "stripe_price_id_enterprise",
    },
}


def is_stripe_configured() -> bool:
    """Check if Stripe is properly configured with real keys (not placeholders)"""
    secret = settings.stripe_secret_key or ""
    pub = settings.stripe_publishable_key or ""
    # Check that keys exist and aren't placeholder values
    return bool(
        secret and pub and
        "REPLACE" not in secret and "REPLACE" not in pub and
        (secret.startswith("sk_test_") or secret.startswith("sk_live_")) and
        (pub.startswith("pk_test_") or pub.startswith("pk_live_"))
    )


@router.get("/config")
async def get_stripe_config():
    """Get Stripe publishable key for frontend"""
    # Return config even if Stripe is not configured - frontend will handle it
    return {
        "configured": is_stripe_configured(),
        "publishable_key": settings.stripe_publishable_key or "",
        "dev_mode": settings.environment == "development" or not is_stripe_configured(),
        "plans": {
            "starter": {"name": "Starter", "instance_type": "t3.medium", "max_workers": 2},
            "pro": {"name": "Pro", "instance_type": "t3.large", "max_workers": 5},
            "enterprise": {"name": "Enterprise", "instance_type": "t3.xlarge", "max_workers": 10},
        }
    }


@router.post("/create-checkout", response_model=CreateCheckoutResponse)
async def create_checkout_session(
    request: CreateCheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a Stripe Checkout session for subscription"""
    if not settings.stripe_secret_key:
        raise HTTPException(status_code=503, detail="Stripe not configured")

    if request.plan_type not in PLAN_CONFIG:
        raise HTTPException(status_code=400, detail="Invalid plan type")

    plan = PLAN_CONFIG[request.plan_type]
    price_id = getattr(settings, plan["price_id_key"])

    if not price_id:
        raise HTTPException(status_code=503, detail=f"Price not configured for {request.plan_type} plan")

    try:
        # Get or create Stripe customer
        if not current_user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=current_user.email,
                metadata={"user_id": str(current_user.id)}
            )
            current_user.stripe_customer_id = customer.id
            await db.commit()

        # Create checkout session
        checkout_session = stripe.checkout.Session.create(
            customer=current_user.stripe_customer_id,
            payment_method_types=["card"],
            line_items=[{
                "price": price_id,
                "quantity": 1,
            }],
            mode="subscription",
            success_url=request.success_url + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=request.cancel_url,
            metadata={
                "user_id": str(current_user.id),
                "plan_type": request.plan_type,
            },
        )

        return CreateCheckoutResponse(
            checkout_url=checkout_session.url,
            session_id=checkout_session.id,
        )

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/subscription", response_model=Optional[SubscriptionResponse])
async def get_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's active subscription"""
    # In dev mode without Stripe, return a free dev subscription
    if not is_stripe_configured():
        return SubscriptionResponse(
            id="dev-subscription",
            plan_type="dev",
            status="active",
            instance_type="t3.large",
            max_workers=5,  # Generous limit for development
            current_period_end=None,
        )

    result = await db.execute(
        select(Subscription)
        .where(Subscription.user_id == current_user.id)
        .where(Subscription.status.in_(["active", "pending"]))
        .order_by(Subscription.created_at.desc())
    )
    subscription = result.scalar_one_or_none()

    if not subscription:
        return None

    return SubscriptionResponse(
        id=str(subscription.id),
        plan_type=subscription.plan_type,
        status=subscription.status,
        instance_type=subscription.instance_type,
        max_workers=subscription.max_workers,
        current_period_end=subscription.current_period_end,
    )


@router.post("/cancel")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cancel the current subscription"""
    if not settings.stripe_secret_key:
        raise HTTPException(status_code=503, detail="Stripe not configured")

    result = await db.execute(
        select(Subscription)
        .where(Subscription.user_id == current_user.id)
        .where(Subscription.status == "active")
    )
    subscription = result.scalar_one_or_none()

    if not subscription:
        raise HTTPException(status_code=404, detail="No active subscription found")

    try:
        # Cancel at period end (user keeps access until end of billing period)
        stripe.Subscription.modify(
            subscription.stripe_subscription_id,
            cancel_at_period_end=True
        )

        subscription.status = "canceled"
        await db.commit()

        return {"message": "Subscription will be canceled at end of billing period"}

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Handle Stripe webhooks"""
    if not settings.stripe_webhook_secret:
        raise HTTPException(status_code=503, detail="Webhook secret not configured")

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle the event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        await handle_checkout_completed(session, db)

    elif event["type"] == "customer.subscription.updated":
        subscription = event["data"]["object"]
        await handle_subscription_updated(subscription, db)

    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        await handle_subscription_deleted(subscription, db)

    elif event["type"] == "invoice.payment_failed":
        invoice = event["data"]["object"]
        await handle_payment_failed(invoice, db)

    return {"status": "ok"}


async def handle_checkout_completed(session: dict, db: AsyncSession):
    """Handle successful checkout"""
    user_id = session.get("metadata", {}).get("user_id")
    plan_type = session.get("metadata", {}).get("plan_type")
    subscription_id = session.get("subscription")

    if not user_id or not plan_type:
        logger.error("Missing user_id or plan_type in checkout session metadata")
        return

    plan = PLAN_CONFIG.get(plan_type)
    if not plan:
        logger.error(f"Unknown plan type: {plan_type}")
        return

    # Get subscription details from Stripe
    stripe_sub = stripe.Subscription.retrieve(subscription_id)

    # Create subscription record
    import uuid
    subscription = Subscription(
        id=uuid.uuid4(),
        user_id=uuid.UUID(user_id),
        stripe_subscription_id=subscription_id,
        stripe_price_id=stripe_sub["items"]["data"][0]["price"]["id"],
        plan_type=plan_type,
        status="active",
        instance_type=plan["instance_type"],
        max_workers=plan["max_workers"],
        current_period_start=datetime.fromtimestamp(stripe_sub["current_period_start"]),
        current_period_end=datetime.fromtimestamp(stripe_sub["current_period_end"]),
    )

    db.add(subscription)
    await db.commit()
    logger.info(f"Created subscription for user {user_id}: {plan_type}")


async def handle_subscription_updated(stripe_sub: dict, db: AsyncSession):
    """Handle subscription updates"""
    result = await db.execute(
        select(Subscription).where(
            Subscription.stripe_subscription_id == stripe_sub["id"]
        )
    )
    subscription = result.scalar_one_or_none()

    if subscription:
        subscription.status = stripe_sub["status"]
        subscription.current_period_start = datetime.fromtimestamp(stripe_sub["current_period_start"])
        subscription.current_period_end = datetime.fromtimestamp(stripe_sub["current_period_end"])
        await db.commit()
        logger.info(f"Updated subscription {stripe_sub['id']}: {stripe_sub['status']}")


async def handle_subscription_deleted(stripe_sub: dict, db: AsyncSession):
    """Handle subscription cancellation"""
    result = await db.execute(
        select(Subscription).where(
            Subscription.stripe_subscription_id == stripe_sub["id"]
        )
    )
    subscription = result.scalar_one_or_none()

    if subscription:
        subscription.status = "canceled"
        await db.commit()
        logger.info(f"Canceled subscription {stripe_sub['id']}")


async def handle_payment_failed(invoice: dict, db: AsyncSession):
    """Handle failed payment"""
    subscription_id = invoice.get("subscription")
    if not subscription_id:
        return

    result = await db.execute(
        select(Subscription).where(
            Subscription.stripe_subscription_id == subscription_id
        )
    )
    subscription = result.scalar_one_or_none()

    if subscription:
        subscription.status = "past_due"
        await db.commit()
        logger.warning(f"Payment failed for subscription {subscription_id}")
