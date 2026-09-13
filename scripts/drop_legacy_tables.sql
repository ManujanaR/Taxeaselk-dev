-- One-time cleanup for a Supabase/Postgres database that was created by the
-- old prototype backend (string-keyed schema). Run in the Supabase SQL editor
-- BEFORE starting the new backend for the first time. The new backend then
-- creates its own tables on boot (Base.metadata.create_all).
--
-- Safe to run on an empty database: every statement is IF EXISTS.

-- 2026-09-14: issues were merged into requests
DROP TABLE IF EXISTS issues CASCADE;
ALTER TABLE IF EXISTS attachments DROP COLUMN IF EXISTS issue_id;

DROP TABLE IF EXISTS
  auditor_settings,
  audit_logs,
  notifications,
  discussion_messages,
  discussion_threads,
  response_attachments,
  client_responses,
  auditor_requests,
  auditor_review_issues,
  company_checklist_items,
  financial_line_items,
  financial_summaries,
  documents,
  engagements,
  auditor_reviews,
  auditor_profiles,
  companies,
  users
CASCADE;
