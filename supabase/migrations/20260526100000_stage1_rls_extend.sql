-- Extend RLS for authenticated dashboard reads/writes

ALTER TABLE opportunity_evidence ENABLE ROW LEVEL SECURITY;
ALTER TABLE opportunity_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE opportunity_notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE opportunity_user_actions ENABLE ROW LEVEL SECURITY;
ALTER TABLE client_lead_details ENABLE ROW LEVEL SECURITY;
ALTER TABLE phd_opportunity_details ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_opportunity_details ENABLE ROW LEVEL SECURITY;
ALTER TABLE remote_job_details ENABLE ROW LEVEL SECURITY;
ALTER TABLE profile_skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE profile_experience ENABLE ROW LEVEL SECURITY;
ALTER TABLE profile_education ENABLE ROW LEVEL SECURITY;
ALTER TABLE profile_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE profile_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE profile_knowledge_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE source_search_terms ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "authenticated_full_access_evidence"
  ON opportunity_evidence FOR ALL TO authenticated USING (true) WITH CHECK (true);

CREATE POLICY "authenticated_full_access_scores"
  ON opportunity_scores FOR ALL TO authenticated USING (true) WITH CHECK (true);

CREATE POLICY "authenticated_full_access_notes"
  ON opportunity_notes FOR ALL TO authenticated USING (true) WITH CHECK (true);

CREATE POLICY "authenticated_full_access_user_actions"
  ON opportunity_user_actions FOR ALL TO authenticated USING (true) WITH CHECK (true);

CREATE POLICY "authenticated_full_access_client_details"
  ON client_lead_details FOR ALL TO authenticated USING (true) WITH CHECK (true);

CREATE POLICY "authenticated_full_access_phd_details"
  ON phd_opportunity_details FOR ALL TO authenticated USING (true) WITH CHECK (true);

CREATE POLICY "authenticated_full_access_job_details"
  ON job_opportunity_details FOR ALL TO authenticated USING (true) WITH CHECK (true);

CREATE POLICY "authenticated_full_access_remote_details"
  ON remote_job_details FOR ALL TO authenticated USING (true) WITH CHECK (true);

CREATE POLICY "authenticated_full_access_profile_skills"
  ON profile_skills FOR ALL TO authenticated USING (true) WITH CHECK (true);

CREATE POLICY "authenticated_full_access_profile_experience"
  ON profile_experience FOR ALL TO authenticated USING (true) WITH CHECK (true);

CREATE POLICY "authenticated_full_access_profile_education"
  ON profile_education FOR ALL TO authenticated USING (true) WITH CHECK (true);

CREATE POLICY "authenticated_full_access_profile_preferences"
  ON profile_preferences FOR ALL TO authenticated USING (true) WITH CHECK (true);

CREATE POLICY "authenticated_full_access_profile_documents"
  ON profile_documents FOR ALL TO authenticated USING (true) WITH CHECK (true);

CREATE POLICY "authenticated_full_access_profile_chunks"
  ON profile_knowledge_chunks FOR ALL TO authenticated USING (true) WITH CHECK (true);

CREATE POLICY "authenticated_full_access_search_terms"
  ON source_search_terms FOR ALL TO authenticated USING (true) WITH CHECK (true);

CREATE POLICY "authenticated_read_audit_logs"
  ON audit_logs FOR SELECT TO authenticated USING (true);
