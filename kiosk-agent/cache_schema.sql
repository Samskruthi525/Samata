-- /var/lib/heritage-kiosk/cache.db   (owner: kiosk user, mode 0600)
CREATE TABLE manifest_state (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  version INTEGER NOT NULL,
  issued_at TEXT NOT NULL,
  expires_at TEXT NOT NULL,
  applied_at TEXT NOT NULL
);
CREATE TABLE cached_item (
  item_id TEXT PRIMARY KEY,
  kind TEXT NOT NULL,
  title TEXT NOT NULL,
  rights_label TEXT NOT NULL,        -- attribution text shown in the viewer
  card_json TEXT NOT NULL,           -- display metadata (no private fields)
  manifest_version INTEGER NOT NULL
);
CREATE TABLE cached_asset (
  asset_id TEXT PRIMARY KEY,
  item_id TEXT NOT NULL REFERENCES cached_item(item_id) ON DELETE CASCADE,
  role TEXT NOT NULL CHECK (role IN ('access_image','access_pdf','caption','audio','video','thumb')),
  path TEXT NOT NULL,
  sha256 TEXT NOT NULL
);
CREATE VIRTUAL TABLE cached_text USING fts5(
  passage_id UNINDEXED, item_id UNINDEXED, printed_page UNINDEXED, text,
  tokenize = 'unicode61 remove_diacritics 2'
);
