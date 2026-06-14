"""AI classification, voting, scoring, and opportunity upsert."""

from __future__ import annotations

import hashlib
from typing import Any

import structlog

from backend.app.ai_brains.classifier_brain import ClassifierBrain
from backend.app.ai_brains.voting_engine import VotingEngine
from backend.app.config.settings import get_settings
from backend.app.db.supabase_repo import SupabaseRepo
from backend.app.ai_brains.ai_json_validator import RELEVANT_CATEGORIES
from backend.app.pipeline.opportunity_builder import build_opportunity_payload, score_to_row

logger = structlog.get_logger(__name__)


class AiRunner:
    def __init__(self, repo: SupabaseRepo, limit: int = 15) -> None:
        self._repo = repo
        self._brain = ClassifierBrain()
        self._voter = VotingEngine()
        self._limit = limit
        self._settings = get_settings()

    def run(self) -> int:
        if self._repo.cloud_calls_today() >= self._settings.ai_daily_cloud_call_limit:
            logger.warning("ai_daily_limit_reached", limit=self._settings.ai_daily_cloud_call_limit)
            self._repo.audit(
                "ai_daily_limit_reached",
                details={"limit": self._settings.ai_daily_cloud_call_limit},
            )
            return 0

        profile = self._repo.get_profile_context()
        if not profile.strip():
            logger.warning("ai_profile_empty", hint="Run scripts/seed_profile.py for better relevance scoring")
        posts = self._repo.get_cleaned_posts_for_analysis(limit=self._limit)
        processed = 0
        skipped_no_output = 0

        for post in posts:
            if self._repo.cloud_calls_today() >= self._settings.ai_daily_cloud_call_limit:
                break
            text = f"{post.get('title') or ''}\n\n{post.get('body_text') or ''}"
            result = self._brain.classify(text, profile_context=profile)
            outputs = result.get("outputs") or []
            if not outputs:
                skipped_no_output += 1
                self._repo.audit(
                    "ai_no_model_output",
                    entity_type="cleaned_posts",
                    entity_id=post.get("id"),
                    details={
                        "content_hash": post.get("content_hash"),
                        "title": post.get("title"),
                        "error": result.get("error"),
                    },
                )
                logger.warning(
                    "ai_no_model_output",
                    cleaned_post_id=post.get("id"),
                    content_hash=post.get("content_hash"),
                    error=result.get("error"),
                )
                continue

            for o in outputs:
                o["content_hash"] = post.get("content_hash")
                self._repo.log_api_usage(o.get("model_name", "ai"), units=1)

            vote = self._voter.decide(outputs)
            relevant_outputs = [
                o
                for o in outputs
                if o.get("is_relevant") is True and o.get("category") in RELEVANT_CATEGORIES
            ]
            final_cat = vote.final_category
            if final_cat in RELEVANT_CATEGORIES and not relevant_outputs:
                relevant_outputs = [o for o in outputs if o.get("category") == final_cat]
            if (
                not relevant_outputs
                or final_cat in ("rejected", "manual_review")
                or final_cat not in RELEVANT_CATEGORIES
            ):
                self._repo.audit(
                    "ai_rejected_cleaned_post",
                    entity_type="cleaned_posts",
                    entity_id=post.get("id"),
                    details={
                        "content_hash": post.get("content_hash"),
                        "models_used": [o.get("model_name") for o in outputs],
                        "reasons": [o.get("reason") for o in outputs],
                    },
                )
                processed += 1
                continue

            primary = relevant_outputs[0]
            if _looks_like_generic_listing(primary, post):
                self._repo.audit(
                    "ai_rejected_generic_listing",
                    entity_type="cleaned_posts",
                    entity_id=post.get("id"),
                    details={
                        "content_hash": post.get("content_hash"),
                        "title": primary.get("title") or post.get("title"),
                        "source_url": post.get("source_url"),
                    },
                )
                processed += 1
                continue
            opp_payload, details, breakdown = build_opportunity_payload(
                vote.final_category,
                vote.final_status,
                vote.confidence,
                primary,
                post,
                source=None,
            )
            row = self._repo.upsert_opportunity(opp_payload)
            oid = row["id"]

            self._repo.insert_evidence_rows(oid, primary.get("evidence") or [], primary.get("model_name", "ai"))
            self._repo.insert_score_row(oid, score_to_row(breakdown))
            self._repo.upsert_category_details(vote.final_category, oid, details)

            for o in outputs:
                self._repo.insert_ai_analysis(oid, post.get("id"), o)

            self._repo.insert_vote(
                oid,
                {
                    "models_used": [o.get("model_name") for o in outputs],
                    "agreement_ratio": vote.agreement_ratio,
                    "final_category": vote.final_category,
                    "final_status": vote.final_status,
                    "final_confidence": vote.confidence,
                },
            )
            processed += 1

        self._repo.audit(
            "ai_analysis_complete",
            details={"processed": processed, "skipped_no_output": skipped_no_output},
        )
        logger.info("ai_analysis_complete", processed=processed, skipped_no_output=skipped_no_output)
        return processed


def _looks_like_generic_listing(model_data: dict[str, Any], post: dict[str, Any]) -> bool:
    """Reject search/category/marketing pages that are not individual opportunities."""
    text = " ".join(
        str(x or "")
        for x in (
            model_data.get("title"),
            model_data.get("summary"),
            model_data.get("reason"),
            post.get("title"),
            post.get("source_url"),
        )
    ).lower()
    generic_markers = (
        "browse all our",
        "open job positions",
        "jobs in germany:",
        "job-board-api",
        "/jobs/data-scientist",
        "remote jobs |",
        "website erstellen",
        "eigene website erstellen",
        "website-builder",
        "kostenlose homepage",
        "how to create a website",
    )
    if any(marker in text for marker in generic_markers):
        return True
    url = str(post.get("source_url") or "").lower()
    if "/remote-jobs/o-" in url or "/api/" in url:
        return True
    return False
