# schema-saas-backend - Repo Context

See `../CLAUDE.md` for full platform context, conventions, and working rules.

## What This Repo Is

FastAPI backend for the CopyPilot Schema Generator workflow. Deployed on
Railway EU West. Default branch: `main`. Current HEAD: `023a420`.
Runtime: Python 3.12.

Railway URL: `https://schema-saas-backend-production.up.railway.app`

## File Structure

```
main.py            - App, CORS, router mounts, health endpoint
auth.py            - Supabase token validation
credentials.py     - Server-side credential hydration and secret stripping
abuse_protection.py - Row limits, active-job checks, rate limits
models.py          - SchemaJobRequest, SchemaRow, SchemaSettings
routers/
  schema.py        - POST /api/schema/run and background worker
  jobs.py          - Schema-scoped job list/get/delete/rename/cancel/duplicate
utils/
  providers.py     - Claude provider routing for schema generation
  schema_prompt.py - Schema.org prompt construction and type guidance
  schema_parse.py  - JSON extraction and JSON-LD script wrapping
  scraper.py       - Page/source scraping helpers
  dfs.py           - Optional SERP fetch
schema.sql         - Reference schema including the `schema` tool
migrations/        - Schema tool constraint migration
tests/             - Provider, prompt, parser, worker, SQL, and abuse tests
```

## Endpoints

```
POST   /api/schema/run
GET    /api/jobs
GET    /api/jobs/{id}
PATCH  /api/jobs/{id}/rename
DELETE /api/jobs/{id}
POST   /api/jobs/{id}/cancel
POST   /api/jobs/{id}/duplicate
GET    /health
```

## Schema Pipeline

1. Strip secrets from job settings before saving the job.
2. Enforce row limit and job-create rate limit.
3. Hydrate runtime credentials server-side from saved settings.
4. Scrape target/homepage sources according to `scrape_target`,
   `scrape_homepage`, and `deep_scrape`.
5. Optionally fetch SERP context when `serp_check` is enabled.
6. Build the schema prompt with `build_schema_prompt`.
7. Generate text through `generate_schema_text`.
8. Extract schema JSON with `extract_schema_json` and wrap it as JSON-LD.
9. Update only the matching user-owned `schema` job.

## Key Model Fields

```python
provider: str = "Claude"
model: str = ""
schema_type: SchemaType = "LocalBusiness"
scrape_target: bool = True
scrape_homepage: bool = False
deep_scrape: bool = False
serp_check: bool = False
```

## Known Gotchas

- Schema currently supports Claude only in `utils/providers.py`; do not expose
  other providers in the UI unless the backend provider exists and is tested.
- Tests intentionally confirm Sonnet 5 schema calls omit `thinking`. Do not copy
  the FAQ `extra_body` thinking override here without a local regression test.
- Jobs must always be scoped with `.eq("tool", "schema")`.
- Background updates must remain scoped to both `user_id` and `tool`.
- `extract_schema_json` accepts `<schema>...</schema>` wrapped JSON and can fall
  back to raw JSON in text. Keep this parser strict enough to reject invalid JSON.
- Row limit is 25 per schema job.

## Local Dev Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt pytest
python -m pytest tests/ -v
```
