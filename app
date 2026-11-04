
ALTER TABLE kochi_air_quality ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow read"
ON kochi_air_quality
FOR SELECT TO anon
USING (true);

CREATE POLICY "Allow insert"
ON kochi_air_quality
FOR INSERT TO anon
WITH CHECK (true);
