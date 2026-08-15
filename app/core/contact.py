from __future__ import annotations

from app.core.config import CONFIG


def contact_links() -> dict[str, str]:
    """Resolve the developer contact links (LinkedIn, GitHub, Email)."""
    return {
        "linkedin": CONFIG.linkedin_url,
        "github": CONFIG.github_url,
        "email": (
            "https://mail.google.com/mail/?view=cm&fs=1"
            f"&to={CONFIG.email_address}&su={CONFIG.name}"
        ),
    }