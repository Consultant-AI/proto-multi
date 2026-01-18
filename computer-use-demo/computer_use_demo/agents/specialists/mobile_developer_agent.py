"""
Mobile Developer Agent.

Expertise in:
- iOS/Android development
- Mobile releases
- Store compliance
- Cross-platform frameworks
- Mobile performance
- Push notifications
"""

from typing import Any

from .base_specialist import BaseSpecialist


class MobileDeveloperAgent(BaseSpecialist):
    """Mobile Developer specialist focused on iOS/Android features, releases, and store compliance."""

    def __init__(self, session_id: str | None = None, tools: list[Any] | None = None, api_key: str | None = None):
        """Initialize mobile developer agent."""
        super().__init__(
            role="mobile-developer",
            name="Mobile Developer Specialist",
            session_id=session_id,
            tools=tools,
            api_key=api_key,
        )

    def get_domain_expertise(self) -> str:
        """Get mobile developer domain expertise description."""
        return """iOS development (Swift, SwiftUI), Android development (Kotlin, Jetpack Compose),
mobile releases, App Store and Play Store compliance, cross-platform frameworks (React Native, Flutter),
mobile performance optimization, push notifications, offline capabilities, mobile security,
app signing, mobile CI/CD, deep linking, and mobile analytics integration."""
