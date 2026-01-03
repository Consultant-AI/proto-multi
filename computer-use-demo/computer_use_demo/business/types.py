"""
Type definitions for Business Engines.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
import uuid


# ============== Revenue Types ==============

class InvoiceStatus(str, Enum):
    """Status of an invoice."""
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentStatus(str, Enum):
    """Status of a payment."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


@dataclass
class Customer:
    """A customer/account."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    email: str = ""
    company: str = ""
    stripe_customer_id: str | None = None
    billing_address: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class InvoiceItem:
    """A line item on an invoice."""
    description: str
    quantity: int = 1
    unit_price: float = 0.0
    tax_rate: float = 0.0

    @property
    def subtotal(self) -> float:
        return self.quantity * self.unit_price

    @property
    def tax(self) -> float:
        return self.subtotal * self.tax_rate

    @property
    def total(self) -> float:
        return self.subtotal + self.tax


@dataclass
class Invoice:
    """An invoice."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str = ""
    items: list[InvoiceItem] = field(default_factory=list)
    status: InvoiceStatus = InvoiceStatus.DRAFT
    currency: str = "USD"
    due_date: datetime | None = None
    paid_at: datetime | None = None
    notes: str = ""
    stripe_invoice_id: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def subtotal(self) -> float:
        return sum(item.subtotal for item in self.items)

    @property
    def tax(self) -> float:
        return sum(item.tax for item in self.items)

    @property
    def total(self) -> float:
        return sum(item.total for item in self.items)


@dataclass
class Payment:
    """A payment."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    invoice_id: str = ""
    amount: float = 0.0
    currency: str = "USD"
    status: PaymentStatus = PaymentStatus.PENDING
    method: str = ""  # card, bank_transfer, etc.
    stripe_payment_id: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None


# ============== Relationship/CRM Types ==============

class LeadStatus(str, Enum):
    """Status of a lead."""
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


@dataclass
class Contact:
    """A contact/person."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    phone: str = ""
    company_id: str | None = None
    title: str = ""
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


@dataclass
class Company:
    """A company/organization."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    domain: str = ""
    industry: str = ""
    size: str = ""  # startup, small, medium, enterprise
    website: str = ""
    address: dict[str, str] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Interaction:
    """A recorded interaction with a contact."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    contact_id: str = ""
    type: str = ""  # email, call, meeting, note
    subject: str = ""
    content: str = ""
    outcome: str = ""
    created_by: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Lead:
    """A sales lead."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    contact_id: str = ""
    company_id: str | None = None
    status: LeadStatus = LeadStatus.NEW
    source: str = ""  # website, referral, campaign
    value: float = 0.0
    probability: float = 0.0  # 0-1
    assigned_to: str = ""
    notes: str = ""
    expected_close: datetime | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


# ============== Growth/Marketing Types ==============

class CampaignStatus(str, Enum):
    """Status of a campaign."""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class Campaign:
    """A marketing campaign."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    type: str = ""  # email, social, content, ads
    status: CampaignStatus = CampaignStatus.DRAFT
    budget: float = 0.0
    spent: float = 0.0
    target_audience: dict[str, Any] = field(default_factory=dict)
    start_date: datetime | None = None
    end_date: datetime | None = None
    metrics: dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


# ============== Compliance Types ==============

class ComplianceStatus(str, Enum):
    """Status of compliance."""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    REVIEW_NEEDED = "review_needed"
    EXEMPT = "exempt"


@dataclass
class ComplianceRule:
    """A compliance rule."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    category: str = ""  # gdpr, soc2, hipaa, pci
    severity: str = "warning"  # info, warning, error
    check_function: str = ""  # Function name or code to run
    remediation: str = ""
    enabled: bool = True


@dataclass
class ComplianceCheck:
    """Result of a compliance check."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    rule_id: str = ""
    status: ComplianceStatus = ComplianceStatus.REVIEW_NEEDED
    details: str = ""
    evidence: list[str] = field(default_factory=list)
    checked_at: datetime = field(default_factory=datetime.utcnow)
    checked_by: str = ""
