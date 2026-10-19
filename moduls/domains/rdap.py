"""Shared domain-status logic.

Single source of truth for the Verisign RDAP lookup and for classifying a raw
status string into ``available`` / ``registered`` / ``unknown``. Historically
this was copy-pasted across ``moduls.cities``, ``moduls.analyzer``,
``moduls.niches``, ``moduls.domains`` and ``moduls.maintenance``; keeping it
here avoids the inconsistencies that duplication caused.
"""

import requests

RDAP_URL_TEMPLATE = "https://rdap.verisign.com/com/v1/domain/{domain}"

AVAILABLE = "available"
REGISTERED = "registered"
UNKNOWN = "unknown"


def check_domain_rdap(domain: str) -> str:
    """Query Verisign RDAP for ``domain`` and return a human-readable status."""
    url = RDAP_URL_TEMPLATE.format(domain=domain)
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return "❌ Registered"
        elif response.status_code == 404:
            return "✅ Available"
        else:
            return f"⚠️ Unknown ({response.status_code})"
    except Exception:
        return "⚠️ Error"


def classify_status(status: str) -> str:
    """Return ``available``, ``registered`` or ``unknown`` for a status string.

    ``registered`` wins when a string somehow contains both words, matching the
    historical behaviour of every counting site except one.
    """
    text = (status or "").lower()
    if "registered" in text:
        return REGISTERED
    if "available" in text:
        return AVAILABLE
    return UNKNOWN


def is_available(status: str) -> bool:
    return classify_status(status) == AVAILABLE


def is_registered(status: str) -> bool:
    return classify_status(status) == REGISTERED


def is_resolved(status: str) -> bool:
    """True when the check gave a definite answer (available or registered)."""
    return classify_status(status) != UNKNOWN
