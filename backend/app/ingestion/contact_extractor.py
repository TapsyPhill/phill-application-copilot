"""Deterministic extraction of application contact signals from cleaned text."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import urljoin


EMAIL_RE = re.compile(r"(?<![\w.+-])([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})(?![\w.-])", re.I)
MAILTO_RE = re.compile(r"mailto:([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})", re.I)
PHONE_RE = re.compile(r"(?<!\d)(\+?\d[\d\s()./-]{7,}\d)(?!\d)")
URL_RE = re.compile(r"https?://[^\s)>\"]+", re.I)

APPLICATION_WORDS = (
    "apply",
    "application",
    "send your application",
    "submit your application",
    "bewerbung",
    "bewerben",
    "doctoral",
    "phd",
    "position",
    "vacancy",
)
DOCUMENT_WORDS = {
    "cv": "CV",
    "curriculum vitae": "CV",
    "cover letter": "cover letter",
    "motivation letter": "motivation letter",
    "transcript": "transcript",
    "references": "references",
    "recommendation": "recommendation letter",
    "research proposal": "research proposal",
    "publication": "publication list",
    "portfolio": "portfolio",
}


@dataclass(frozen=True)
class ContactSignal:
    contact_type: str
    contact_value: str
    proof_snippet: str
    confidence: float = 85.0


def extract_application_signals(text: str, source_url: str | None = None) -> dict[str, Any]:
    """Return contact, application URL, instruction, and document hints from text.

    This is intentionally conservative: it only extracts values present in the
    source text and keeps snippets for proof.
    """
    body = text or ""
    contacts: list[ContactSignal] = []
    seen: set[tuple[str, str]] = set()

    for match in list(MAILTO_RE.finditer(body)) + list(EMAIL_RE.finditer(body)):
        email = match.group(1).strip().rstrip(".,;:")
        key = ("email", email.lower())
        if key in seen or _looks_like_noise_email(email):
            continue
        seen.add(key)
        contacts.append(ContactSignal("email", email, _snippet_around(body, match.start(), match.end()), 92.0))

    for match in PHONE_RE.finditer(body):
        phone = re.sub(r"\s+", " ", match.group(1)).strip()
        if _looks_like_date_or_id(phone):
            continue
        key = ("phone", phone)
        if key in seen:
            continue
        seen.add(key)
        contacts.append(ContactSignal("phone", phone, _snippet_around(body, match.start(), match.end()), 72.0))

    application_url = _application_url(body, source_url)
    required_documents = _required_documents(body)
    application_instructions = _application_instructions(body)

    return {
        "contacts": [c.__dict__ for c in contacts[:5]],
        "primary_email": _first_contact(contacts, "email"),
        "primary_phone": _first_contact(contacts, "phone"),
        "email_proof": _first_proof(contacts, "email"),
        "phone_proof": _first_proof(contacts, "phone"),
        "application_url": application_url,
        "required_documents": required_documents,
        "application_instructions": application_instructions,
    }


def _first_contact(contacts: list[ContactSignal], contact_type: str) -> str | None:
    for contact in contacts:
        if contact.contact_type == contact_type:
            return contact.contact_value
    return None


def _first_proof(contacts: list[ContactSignal], contact_type: str) -> str | None:
    for contact in contacts:
        if contact.contact_type == contact_type:
            return contact.proof_snippet
    return None


def _snippet_around(text: str, start: int, end: int, radius: int = 180) -> str:
    left = max(0, start - radius)
    right = min(len(text), end + radius)
    return re.sub(r"\s+", " ", text[left:right]).strip()


def _looks_like_noise_email(email: str) -> bool:
    local, _, domain = email.lower().partition("@")
    return (
        not local
        or not domain
        or domain.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp"))
        or local in {"example", "email", "your.email", "name"}
    )


def _looks_like_date_or_id(value: str) -> bool:
    digits = re.sub(r"\D", "", value)
    return len(digits) < 8 or bool(re.fullmatch(r"20\d{6,}", digits))


def _application_url(text: str, source_url: str | None) -> str | None:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in lines:
        lower = line.lower()
        if not any(word in lower for word in APPLICATION_WORDS):
            continue
        match = URL_RE.search(line)
        if match:
            return match.group(0).rstrip(".,;")
        if "href=" in lower:
            href = re.search(r"href=[\"']([^\"']+)[\"']", line, re.I)
            if href and source_url:
                return urljoin(source_url, href.group(1))
    return None


def _required_documents(text: str) -> list[str]:
    lower = text.lower()
    docs = []
    for needle, label in DOCUMENT_WORDS.items():
        if needle in lower:
            docs.append(label)
    return sorted(set(docs))


def _application_instructions(text: str) -> str | None:
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines() if line.strip()]
    for line in lines:
        lower = line.lower()
        if any(word in lower for word in ("send your application", "submit your application", "apply by", "please apply", "bewerbung")):
            return line[:1000]
    return None
