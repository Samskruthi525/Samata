# Repository links

Replace `YOUR-ORG` once the GitHub organisation is decided. Status legend as in README §66.

| Repository | Purpose | URL (placeholder) | Status |
|---|---|---|---|
| `ambedkar-heritage-archive-main` | README, contracts, reference rules + tests, UI prototype, demo corpus, figures | https://github.com/YOUR-ORG/ambedkar-heritage-archive-main | ✅ this repository |
| `heritage-kiosk-agent` | GPIO bridge, loopback relay, manifest sync, cache DB (Pi) | https://github.com/YOUR-ORG/heritage-kiosk-agent | 🧪 core files in `kiosk-agent/` here |
| `heritage-kiosk-ui` | React + TypeScript kiosk UI, served locally on the Pi | https://github.com/YOUR-ORG/heritage-kiosk-ui | 🧪 single-file prototype in `prototype/` |
| `heritage-archive-api` | FastAPI: public, device and admin routes; rights gate; RAG; manifest signing | https://github.com/YOUR-ORG/heritage-archive-api | 📐 specified |
| `heritage-ingest-worker` | Fixity, OCR, ASR, derivatives, embeddings | https://github.com/YOUR-ORG/heritage-ingest-worker | 📐 specified |
| `heritage-infra` | Environments, backups, monitoring, secret wiring (names only) | https://github.com/YOUR-ORG/heritage-infra | 📐 specified |

Shared artefacts consumed by the implementation repositories:

- `reference/heritage_core` — trust rules + test vectors (vendored as a wheel)
- `contracts/*.schema.json`, `contracts/openapi-excerpt.yaml` — inter-repository contracts
- `schema/archive.sql` — catalogue schema (source: README §27)
- `kiosk-agent/cache_schema.sql` — offline cache schema (source: README §20.4)
