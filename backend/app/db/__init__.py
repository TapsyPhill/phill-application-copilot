"""Supabase data access layer."""

from backend.app.db.supabase_repo import SupabaseRepo, get_repo

__all__ = ["SupabaseRepo", "get_repo"]
