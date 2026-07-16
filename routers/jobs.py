from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from abuse_protection import enforce_rate_limit
from auth import get_current_user, get_supabase

router = APIRouter()


class RenameRequest(BaseModel):
    name: str


def _schema_job_query(sb, user_id: str):
    return sb.table("jobs").select("*").eq("user_id", user_id).eq("tool", "schema")


def _get_schema_job(sb, user_id: str, job_id: str) -> dict:
    result = _schema_job_query(sb, user_id).eq("id", job_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Job not found")
    return result.data[0]


def build_duplicate_job_record(user_id: str, job: dict) -> dict:
    rows = job.get("rows") or []
    results = job.get("results") or []
    failed_rows = sum(
        1
        for result in results
        if result.get("error") or result.get("status") in {"error", "failed"}
    )
    return {
        "user_id": user_id,
        "client_profile_id": job.get("client_profile_id"),
        "tool": "schema",
        "name": f"{job.get('name') or 'Schema Generator Job'} copy",
        "status": "complete",
        "rows": rows,
        "settings": job.get("settings") or {},
        "results": results,
        "total_rows": len(rows),
        "completed_rows": len(results),
        "failed_rows": failed_rows,
        "current_step": "Duplicated.",
    }


@router.get("")
def list_jobs(
    client_profile_id: str | None = None,
    unassigned: bool = False,
    user=Depends(get_current_user),
):
    sb = get_supabase()
    query = _schema_job_query(sb, user.id)
    if client_profile_id:
        query = query.eq("client_profile_id", client_profile_id)
    elif unassigned:
        query = query.is_("client_profile_id", "null")
    result = query.order("created_at", desc=True).execute()
    return result.data or []


@router.get("/{job_id}")
def get_job(job_id: str, user=Depends(get_current_user)):
    sb = get_supabase()
    return _get_schema_job(sb, user.id, job_id)


@router.patch("/{job_id}/rename")
def rename_job(job_id: str, request: RenameRequest, user=Depends(get_current_user)):
    sb = get_supabase()
    _get_schema_job(sb, user.id, job_id)
    result = (
        sb.table("jobs")
        .update({"name": request.name})
        .eq("id", job_id)
        .eq("user_id", user.id)
        .eq("tool", "schema")
        .execute()
    )
    return (result.data or [{}])[0]


@router.delete("/{job_id}")
def delete_job(job_id: str, user=Depends(get_current_user)):
    sb = get_supabase()
    _get_schema_job(sb, user.id, job_id)
    sb.table("jobs").delete().eq("id", job_id).eq("user_id", user.id).eq("tool", "schema").execute()
    return {"ok": True}


@router.post("/{job_id}/cancel")
def cancel_job(job_id: str, user=Depends(get_current_user)):
    sb = get_supabase()
    _get_schema_job(sb, user.id, job_id)
    result = (
        sb.table("jobs")
        .update({"status": "cancelled", "current_step": "Cancelled — stopping after current row..."})
        .eq("id", job_id)
        .eq("user_id", user.id)
        .eq("tool", "schema")
        .execute()
    )
    return (result.data or [{}])[0]


@router.post("/{job_id}/duplicate")
def duplicate_job(job_id: str, user=Depends(get_current_user)):
    sb = get_supabase()
    job = _get_schema_job(sb, user.id, job_id)
    enforce_rate_limit(sb, user.id, "schema", "job-create", 10)
    record = build_duplicate_job_record(user.id, job)
    result = sb.table("jobs").insert(record).execute()
    created = (result.data or [{}])[0]
    return {"job_id": created.get("id"), **created}
