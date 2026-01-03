"""
Revenue Engine.

Handles billing, invoicing, and payments.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from .types import (
    Customer,
    Invoice,
    InvoiceItem,
    InvoiceStatus,
    Payment,
    PaymentStatus,
)


class RevenueEngine:
    """
    Revenue management engine.

    Features:
    - Customer management
    - Invoice creation and tracking
    - Payment processing (Stripe integration placeholder)
    - Revenue reporting
    """

    def __init__(self, data_dir: Path | None = None):
        self._data_dir = data_dir or Path.home() / ".proto" / "company" / "business" / "revenue"
        self._data_dir.mkdir(parents=True, exist_ok=True)

        self._customers: dict[str, Customer] = {}
        self._invoices: dict[str, Invoice] = {}
        self._payments: dict[str, Payment] = {}

        # Stripe client (placeholder)
        self._stripe_api_key: str | None = None

        self._load()

    def _load(self) -> None:
        """Load data from disk."""
        # Load customers
        customers_file = self._data_dir / "customers.json"
        if customers_file.exists():
            try:
                with open(customers_file, "r") as f:
                    data = json.load(f)
                for cust in data:
                    c = Customer(
                        id=cust["id"],
                        name=cust["name"],
                        email=cust.get("email", ""),
                        company=cust.get("company", ""),
                    )
                    self._customers[c.id] = c
            except Exception:
                pass

        # Load invoices
        invoices_file = self._data_dir / "invoices.json"
        if invoices_file.exists():
            try:
                with open(invoices_file, "r") as f:
                    data = json.load(f)
                for inv in data:
                    items = [
                        InvoiceItem(
                            description=i["description"],
                            quantity=i["quantity"],
                            unit_price=i["unit_price"],
                            tax_rate=i.get("tax_rate", 0),
                        )
                        for i in inv.get("items", [])
                    ]
                    i = Invoice(
                        id=inv["id"],
                        customer_id=inv["customer_id"],
                        items=items,
                        status=InvoiceStatus(inv.get("status", "draft")),
                    )
                    self._invoices[i.id] = i
            except Exception:
                pass

    def _save(self) -> None:
        """Save data to disk."""
        # Save customers
        customers_file = self._data_dir / "customers.json"
        customers_data = [
            {
                "id": c.id,
                "name": c.name,
                "email": c.email,
                "company": c.company,
            }
            for c in self._customers.values()
        ]
        with open(customers_file, "w") as f:
            json.dump(customers_data, f, indent=2)

        # Save invoices
        invoices_file = self._data_dir / "invoices.json"
        invoices_data = [
            {
                "id": i.id,
                "customer_id": i.customer_id,
                "items": [
                    {
                        "description": item.description,
                        "quantity": item.quantity,
                        "unit_price": item.unit_price,
                        "tax_rate": item.tax_rate,
                    }
                    for item in i.items
                ],
                "status": i.status.value,
            }
            for i in self._invoices.values()
        ]
        with open(invoices_file, "w") as f:
            json.dump(invoices_data, f, indent=2)

    def configure_stripe(self, api_key: str) -> None:
        """Configure Stripe API key."""
        self._stripe_api_key = api_key

    # Customer operations

    async def create_customer(
        self,
        name: str,
        email: str,
        company: str = "",
        billing_address: dict[str, str] | None = None,
    ) -> Customer:
        """Create a new customer."""
        customer = Customer(
            name=name,
            email=email,
            company=company,
            billing_address=billing_address or {},
        )

        self._customers[customer.id] = customer
        self._save()

        print(f"[Revenue] Created customer: {name}")
        return customer

    async def get_customer(self, customer_id: str) -> Customer | None:
        """Get a customer by ID."""
        return self._customers.get(customer_id)

    async def list_customers(self) -> list[Customer]:
        """List all customers."""
        return list(self._customers.values())

    # Invoice operations

    async def create_invoice(
        self,
        customer_id: str,
        items: list[InvoiceItem],
        due_days: int = 30,
        notes: str = "",
    ) -> Invoice | None:
        """Create an invoice for a customer."""
        customer = self._customers.get(customer_id)
        if not customer:
            print(f"[Revenue] Customer not found: {customer_id}")
            return None

        invoice = Invoice(
            customer_id=customer_id,
            items=items,
            status=InvoiceStatus.DRAFT,
            due_date=datetime.utcnow() + timedelta(days=due_days),
            notes=notes,
        )

        self._invoices[invoice.id] = invoice
        self._save()

        print(f"[Revenue] Created invoice {invoice.id}: ${invoice.total:.2f}")
        return invoice

    async def send_invoice(self, invoice_id: str) -> bool:
        """Send an invoice to the customer."""
        invoice = self._invoices.get(invoice_id)
        if not invoice:
            return False

        invoice.status = InvoiceStatus.SENT
        self._save()

        # TODO: Send email notification
        print(f"[Revenue] Sent invoice {invoice_id}")
        return True

    async def mark_paid(self, invoice_id: str) -> bool:
        """Mark an invoice as paid."""
        invoice = self._invoices.get(invoice_id)
        if not invoice:
            return False

        invoice.status = InvoiceStatus.PAID
        invoice.paid_at = datetime.utcnow()
        self._save()

        print(f"[Revenue] Invoice {invoice_id} marked as paid")
        return True

    async def get_invoice(self, invoice_id: str) -> Invoice | None:
        """Get an invoice by ID."""
        return self._invoices.get(invoice_id)

    async def list_invoices(
        self,
        customer_id: str | None = None,
        status: InvoiceStatus | None = None,
    ) -> list[Invoice]:
        """List invoices with optional filters."""
        invoices = list(self._invoices.values())

        if customer_id:
            invoices = [i for i in invoices if i.customer_id == customer_id]
        if status:
            invoices = [i for i in invoices if i.status == status]

        return invoices

    # Payment operations

    async def process_payment(
        self,
        invoice_id: str,
        method: str = "card",
    ) -> Payment | None:
        """Process a payment for an invoice."""
        invoice = self._invoices.get(invoice_id)
        if not invoice:
            return None

        payment = Payment(
            invoice_id=invoice_id,
            amount=invoice.total,
            currency=invoice.currency,
            status=PaymentStatus.PENDING,
            method=method,
        )

        # TODO: Actual Stripe payment processing
        # For now, simulate successful payment
        payment.status = PaymentStatus.COMPLETED
        payment.completed_at = datetime.utcnow()

        self._payments[payment.id] = payment
        await self.mark_paid(invoice_id)

        print(f"[Revenue] Payment processed: ${payment.amount:.2f}")
        return payment

    # Reporting

    def get_revenue_report(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> dict[str, Any]:
        """Generate a revenue report."""
        invoices = list(self._invoices.values())

        if start_date:
            invoices = [i for i in invoices if i.created_at >= start_date]
        if end_date:
            invoices = [i for i in invoices if i.created_at <= end_date]

        paid = [i for i in invoices if i.status == InvoiceStatus.PAID]
        pending = [i for i in invoices if i.status in [InvoiceStatus.SENT, InvoiceStatus.DRAFT]]
        overdue = [i for i in invoices if i.status == InvoiceStatus.OVERDUE]

        return {
            "total_invoiced": sum(i.total for i in invoices),
            "total_paid": sum(i.total for i in paid),
            "total_pending": sum(i.total for i in pending),
            "total_overdue": sum(i.total for i in overdue),
            "invoice_count": len(invoices),
            "paid_count": len(paid),
            "pending_count": len(pending),
            "overdue_count": len(overdue),
        }


# Global instance
_revenue_engine: RevenueEngine | None = None


def get_revenue_engine() -> RevenueEngine:
    """Get or create the global revenue engine."""
    global _revenue_engine
    if _revenue_engine is None:
        _revenue_engine = RevenueEngine()
    return _revenue_engine
