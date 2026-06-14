#!/usr/bin/env python3
"""Backfill real application contacts for rows that stored boolean placeholders."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.db.supabase_repo import get_repo
from backend.app.ingestion.contact_extractor import extract_application_signals


BAD_VALUES = {"true", "false", "unknown", "unclear", "null", "none", ""}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Write updates. Default is dry-run.")
    parser.add_argument("--limit", type=int, default=500)
    args = parser.parse_args()

    repo = get_repo()
    client = repo._client
    opportunities = (
        client.table("opportunities")
        .select("id,title,category,source_url,contact_email,contact_phone,application_method,application_url,required_documents")
        .order("created_at", desc=True)
        .limit(args.limit)
        .execute()
        .data
        or []
    )

    candidates = [
        row
        for row in opportunities
        if _bad_contact(row.get("contact_email"))
        or _noise_email(row.get("contact_email"))
        or _bad_contact(row.get("contact_phone"))
        or _noise_phone(row.get("contact_phone"))
    ]
    print(f"Found {len(candidates)} opportunities with invalid contact values")

    changed = 0
    for opp in candidates:
        cleaned = _latest_cleaned_post(client, opp["id"])
        signals = extract_application_signals(cleaned.get("body_text") or "", cleaned.get("source_url") or opp.get("source_url")) if cleaned else {}
        payload = {
            "contact_email": signals.get("primary_email"),
            "contact_phone": signals.get("primary_phone"),
        }
        if signals.get("application_url") and not _displayable(opp.get("application_url")):
            payload["application_url"] = signals["application_url"]
        if signals.get("required_documents") and not opp.get("required_documents"):
            payload["required_documents"] = signals["required_documents"]
        if payload["contact_email"] and opp.get("application_method") in (None, "", "unknown", "email", True, False):
            payload["application_method"] = "email"
        elif not payload["contact_email"] and str(opp.get("application_method")).lower() == "email":
            payload["application_method"] = "unknown"

        print(f"- {opp['id']} {opp.get('title')!r}: email={payload.get('contact_email')!r} phone={payload.get('contact_phone')!r}")
        if not args.apply:
            continue

        client.table("opportunities").update(payload).eq("id", opp["id"]).execute()
        repo.replace_opportunity_contacts(opp["id"], signals.get("contacts") or [])
        _update_detail_contact(client, opp, payload, signals)
        repo.audit(
            "application_contacts_backfilled",
            entity_type="opportunities",
            entity_id=opp["id"],
            details={"email": payload.get("contact_email"), "phone": payload.get("contact_phone")},
        )
        changed += 1

    print(f"{'Updated' if args.apply else 'Would update'} {changed if args.apply else len(candidates)} opportunities")
    return 0


def _latest_cleaned_post(client, opportunity_id: str) -> dict[str, Any] | None:
    analysis = (
        client.table("opportunity_ai_analysis")
        .select("cleaned_post_id")
        .eq("opportunity_id", opportunity_id)
        .order("analyzed_at", desc=True)
        .limit(1)
        .execute()
        .data
        or []
    )
    cleaned_id = analysis[0].get("cleaned_post_id") if analysis else None
    if not cleaned_id:
        return None
    rows = (
        client.table("cleaned_posts")
        .select("id,body_text,source_url")
        .eq("id", cleaned_id)
        .limit(1)
        .execute()
        .data
        or []
    )
    return rows[0] if rows else None


def _update_detail_contact(client, opp: dict[str, Any], payload: dict[str, Any], signals: dict[str, Any]) -> None:
    table = {"phd": "phd_opportunity_details", "job": "job_opportunity_details"}.get(opp.get("category"))
    if not table:
        return
    detail_payload = {
        "application_email": payload.get("contact_email"),
        "email_application_possible": "yes" if payload.get("contact_email") else "unclear",
        "email_proof": signals.get("email_proof"),
    }
    client.table(table).update(detail_payload).eq("opportunity_id", opp["id"]).execute()


def _bad_contact(value: Any) -> bool:
    if isinstance(value, bool):
        return True
    if value is None:
        return False
    text = str(value).strip().lower()
    return text in BAD_VALUES


def _noise_email(value: Any) -> bool:
    if not _displayable(value):
        return False
    text = str(value).strip().lower()
    local, _, domain = text.partition("@")
    return (
        "@" not in text
        or domain in {"example.com", "example.edu", "ihre-domain.de"}
        or local in {"example", "email", "your.email", "name"}
        or local.startswith("user")
    )


def _noise_phone(value: Any) -> bool:
    if not _displayable(value):
        return False
    text = str(value).strip()
    digits = "".join(ch for ch in text if ch.isdigit())
    if len(digits) < 8:
        return True
    if digits in {"0123456789", "123456789", "12345678910"}:
        return True
    if "." in text and text.count(".") >= 2:
        return True
    if "-" in text and not text.startswith("+"):
        return True
    return False


def _displayable(value: Any) -> bool:
    if value is None or isinstance(value, bool):
        return False
    return str(value).strip().lower() not in BAD_VALUES


if __name__ == "__main__":
    raise SystemExit(main())
