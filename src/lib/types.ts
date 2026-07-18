export type Programme = {
  id: string; user_id: string; name: string; platform: string; programme_ref: string;
  enabled: boolean; notes: string; scope_summary: string; review_due_date: string | null;
  created_at: string; updated_at: string;
};

export type Asset = {
  id: string; user_id: string; programme_id: string; value: string;
  asset_type: "Domain" | "Wildcard" | "API" | "Mobile" | "Other";
  notes: string; created_at: string; updated_at: string;
};

export type Finding = {
  id: string; user_id: string; programme_id: string; asset_id: string | null;
  title: string; description: string; severity: string; status: string; notes: string;
  source_reference: string; discovered_at: string; created_at: string; updated_at: string;
  programmes?: { name: string } | null; assets?: { value: string } | null;
};

export type Evidence = {
  id: string; finding_id: string; notes: string; url: string;
  screenshot_metadata: string; request_metadata: string; response_metadata: string;
  captured_at: string; created_at: string;
};

export type Report = {
  id: string; finding_id: string; title: string; summary: string; steps: string;
  expected_behaviour: string; actual_behaviour: string; impact: string;
  evidence_text: string; suggested_remediation: string; status: string;
  created_at: string; updated_at: string;
};

export const severities = ["Critical", "High", "Medium", "Low", "Informational"];
export const statuses = ["New", "Investigating", "Needs Evidence", "Verified", "Ready to Report", "Submitted", "Closed"];
export const assetTypes = ["Domain", "Wildcard", "API", "Mobile", "Other"];
