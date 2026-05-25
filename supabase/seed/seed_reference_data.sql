-- Reference data for Stage 1 (idempotent inserts)

INSERT INTO source_categories (name, description)
VALUES
  ('client_lead', 'Small-business and freelance technical service leads'),
  ('phd', 'Doctoral and research positions'),
  ('job', 'Employment opportunities'),
  ('remote_job', 'Remote employment opportunities')
ON CONFLICT (name) DO NOTHING;

INSERT INTO system_settings (key, value)
VALUES
  ('stage1_version', '"1.0.0"'::jsonb),
  ('scoring_version', '"stage1_v1"'::jsonb)
ON CONFLICT (key) DO NOTHING;
