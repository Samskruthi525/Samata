-- Heritage archive catalogue schema (PostgreSQL 16 + pgvector).
-- Copied from README §27 (the README is the reviewed source; keep them in sync).
-- Status: specified, not yet migrated in heritage-archive-api.

-- heritage-archive-api/migrations/0001_init.sql   (📐 specified; adapt vector dimension to the chosen model)
CREATE EXTENSION IF NOT EXISTS vector;          -- if pgvector is available

CREATE TABLE collection (
  id text PRIMARY KEY,
  name text NOT NULL,
  custodian text NOT NULL,
  scope text,
  ingestion_agreement_uri text
);

CREATE TABLE rights_policy (
  id text PRIMARY KEY,
  status text NOT NULL CHECK (status IN
    ('unknown','permission_pending','public_display_approved','restricted_to_staff','link_only','withdrawn')),
  public_display boolean NOT NULL DEFAULT false,
  download_allowed boolean NOT NULL DEFAULT false,
  derivative_allowed boolean NOT NULL DEFAULT false,
  ai_processing_allowed boolean NOT NULL DEFAULT false,
  offline_cache_allowed boolean NOT NULL DEFAULT false,
  rights_holder text,
  attribution_text text,
  restrictions text,
  permission_record_uri text,
  review_date date,
  reviewed_by text,
  CHECK (status <> 'public_display_approved' OR (permission_record_uri IS NOT NULL AND review_date IS NOT NULL))
);

CREATE TABLE archive_item (
  id text PRIMARY KEY,
  collection_id text NOT NULL REFERENCES collection(id),
  rights_id text NOT NULL REFERENCES rights_policy(id),
  kind text NOT NULL CHECK (kind IN ('writing','constitutional','manuscript_photo','media','interpretive')),
  title text NOT NULL,
  creator text, creator_role text, speaker text, speaker_verified boolean NOT NULL DEFAULT false,
  date_label text, date_from date, date_to date,
  date_precision text CHECK (date_precision IN ('day','month','year','circa','range','range_circa','unverified')),
  language_code text, script_code text,
  edition_label text, volume_label text, publisher text,
  media_kind text CHECK (media_kind IN ('authentic','narration','interview','documentary')),
  source_uri text NOT NULL,                     -- immutable once set (trigger below)
  accession_ref text,
  description text,
  status text NOT NULL DEFAULT 'draft'
    CHECK (status IN ('draft','in_review','approved_1','published','withdrawn')),
  approved_1_by text, published_by text,
  CHECK (published_by IS NULL OR published_by <> approved_1_by),   -- two different people
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE asset (
  id text PRIMARY KEY,
  item_id text NOT NULL REFERENCES archive_item(id) ON DELETE RESTRICT,
  role text NOT NULL CHECK (role IN ('master','access','processing')),
  derived_from text REFERENCES asset(id),
  uri text NOT NULL, media_type text NOT NULL, bytes bigint,
  sha256 char(64) NOT NULL,
  transformations jsonb NOT NULL DEFAULT '[]',
  capture_device text, captured_at timestamptz,
  version integer NOT NULL DEFAULT 1,
  CHECK (role <> 'master' OR derived_from IS NULL)
);

CREATE TABLE page (
  id text PRIMARY KEY,
  item_id text NOT NULL REFERENCES archive_item(id),
  pdf_page_index integer NOT NULL,              -- 0-based internally (documented)
  printed_page_label text,                      -- 'xii', '978', 'Part III', …
  access_image_asset text REFERENCES asset(id),
  reviewed_text text,
  ocr_text text,
  ocr_engine text, ocr_confidence real,
  ocr_status text CHECK (ocr_status IN ('none','candidate','reviewed','transcription_pending')),
  reviewed_by text, reviewed_at timestamptz,
  UNIQUE (item_id, pdf_page_index)
);

CREATE TABLE passage (
  id text PRIMARY KEY,
  page_id text NOT NULL REFERENCES page(id),
  exact_text text NOT NULL,
  start_offset integer, end_offset integer,
  transcription_version integer NOT NULL DEFAULT 1,
  language_code text,
  is_translation boolean NOT NULL DEFAULT false,
  translation_of text REFERENCES passage(id),
  translator_or_model text,
  reviewed boolean NOT NULL DEFAULT false,
  tsv tsvector GENERATED ALWAYS AS (to_tsvector('simple', exact_text)) STORED,
  embedding vector(768)                         -- ILLUSTRATIVE: must match the actual chosen model
);
CREATE INDEX passage_tsv_idx ON passage USING gin (tsv);
CREATE INDEX passage_vec_idx ON passage USING hnsw (embedding vector_cosine_ops);

CREATE TABLE transcript_segment (
  id text PRIMARY KEY,
  item_id text NOT NULL REFERENCES archive_item(id),
  start_ms integer NOT NULL, end_ms integer NOT NULL,
  words text NOT NULL,
  speaker text, speaker_verified boolean NOT NULL DEFAULT false,
  asr_engine text, reviewed boolean NOT NULL DEFAULT false,
  CHECK (end_ms > start_ms)
);

CREATE TABLE timeline_event (
  id text PRIMARY KEY,
  event_date_label text NOT NULL, date_from date, date_to date,
  label text NOT NULL, display_text text NOT NULL,
  author_editor text, reviewed_by text, version integer NOT NULL DEFAULT 1,
  status text NOT NULL DEFAULT 'draft' CHECK (status IN ('draft','in_review','published','withdrawn'))
);

CREATE TABLE event_evidence (                    -- own ID: one event may cite many passages of one item
  id text PRIMARY KEY,
  event_id text NOT NULL REFERENCES timeline_event(id) ON DELETE CASCADE,
  item_id text NOT NULL REFERENCES archive_item(id),
  relation text NOT NULL,
  page_id text REFERENCES page(id),
  passage_id text REFERENCES passage(id),
  time_start_ms integer, time_end_ms integer,
  UNIQUE (event_id, item_id, page_id, passage_id, time_start_ms)
);

CREATE TABLE relation (                          -- knowledge map: reviewed triples only
  id text PRIMARY KEY,
  subject_id text NOT NULL, predicate text NOT NULL, object_id text NOT NULL,
  evidence_id text REFERENCES event_evidence(id),
  confidence text CHECK (confidence IN ('verified','probable','disputed')),
  reviewed_by text NOT NULL
);

CREATE TABLE audit_log (                         -- append-only
  id bigserial PRIMARY KEY,
  at timestamptz NOT NULL DEFAULT now(),
  actor text NOT NULL, actor_kind text NOT NULL CHECK (actor_kind IN ('human','device','worker')),
  action text NOT NULL, object_type text NOT NULL, object_id text NOT NULL,
  before jsonb, after jsonb, reason text
);
REVOKE UPDATE, DELETE ON audit_log FROM PUBLIC;

-- source_uri immutability
CREATE FUNCTION forbid_source_uri_change() RETURNS trigger AS $$
BEGIN
  IF NEW.source_uri IS DISTINCT FROM OLD.source_uri THEN
    RAISE EXCEPTION 'source_uri is immutable; create a new item or record a correction';
  END IF;
  RETURN NEW;
END $$ LANGUAGE plpgsql;
CREATE TRIGGER archive_item_source_uri BEFORE UPDATE ON archive_item
  FOR EACH ROW EXECUTE FUNCTION forbid_source_uri_change();

-- public view used by every public/device route
CREATE VIEW public_item AS
  SELECT i.* FROM archive_item i JOIN rights_policy r ON r.id = i.rights_id
  WHERE i.status = 'published' AND r.status IN ('public_display_approved','link_only');
