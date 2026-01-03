"""
Proto Business Engines Module.

Provides business automation capabilities.

Components:
- Revenue: Stripe integration, invoicing, payments
- Growth: Marketing automation, analytics
- Relationships: CRM, stakeholder tracking
- Compliance: Regulatory compliance engine

Usage:
    from computer_use_demo.business import (
        RevenueEngine,
        GrowthEngine,
        RelationshipEngine,
        ComplianceEngine,
    )

    # Revenue operations
    revenue = RevenueEngine()
    await revenue.create_invoice(customer_id, items)

    # CRM operations
    crm = RelationshipEngine()
    await crm.add_contact(contact_info)
"""

from .types import (
    Customer,
    Invoice,
    InvoiceItem,
    InvoiceStatus,
    Payment,
    PaymentStatus,
    Contact,
    Company,
    Interaction,
    Lead,
    LeadStatus,
    Campaign,
    CampaignStatus,
    ComplianceRule,
    ComplianceCheck,
    ComplianceStatus,
)

from .revenue import (
    RevenueEngine,
    get_revenue_engine,
)

from .growth import (
    GrowthEngine,
    get_growth_engine,
)

from .relationships import (
    RelationshipEngine,
    get_relationship_engine,
)

from .compliance import (
    ComplianceEngine,
    get_compliance_engine,
)

__all__ = [
    # Types
    "Customer",
    "Invoice",
    "InvoiceItem",
    "InvoiceStatus",
    "Payment",
    "PaymentStatus",
    "Contact",
    "Company",
    "Interaction",
    "Lead",
    "LeadStatus",
    "Campaign",
    "CampaignStatus",
    "ComplianceRule",
    "ComplianceCheck",
    "ComplianceStatus",
    # Engines
    "RevenueEngine",
    "GrowthEngine",
    "RelationshipEngine",
    "ComplianceEngine",
    "get_revenue_engine",
    "get_growth_engine",
    "get_relationship_engine",
    "get_compliance_engine",
]
