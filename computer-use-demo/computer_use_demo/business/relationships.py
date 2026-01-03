"""
Relationship Engine (CRM).

Manages contacts, companies, and sales pipeline.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .types import (
    Contact,
    Company,
    Interaction,
    Lead,
    LeadStatus,
)


class RelationshipEngine:
    """
    CRM and relationship management engine.

    Features:
    - Contact management
    - Company tracking
    - Interaction logging
    - Sales pipeline
    """

    def __init__(self, data_dir: Path | None = None):
        self._data_dir = data_dir or Path.home() / ".proto" / "company" / "business" / "crm"
        self._data_dir.mkdir(parents=True, exist_ok=True)

        self._contacts: dict[str, Contact] = {}
        self._companies: dict[str, Company] = {}
        self._interactions: dict[str, Interaction] = {}
        self._leads: dict[str, Lead] = {}

        self._load()

    def _load(self) -> None:
        """Load data from disk."""
        for data_type, storage in [
            ("contacts", self._contacts),
            ("companies", self._companies),
            ("leads", self._leads),
        ]:
            data_file = self._data_dir / f"{data_type}.json"
            if data_file.exists():
                try:
                    with open(data_file, "r") as f:
                        data = json.load(f)
                    # Basic loading - would need proper deserialization
                except Exception:
                    pass

    def _save(self) -> None:
        """Save data to disk."""
        # Save contacts
        contacts_file = self._data_dir / "contacts.json"
        with open(contacts_file, "w") as f:
            json.dump(
                [{"id": c.id, "first_name": c.first_name, "last_name": c.last_name, "email": c.email}
                 for c in self._contacts.values()],
                f, indent=2
            )

        # Save companies
        companies_file = self._data_dir / "companies.json"
        with open(companies_file, "w") as f:
            json.dump(
                [{"id": c.id, "name": c.name, "domain": c.domain}
                 for c in self._companies.values()],
                f, indent=2
            )

        # Save leads
        leads_file = self._data_dir / "leads.json"
        with open(leads_file, "w") as f:
            json.dump(
                [{"id": l.id, "contact_id": l.contact_id, "status": l.status.value, "value": l.value}
                 for l in self._leads.values()],
                f, indent=2
            )

    # Contact operations

    async def add_contact(
        self,
        first_name: str,
        last_name: str,
        email: str,
        phone: str = "",
        company_id: str | None = None,
        title: str = "",
        tags: list[str] | None = None,
    ) -> Contact:
        """Add a new contact."""
        contact = Contact(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            company_id=company_id,
            title=title,
            tags=tags or [],
        )

        self._contacts[contact.id] = contact
        self._save()

        print(f"[CRM] Added contact: {contact.full_name}")
        return contact

    async def get_contact(self, contact_id: str) -> Contact | None:
        """Get a contact by ID."""
        return self._contacts.get(contact_id)

    async def find_contacts(
        self,
        query: str | None = None,
        company_id: str | None = None,
        tags: list[str] | None = None,
    ) -> list[Contact]:
        """Find contacts matching criteria."""
        contacts = list(self._contacts.values())

        if query:
            query_lower = query.lower()
            contacts = [
                c for c in contacts
                if query_lower in c.full_name.lower() or query_lower in c.email.lower()
            ]

        if company_id:
            contacts = [c for c in contacts if c.company_id == company_id]

        if tags:
            contacts = [c for c in contacts if any(t in c.tags for t in tags)]

        return contacts

    async def update_contact(self, contact_id: str, **updates) -> Contact | None:
        """Update a contact."""
        contact = self._contacts.get(contact_id)
        if not contact:
            return None

        for key, value in updates.items():
            if hasattr(contact, key):
                setattr(contact, key, value)

        self._save()
        return contact

    # Company operations

    async def add_company(
        self,
        name: str,
        domain: str = "",
        industry: str = "",
        size: str = "",
        website: str = "",
    ) -> Company:
        """Add a new company."""
        company = Company(
            name=name,
            domain=domain,
            industry=industry,
            size=size,
            website=website,
        )

        self._companies[company.id] = company
        self._save()

        print(f"[CRM] Added company: {name}")
        return company

    async def get_company(self, company_id: str) -> Company | None:
        """Get a company by ID."""
        return self._companies.get(company_id)

    async def find_companies(
        self,
        query: str | None = None,
        industry: str | None = None,
    ) -> list[Company]:
        """Find companies matching criteria."""
        companies = list(self._companies.values())

        if query:
            query_lower = query.lower()
            companies = [
                c for c in companies
                if query_lower in c.name.lower() or query_lower in c.domain.lower()
            ]

        if industry:
            companies = [c for c in companies if c.industry == industry]

        return companies

    # Interaction logging

    async def log_interaction(
        self,
        contact_id: str,
        interaction_type: str,
        subject: str,
        content: str = "",
        outcome: str = "",
        created_by: str = "",
    ) -> Interaction:
        """Log an interaction with a contact."""
        interaction = Interaction(
            contact_id=contact_id,
            type=interaction_type,
            subject=subject,
            content=content,
            outcome=outcome,
            created_by=created_by,
        )

        self._interactions[interaction.id] = interaction
        print(f"[CRM] Logged {interaction_type}: {subject}")
        return interaction

    async def get_contact_interactions(self, contact_id: str) -> list[Interaction]:
        """Get all interactions for a contact."""
        return [
            i for i in self._interactions.values()
            if i.contact_id == contact_id
        ]

    # Lead/pipeline operations

    async def create_lead(
        self,
        contact_id: str,
        source: str,
        value: float = 0.0,
        assigned_to: str = "",
        company_id: str | None = None,
    ) -> Lead:
        """Create a new lead."""
        lead = Lead(
            contact_id=contact_id,
            company_id=company_id,
            source=source,
            value=value,
            assigned_to=assigned_to,
        )

        self._leads[lead.id] = lead
        self._save()

        print(f"[CRM] Created lead: ${value:.2f} from {source}")
        return lead

    async def update_lead_status(
        self,
        lead_id: str,
        status: LeadStatus,
        notes: str = "",
    ) -> Lead | None:
        """Update lead status."""
        lead = self._leads.get(lead_id)
        if not lead:
            return None

        lead.status = status
        lead.updated_at = datetime.utcnow()
        if notes:
            lead.notes = notes

        self._save()

        print(f"[CRM] Lead {lead_id} -> {status.value}")
        return lead

    async def get_pipeline(
        self,
        assigned_to: str | None = None,
    ) -> dict[str, list[Lead]]:
        """Get leads grouped by status."""
        leads = list(self._leads.values())

        if assigned_to:
            leads = [l for l in leads if l.assigned_to == assigned_to]

        pipeline = {}
        for status in LeadStatus:
            pipeline[status.value] = [l for l in leads if l.status == status]

        return pipeline

    def get_pipeline_value(self) -> dict[str, float]:
        """Get total value at each pipeline stage."""
        pipeline = {}
        for status in LeadStatus:
            leads = [l for l in self._leads.values() if l.status == status]
            pipeline[status.value] = sum(l.value for l in leads)
        return pipeline


# Global instance
_relationship_engine: RelationshipEngine | None = None


def get_relationship_engine() -> RelationshipEngine:
    """Get or create the global relationship engine."""
    global _relationship_engine
    if _relationship_engine is None:
        _relationship_engine = RelationshipEngine()
    return _relationship_engine
