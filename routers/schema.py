import json
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends

from abuse_protection import enforce_job_start, enforce_rate_limit
from auth import get_current_user, get_supabase
from credentials import hydrate_job_settings, strip_secret_fields
from models import SchemaJobRequest, SchemaRow, SchemaSettings
from utils.dfs import get_serp_data
from utils.providers import generate_schema_text
from utils.schema_parse import extract_schema_json, wrap_json_ld
from utils.schema_prompt import build_schema_prompt
from utils.scraper import build_scrape_targets, scrape_with_jina

router = APIRouter()


def build_initial_job_record(user_id: str, request: SchemaJobRequest) -> dict[str, Any]:
    settings = strip_secret_fields(request.settings.model_dump())
    return {
        "user_id": user_id,
        "tool": "schema",
        "name": request.name,
        "status": "running",
        "rows": [row.model_dump(mode="json") for row in request.rows],
        "settings": settings,
        "results": [],
        "progress": {"total": len(request.rows), "completed": 0, "failed": 0},
    }


def scrape_sources(row: SchemaRow, settings: SchemaSettings) -> dict[str, str]:
    targets = build_scrape_targets(
        str(row.url),
        scrape_target=settings.scrape_target,
        scrape_homepage=settings.scrape_homepage,
        deep_scrape=settings.deep_scrape,
    )
    sources: dict[str, str] = {}
    for key, target_url in targets:
        try:
            sources[key] = scrape_with_jina(target_url)
        except Exception:
            continue
    return sources


def fetch_optional_serp(row: SchemaRow, settings: dict | SchemaSettings) -> str:
    values = settings if isinstance(settings, dict) else settings.model_dump()
    if not values.get("serp_check"):
        return ""
    login = values.get("dfs_login", "")
    password = values.get("dfs_password", "")
    if not login or not password:
        return ""
    keyword = row.keyword or str(row.url).split("//", 1)[-1].split("/", 1)[0]
    try:
        return json.dumps(get_serp_data(login, password, keyword), ensure_ascii=False)
    except Exception:
        return ""


def process_schema_row(
    row: SchemaRow,
    settings: SchemaSettings,
    runtime_settings: dict[str, Any],
) -> dict[str, Any]:
    try:
        scraped_content = scrape_sources(row, settings)
        merged_settings = {**settings.model_dump(), **runtime_settings}
        serp_data = fetch_optional_serp(row, merged_settings)
        prompt = build_schema_prompt(
            url=str(row.url),
            schema_type=settings.schema_type,
            scraped_content=scraped_content,
            serp_data=serp_data,
        )
        text = generate_schema_text(
            settings.provider,
            runtime_settings.get("api_key", ""),
            prompt,
            settings.model or None,
        )
        schema = extract_schema_json(text)
        schema_json = json.dumps(schema, ensure_ascii=False, indent=2)
        return {
            "url": str(row.url),
            "status": "complete",
            "schema_type": settings.schema_type,
            "schema": schema,
            "schema_json": schema_json,
            "schema_script": wrap_json_ld(schema),
            "source_summary": {
                "scraped_sections": list(scraped_content.keys()),
                "serp_used": bool(serp_data),
            },
            "error": None,
        }
    except Exception as exc:
        return {
            "url": str(row.url),
            "status": "failed",
            "schema_type": settings.schema_type,
            "schema": None,
            "schema_json": "",
            "schema_script": "",
            "source_summary": {"scraped_sections": [], "serp_used": False},
            "error": str(exc),
        }


def _update_job(sb, job_id: str, user_id: str, data: dict[str, Any]) -> None:
    (
        sb.table("jobs")
        .update(data)
        .eq("id", job_id)
        .eq("user_id", user_id)
        .eq("tool", "schema")
        .execute()
    )


def _is_cancelled(sb, job_id: str, user_id: str) -> bool:
    result = (
        sb.table("jobs")
        .select("status")
        .eq("id", job_id)
        .eq("user_id", user_id)
        .eq("tool", "schema")
        .execute()
    )
    return bool(result.data and result.data[0].get("status") in {"cancelling", "cancelled"})


def _run_schema_job(sb, user_id: str, job_id: str, request: SchemaJobRequest) -> None:
    runtime_settings = hydrate_job_settings(
        sb,
        user_id,
        request.settings.model_dump(),
    )
    results = []
    failed = 0
    for row in request.rows:
        if _is_cancelled(sb, job_id, user_id):
            _update_job(sb, job_id, user_id, {"status": "cancelled"})
            return
        result = process_schema_row(row, request.settings, runtime_settings)
        results.append(result)
        failed += 1 if result["status"] == "failed" else 0
        _update_job(sb, job_id, user_id, {
            "results": results,
            "progress": {
                "total": len(request.rows),
                "completed": len(results),
                "failed": failed,
            },
        })
        if _is_cancelled(sb, job_id, user_id):
            _update_job(sb, job_id, user_id, {"status": "cancelled"})
            return

    _update_job(sb, job_id, user_id, {
        "status": "complete" if failed == 0 else "completed_with_errors",
        "results": results,
        "progress": {
            "total": len(request.rows),
            "completed": len(results),
            "failed": failed,
        },
    })


@router.post("/run")
def run_schema_job(
    request: SchemaJobRequest,
    background_tasks: BackgroundTasks,
    user=Depends(get_current_user),
):
    sb = get_supabase()
    enforce_job_start(sb, user.id, "schema", len(request.rows), 25)
    enforce_rate_limit(sb, user.id, "schema", "job-create", 10)
    record = build_initial_job_record(user.id, request)
    created = sb.table("jobs").insert(record).execute()
    job_id = created.data[0]["id"]
    background_tasks.add_task(_run_schema_job, sb, user.id, job_id, request)
    return {"job_id": job_id}
