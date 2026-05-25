-- Enable RLS on all remaining public tables (Supabase Advisor / Stage 1 security)
-- Service role (GitHub Actions) bypasses RLS. Authenticated dashboard users get read/write below.

-- Pipeline / ingestion (no anon access; service role only)
ALTER TABLE source_categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE source_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE source_health_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE source_failures ENABLE ROW LEVEL SECURITY;
ALTER TABLE scrape_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE discovered_urls ENABLE ROW LEVEL SECURITY;
ALTER TABLE raw_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE cleaned_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE scraping_errors ENABLE ROW LEVEL SECURITY;

-- Opportunity relations
ALTER TABLE opportunity_sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE opportunity_contacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE opportunity_ai_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE opportunity_votes ENABLE ROW LEVEL SECURITY;
ALTER TABLE opportunity_duplicates ENABLE ROW LEVEL SECURITY;
ALTER TABLE opportunity_tags ENABLE ROW LEVEL SECURITY;

-- RAG / embeddings
ALTER TABLE opportunity_knowledge_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE embeddings_metadata ENABLE ROW LEVEL SECURITY;
ALTER TABLE rag_queries ENABLE ROW LEVEL SECURITY;
ALTER TABLE rag_results ENABLE ROW LEVEL SECURITY;

-- Stage 2 placeholders (locked down until Stage 2)
ALTER TABLE document_vault ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_bundles ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_bundle_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE applications ENABLE ROW LEVEL SECURITY;
ALTER TABLE application_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_drafts ENABLE ROW LEVEL SECURITY;
ALTER TABLE gmail_threads ENABLE ROW LEVEL SECURITY;
ALTER TABLE portal_application_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE follow_up_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE application_events ENABLE ROW LEVEL SECURITY;

-- System
ALTER TABLE ai_model_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_usage_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE notification_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE backup_exports ENABLE ROW LEVEL SECURITY;

-- Authenticated dashboard policies (idempotent: drop if re-run)
DO $$
DECLARE
  t text;
  tables text[] := ARRAY[
    'source_categories', 'source_runs', 'source_health_metrics', 'source_failures',
    'scrape_jobs', 'discovered_urls', 'raw_posts', 'cleaned_posts', 'scraping_errors',
    'opportunity_sources', 'opportunity_contacts', 'opportunity_ai_analysis',
    'opportunity_votes', 'opportunity_duplicates', 'opportunity_tags',
    'opportunity_knowledge_chunks', 'embeddings_metadata', 'rag_queries', 'rag_results',
    'document_vault', 'document_versions', 'document_bundles', 'document_bundle_items',
    'applications', 'application_documents', 'email_drafts', 'gmail_threads',
    'portal_application_tasks', 'follow_up_tasks', 'application_events',
    'ai_model_runs', 'api_usage_logs', 'system_settings', 'notification_logs', 'backup_exports'
  ];
BEGIN
  FOREACH t IN ARRAY tables
  LOOP
    EXECUTE format('DROP POLICY IF EXISTS authenticated_full_access_%I ON %I', t, t);
    EXECUTE format(
      'CREATE POLICY authenticated_full_access_%I ON %I FOR ALL TO authenticated USING (true) WITH CHECK (true)',
      t, t
    );
  END LOOP;
END $$;
