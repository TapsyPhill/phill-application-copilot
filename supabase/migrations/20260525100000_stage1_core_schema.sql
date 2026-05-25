-- Stage 1: Opportunity Command Center core schema
-- Apply via Supabase SQL editor or CLI. UUID PKs, timestamps, RLS-ready.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

-- =============================================================================
-- TABLE GROUP 1: PROFILE
-- =============================================================================

CREATE TABLE user_profiles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  display_name TEXT NOT NULL,
  legal_name TEXT,
  headline TEXT,
  location_country TEXT DEFAULT 'Germany',
  location_city TEXT DEFAULT 'Bremen',
  summary TEXT,
  languages JSONB DEFAULT '[]'::jsonb,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE profile_skills (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  profile_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
  skill_name TEXT NOT NULL,
  skill_category TEXT,
  proficiency TEXT,
  priority_weight NUMERIC(4,2) DEFAULT 1.0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE profile_experience (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  profile_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
  company TEXT NOT NULL,
  role_title TEXT NOT NULL,
  start_date DATE,
  end_date DATE,
  is_current BOOLEAN DEFAULT false,
  description TEXT,
  highlights JSONB DEFAULT '[]'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE profile_education (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  profile_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
  institution TEXT NOT NULL,
  degree TEXT,
  field TEXT,
  start_year INT,
  end_year INT,
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE profile_preferences (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  profile_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
  preference_key TEXT NOT NULL,
  preference_value JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (profile_id, preference_key)
);

CREATE TABLE profile_documents (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  profile_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
  doc_type TEXT NOT NULL,
  title TEXT NOT NULL,
  storage_path TEXT,
  content_text TEXT,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE profile_knowledge_chunks (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  profile_id UUID NOT NULL REFERENCES user_profiles(id) ON DELETE CASCADE,
  chunk_type TEXT NOT NULL,
  title TEXT,
  content TEXT NOT NULL,
  embedding vector(384),
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =============================================================================
-- TABLE GROUP 2: SOURCES
-- =============================================================================

CREATE TABLE source_categories (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL UNIQUE,
  description TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE sources (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  external_id TEXT UNIQUE,
  source_name TEXT NOT NULL,
  url TEXT NOT NULL,
  base_domain TEXT NOT NULL,
  source_group TEXT,
  country TEXT,
  region TEXT,
  city TEXT,
  language TEXT DEFAULT 'de',
  category TEXT,
  source_type TEXT NOT NULL DEFAULT 'unknown',
  target_section TEXT NOT NULL,
  scraping_method_preference TEXT NOT NULL DEFAULT 'requests_bs4',
  priority INT DEFAULT 5,
  enabled BOOLEAN DEFAULT true,
  requires_js BOOLEAN DEFAULT false,
  requires_login BOOLEAN DEFAULT false,
  allows_search BOOLEAN DEFAULT false,
  search_url_pattern TEXT,
  notes TEXT,
  search_terms JSONB DEFAULT '[]'::jsonb,
  health_score NUMERIC(5,2) DEFAULT 50,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE source_search_terms (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  source_id UUID REFERENCES sources(id) ON DELETE CASCADE,
  term TEXT NOT NULL,
  language TEXT,
  target_section TEXT,
  enabled BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE source_runs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
  run_type TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'started',
  urls_discovered INT DEFAULT 0,
  posts_scraped INT DEFAULT 0,
  errors_count INT DEFAULT 0,
  started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  finished_at TIMESTAMPTZ,
  metadata JSONB DEFAULT '{}'::jsonb
);

CREATE TABLE source_health_metrics (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
  metric_date DATE NOT NULL DEFAULT CURRENT_DATE,
  success_rate NUMERIC(5,2),
  avg_quality_score NUMERIC(5,2),
  opportunities_created INT DEFAULT 0,
  garbage_rate NUMERIC(5,2),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (source_id, metric_date)
);

CREATE TABLE source_failures (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  source_id UUID REFERENCES sources(id) ON DELETE SET NULL,
  url TEXT,
  error_type TEXT,
  error_message TEXT,
  scraper_used TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =============================================================================
-- TABLE GROUP 3: SCRAPING
-- =============================================================================

CREATE TABLE scrape_jobs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  job_type TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'queued',
  source_id UUID REFERENCES sources(id) ON DELETE SET NULL,
  payload JSONB DEFAULT '{}'::jsonb,
  started_at TIMESTAMPTZ,
  finished_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE discovered_urls (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  source_id UUID REFERENCES sources(id) ON DELETE SET NULL,
  url TEXT NOT NULL,
  url_hash TEXT NOT NULL,
  discovery_method TEXT NOT NULL,
  search_term TEXT,
  status TEXT DEFAULT 'pending',
  first_seen_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  last_seen_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  metadata JSONB DEFAULT '{}'::jsonb,
  UNIQUE (url_hash)
);

CREATE TABLE raw_posts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  source_id UUID REFERENCES sources(id) ON DELETE SET NULL,
  discovered_url_id UUID REFERENCES discovered_urls(id) ON DELETE SET NULL,
  source_url TEXT NOT NULL,
  url_hash TEXT NOT NULL,
  scraper_used TEXT,
  raw_html TEXT,
  raw_text TEXT,
  raw_markdown TEXT,
  metadata JSONB DEFAULT '{}'::jsonb,
  scraped_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE cleaned_posts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  raw_post_id UUID NOT NULL REFERENCES raw_posts(id) ON DELETE CASCADE,
  source_url TEXT NOT NULL,
  url_hash TEXT NOT NULL,
  content_hash TEXT NOT NULL,
  title TEXT,
  body_text TEXT NOT NULL,
  language TEXT,
  quality_score NUMERIC(5,2),
  quality_status TEXT DEFAULT 'passed',
  rejection_reason TEXT,
  metadata JSONB DEFAULT '{}'::jsonb,
  cleaned_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE scraping_errors (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  scrape_job_id UUID REFERENCES scrape_jobs(id) ON DELETE SET NULL,
  source_id UUID REFERENCES sources(id) ON DELETE SET NULL,
  url TEXT,
  error_type TEXT,
  error_message TEXT,
  stack_trace TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =============================================================================
-- TABLE GROUP 4: OPPORTUNITIES (core)
-- =============================================================================

CREATE TABLE opportunities (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  title TEXT NOT NULL,
  summary TEXT,
  category TEXT NOT NULL,
  subcategory TEXT,
  country TEXT,
  city TEXT,
  organization TEXT,
  source_url TEXT NOT NULL,
  canonical_url TEXT,
  original_url TEXT,
  application_method TEXT DEFAULT 'unknown',
  contact_method TEXT DEFAULT 'unknown',
  contact_email TEXT,
  contact_phone TEXT,
  contact_url TEXT,
  posted_date DATE,
  deadline DATE,
  viewed BOOLEAN NOT NULL DEFAULT false,
  viewed_at TIMESTAMPTZ,
  last_opened_at TIMESTAMPTZ,
  open_count INT DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'new',
  priority TEXT DEFAULT 'normal',
  final_score NUMERIC(5,2) DEFAULT 0,
  confidence_score NUMERIC(5,2) DEFAULT 0,
  first_seen_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  last_seen_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  times_seen INT DEFAULT 1,
  url_hash TEXT NOT NULL,
  content_hash TEXT,
  semantic_hash TEXT,
  language TEXT,
  approved_for_application BOOLEAN DEFAULT false,
  stage2_ready BOOLEAN DEFAULT false,
  recommended_document_bundle UUID,
  required_documents JSONB DEFAULT '[]'::jsonb,
  application_url TEXT,
  application_status TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (url_hash)
);

CREATE TABLE opportunity_sources (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  opportunity_id UUID NOT NULL REFERENCES opportunities(id) ON DELETE CASCADE,
  source_id UUID REFERENCES sources(id) ON DELETE SET NULL,
  source_url TEXT NOT NULL,
  discovered_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  scraper_used TEXT,
  is_primary BOOLEAN DEFAULT false
);

CREATE TABLE opportunity_contacts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  opportunity_id UUID NOT NULL REFERENCES opportunities(id) ON DELETE CASCADE,
  contact_type TEXT NOT NULL,
  contact_value TEXT NOT NULL,
  proof_snippet TEXT,
  confidence NUMERIC(5,2),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE opportunity_evidence (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  opportunity_id UUID NOT NULL REFERENCES opportunities(id) ON DELETE CASCADE,
  evidence_type TEXT NOT NULL,
  snippet TEXT NOT NULL,
  source_offset INT,
  model_name TEXT,
  confidence NUMERIC(5,2),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE opportunity_scores (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  opportunity_id UUID NOT NULL REFERENCES opportunities(id) ON DELETE CASCADE,
  profile_match_score NUMERIC(5,2),
  recency_score NUMERIC(5,2),
  evidence_score NUMERIC(5,2),
  contact_score NUMERIC(5,2),
  application_method_score NUMERIC(5,2),
  country_score NUMERIC(5,2),
  source_reliability_score NUMERIC(5,2),
  duplicate_penalty NUMERIC(5,2) DEFAULT 0,
  urgency_score NUMERIC(5,2),
  final_score NUMERIC(5,2),
  scoring_version TEXT DEFAULT 'stage1_v1',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE opportunity_ai_analysis (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  opportunity_id UUID NOT NULL REFERENCES opportunities(id) ON DELETE CASCADE,
  cleaned_post_id UUID REFERENCES cleaned_posts(id) ON DELETE SET NULL,
  model_name TEXT NOT NULL,
  is_relevant BOOLEAN,
  category TEXT,
  subcategory TEXT,
  fit_score NUMERIC(5,2),
  confidence NUMERIC(5,2),
  reason TEXT,
  raw_json JSONB NOT NULL,
  content_hash TEXT,
  analyzed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE opportunity_votes (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  opportunity_id UUID NOT NULL REFERENCES opportunities(id) ON DELETE CASCADE,
  vote_round TEXT NOT NULL,
  models_used JSONB NOT NULL,
  agreement_ratio NUMERIC(4,2),
  final_category TEXT,
  final_status TEXT,
  final_confidence NUMERIC(5,2),
  decision_json JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE opportunity_status_history (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  opportunity_id UUID NOT NULL REFERENCES opportunities(id) ON DELETE CASCADE,
  old_status TEXT,
  new_status TEXT NOT NULL,
  changed_by TEXT DEFAULT 'system',
  reason TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE opportunity_user_actions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  opportunity_id UUID NOT NULL REFERENCES opportunities(id) ON DELETE CASCADE,
  action_type TEXT NOT NULL,
  action_payload JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE opportunity_duplicates (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  primary_opportunity_id UUID NOT NULL REFERENCES opportunities(id) ON DELETE CASCADE,
  duplicate_opportunity_id UUID NOT NULL REFERENCES opportunities(id) ON DELETE CASCADE,
  match_type TEXT NOT NULL,
  similarity_score NUMERIC(5,2),
  merged_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE opportunity_tags (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  opportunity_id UUID NOT NULL REFERENCES opportunities(id) ON DELETE CASCADE,
  tag TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (opportunity_id, tag)
);

CREATE TABLE opportunity_notes (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  opportunity_id UUID NOT NULL REFERENCES opportunities(id) ON DELETE CASCADE,
  note_text TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =============================================================================
-- TABLE GROUP 5: CATEGORY-SPECIFIC DETAILS
-- =============================================================================

CREATE TABLE client_lead_details (
  opportunity_id UUID PRIMARY KEY REFERENCES opportunities(id) ON DELETE CASCADE,
  client_type TEXT,
  need_detected TEXT,
  technical_service_category TEXT,
  lead_region TEXT,
  platform_message_link TEXT,
  contact_form_url TEXT,
  suggested_service_offer TEXT,
  south_africa_focus BOOLEAN DEFAULT false
);

CREATE TABLE phd_opportunity_details (
  opportunity_id UUID PRIMARY KEY REFERENCES opportunities(id) ON DELETE CASCADE,
  university TEXT,
  department TEXT,
  supervisor TEXT,
  funding_status TEXT DEFAULT 'unclear',
  funding_proof TEXT,
  deadline_proof TEXT,
  email_application_possible TEXT DEFAULT 'unclear',
  application_email TEXT,
  email_proof TEXT,
  portal_link TEXT,
  research_summary TEXT,
  why_fits_profile TEXT
);

CREATE TABLE job_opportunity_details (
  opportunity_id UUID PRIMARY KEY REFERENCES opportunities(id) ON DELETE CASCADE,
  company TEXT,
  seniority TEXT,
  work_mode TEXT,
  skills_required JSONB DEFAULT '[]'::jsonb,
  language_requirements JSONB DEFAULT '[]'::jsonb,
  salary_text TEXT,
  email_application_possible TEXT DEFAULT 'unclear',
  application_email TEXT,
  email_proof TEXT,
  portal_url TEXT,
  recruiter_contact TEXT,
  why_fits_profile TEXT
);

CREATE TABLE remote_job_details (
  opportunity_id UUID PRIMARY KEY REFERENCES opportunities(id) ON DELETE CASCADE,
  company TEXT,
  company_location TEXT,
  remote_restriction TEXT DEFAULT 'unclear',
  timezone_restriction TEXT,
  remote_proof TEXT,
  skills JSONB DEFAULT '[]'::jsonb,
  salary_text TEXT
);

-- =============================================================================
-- TABLE GROUP 6: RAG / VECTOR
-- =============================================================================

CREATE TABLE opportunity_knowledge_chunks (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  opportunity_id UUID REFERENCES opportunities(id) ON DELETE CASCADE,
  chunk_index INT NOT NULL,
  content TEXT NOT NULL,
  embedding vector(384),
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE embeddings_metadata (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  entity_type TEXT NOT NULL,
  entity_id UUID NOT NULL,
  model_name TEXT NOT NULL,
  dimensions INT NOT NULL,
  storage_backend TEXT DEFAULT 'chroma',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE rag_queries (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  query_text TEXT NOT NULL,
  query_type TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE rag_results (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  rag_query_id UUID NOT NULL REFERENCES rag_queries(id) ON DELETE CASCADE,
  chunk_id UUID,
  score NUMERIC(8,5),
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =============================================================================
-- TABLE GROUP 7: DOCUMENTS / STAGE 2-READY
-- =============================================================================

CREATE TABLE document_vault (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  title TEXT NOT NULL,
  doc_type TEXT NOT NULL,
  storage_path TEXT,
  content_hash TEXT,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE document_versions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  document_id UUID NOT NULL REFERENCES document_vault(id) ON DELETE CASCADE,
  version_number INT NOT NULL,
  storage_path TEXT,
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE document_bundles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  bundle_type TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE document_bundle_items (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  bundle_id UUID NOT NULL REFERENCES document_bundles(id) ON DELETE CASCADE,
  document_id UUID NOT NULL REFERENCES document_vault(id) ON DELETE CASCADE,
  sort_order INT DEFAULT 0
);

CREATE TABLE applications (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  opportunity_id UUID NOT NULL REFERENCES opportunities(id) ON DELETE CASCADE,
  status TEXT DEFAULT 'draft',
  application_method TEXT,
  contact_email TEXT,
  portal_url TEXT,
  stage2_ready BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE application_documents (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
  document_id UUID NOT NULL REFERENCES document_vault(id) ON DELETE CASCADE
);

CREATE TABLE email_drafts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  application_id UUID REFERENCES applications(id) ON DELETE CASCADE,
  opportunity_id UUID REFERENCES opportunities(id) ON DELETE CASCADE,
  subject TEXT,
  body TEXT,
  status TEXT DEFAULT 'draft',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE gmail_threads (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  application_id UUID REFERENCES applications(id) ON DELETE CASCADE,
  thread_id TEXT,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE portal_application_tasks (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
  task_status TEXT DEFAULT 'pending',
  portal_url TEXT,
  checklist JSONB DEFAULT '[]'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE follow_up_tasks (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
  due_at TIMESTAMPTZ,
  status TEXT DEFAULT 'pending',
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE application_events (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
  event_type TEXT NOT NULL,
  event_payload JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =============================================================================
-- TABLE GROUP 8: SYSTEM
-- =============================================================================

CREATE TABLE audit_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  actor TEXT DEFAULT 'system',
  action TEXT NOT NULL,
  entity_type TEXT,
  entity_id UUID,
  details JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE ai_model_runs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  model_name TEXT NOT NULL,
  run_type TEXT NOT NULL,
  input_hash TEXT,
  tokens_in INT,
  tokens_out INT,
  latency_ms INT,
  status TEXT,
  error_message TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE api_usage_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  service_name TEXT NOT NULL,
  endpoint TEXT,
  units_used NUMERIC(12,4),
  cost_estimate NUMERIC(12,4),
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE system_settings (
  key TEXT PRIMARY KEY,
  value JSONB NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE notification_logs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  channel TEXT,
  payload JSONB,
  status TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE backup_exports (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  export_type TEXT NOT NULL,
  storage_path TEXT,
  row_counts JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =============================================================================
-- INDEXES
-- =============================================================================

CREATE INDEX idx_opportunities_category ON opportunities(category);
CREATE INDEX idx_opportunities_subcategory ON opportunities(subcategory);
CREATE INDEX idx_opportunities_country ON opportunities(country);
CREATE INDEX idx_opportunities_city ON opportunities(city);
CREATE INDEX idx_opportunities_status ON opportunities(status);
CREATE INDEX idx_opportunities_viewed ON opportunities(viewed);
CREATE INDEX idx_opportunities_posted_date ON opportunities(posted_date);
CREATE INDEX idx_opportunities_deadline ON opportunities(deadline);
CREATE INDEX idx_opportunities_final_score ON opportunities(final_score DESC);
CREATE INDEX idx_opportunities_url_hash ON opportunities(url_hash);
CREATE INDEX idx_opportunities_content_hash ON opportunities(content_hash);
CREATE INDEX idx_sources_target_section ON sources(target_section);
CREATE INDEX idx_sources_enabled ON sources(enabled);
CREATE INDEX idx_discovered_urls_status ON discovered_urls(status);
CREATE INDEX idx_cleaned_posts_content_hash ON cleaned_posts(content_hash);

-- =============================================================================
-- RLS (single-user private app — enable after auth user exists)
-- =============================================================================

ALTER TABLE opportunities ENABLE ROW LEVEL SECURITY;
ALTER TABLE sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "authenticated_full_access_opportunities"
  ON opportunities FOR ALL
  TO authenticated
  USING (true)
  WITH CHECK (true);

CREATE POLICY "authenticated_full_access_sources"
  ON sources FOR ALL
  TO authenticated
  USING (true)
  WITH CHECK (true);

CREATE POLICY "authenticated_full_access_profiles"
  ON user_profiles FOR ALL
  TO authenticated
  USING (true)
  WITH CHECK (true);

-- Service role bypasses RLS for backend scripts.
