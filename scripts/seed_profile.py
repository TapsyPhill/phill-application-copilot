#!/usr/bin/env python3
"""Seed Tapuwa Phill Mhembere profile for Stage 1 RAG and scoring."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.db.supabase_repo import SupabaseRepo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROFILE = {
    "display_name": "Tapuwa Phill Mhembere",
    "legal_name": "Tapuwa Phill Mhembere",
    "headline": "Data Scientist · Actuarial Data Analyst · LLM / Full-Stack AI Developer",
    "location_country": "Germany",
    "location_city": "Bremen",
    "summary": (
        "Data Scientist and LLM Engineer with actuarial analytics background. "
        "Builds Python/FastAPI data pipelines, RAG systems, dashboards, and small-business "
        "digital solutions across Germany, global remote, and South Africa."
    ),
    "languages": [
        {"language": "English", "level": "fluent"},
        {"language": "German", "level": "working"},
    ],
}

SKILLS = [
    ("Python", "core", "expert"),
    ("SQL / PostgreSQL", "core", "expert"),
    ("FastAPI", "core", "advanced"),
    ("LLM systems", "ai", "expert"),
    ("RAG / vector search", "ai", "expert"),
    ("Machine learning", "ai", "advanced"),
    ("Data pipelines", "data", "advanced"),
    ("Analytics engineering", "data", "advanced"),
    ("Power BI", "bi", "advanced"),
    ("Tableau", "bi", "intermediate"),
    ("Actuarial / risk modeling", "finance", "advanced"),
    ("API integration", "integration", "advanced"),
    ("WordPress / web", "client_services", "advanced"),
    ("Business digitization", "client_services", "advanced"),
]

EXPERIENCE = [
    {
        "company": "Freelance / Client Projects",
        "role_title": "LLM Engineer & Full-Stack AI Developer",
        "is_current": True,
        "description": "RAG apps, FastAPI backends, automation, dashboards, AI integration for SMEs.",
    },
    {
        "company": "Data & Analytics Roles",
        "role_title": "Data Scientist / Actuarial Data Analyst",
        "is_current": False,
        "description": "Predictive modeling, risk analytics, reporting, SQL pipelines.",
    },
]

EDUCATION = [
    {
        "institution": "MSc Data Science",
        "degree": "MSc",
        "field": "Data Science",
        "notes": "Completed",
    },
    {
        "institution": "BSc Computer Science / Actuarial Science",
        "degree": "BSc",
        "field": "Computer Science / Actuarial Science",
        "notes": "Completed",
    },
]

PREFERENCES = [
    ("job_markets", ["Germany", "EU", "remote"]),
    ("client_lead_regions", ["Germany", "South Africa", "global"]),
    ("phd_funding", ["fully_funded", "salaried_phd", "scholarship_available"]),
    ("remote_preference", ["worldwide_remote", "eu_remote", "south_africa_friendly"]),
    ("deprioritize", ["us_only_remote", "self_funded_phd", "native_german_required"]),
    ("ielts", {"type": "Academic", "overall": 6.5, "level": "B2"}),
]

CHUNKS = [
    (
        "core_identity",
        "Tapuwa Phill Mhembere — Data Scientist, Actuarial Data Analyst, LLM Engineer",
        "Python, SQL, FastAPI, LLM/RAG, data pipelines, actuarial modeling, Power BI, dashboards.",
    ),
    (
        "client_services",
        "Client lead services",
        "Web/app development, AI integration, automation, Excel, booking systems, Google Maps/API, "
        "digitization, workflow tools, technical help for small businesses and nonprofits.",
    ),
    (
        "phd_interests",
        "PhD interests",
        "Funded doctoral roles in data science, ML, NLP, RAG, computational statistics, explainable AI.",
    ),
]


def main() -> int:
    repo = SupabaseRepo.from_settings()
    client = repo._client

    existing = client.table("user_profiles").select("id").limit(1).execute().data
    if existing:
        pid = existing[0]["id"]
        client.table("user_profiles").update(PROFILE).eq("id", pid).execute()
        logger.info("profile_updated", extra={"id": pid})
    else:
        r = client.table("user_profiles").insert(PROFILE).execute()
        pid = r.data[0]["id"]
        logger.info("profile_created", extra={"id": pid})

    client.table("profile_skills").delete().eq("profile_id", pid).execute()
    for skill_name, cat, prof in SKILLS:
        client.table("profile_skills").insert(
            {
                "profile_id": pid,
                "skill_name": skill_name,
                "skill_category": cat,
                "proficiency": prof,
            }
        ).execute()

    client.table("profile_experience").delete().eq("profile_id", pid).execute()
    for exp in EXPERIENCE:
        client.table("profile_experience").insert({**exp, "profile_id": pid}).execute()

    client.table("profile_education").delete().eq("profile_id", pid).execute()
    for edu in EDUCATION:
        client.table("profile_education").insert({**edu, "profile_id": pid}).execute()

    for key, val in PREFERENCES:
        client.table("profile_preferences").upsert(
            {"profile_id": pid, "preference_key": key, "preference_value": val},
            on_conflict="profile_id,preference_key",
        ).execute()

    client.table("profile_knowledge_chunks").delete().eq("profile_id", pid).execute()
    for ctype, title, content in CHUNKS:
        client.table("profile_knowledge_chunks").insert(
            {"profile_id": pid, "chunk_type": ctype, "title": title, "content": content}
        ).execute()

    client.table("profile_documents").delete().eq("profile_id", pid).eq("doc_type", "cv").execute()
    client.table("profile_documents").insert(
        {
            "profile_id": pid,
            "doc_type": "cv",
            "title": "Tapuwa Phill Mhembere CV (seed)",
            "content_text": PROFILE["summary"] + " " + " ".join(c[2] for c in CHUNKS),
        }
    ).execute()

    repo.audit("profile_seeded", entity_type="user_profiles", entity_id=pid)
    logger.info("profile_seed_complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
