ALTER TABLE opportunity_status_history ENABLE ROW LEVEL SECURITY;

CREATE POLICY "authenticated_full_access_status_history"
  ON opportunity_status_history FOR ALL
  TO authenticated
  USING (true)
  WITH CHECK (true);
