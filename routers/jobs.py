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


@router.get("")
def list_jobs(user=Depends(get_current_user)):
    sb = get_supabase()
    result = (
        _schema_job_query(sb, user.id)
        .order("created_at", desc=True)
        .execute()
    )
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
        .update({"status": "cancelling"})
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
    record = {
        "user_id": user.id,
        "tool": "schema",
        "name": f"{job.get('name') or 'Schema Generator Job'} copy",
        "status": "draft",
        "rows": job.get("rows") or [],
        "settings": job.get("settings") or {},
        "results": [],
        "progress": {"total": len(job.get("rows") or []), "completed": 0, "failed": 0},
    }
    result = sb.table("jobs").insert(record).execute()
    created = (result.data or [{}])[0]
    return {"job_id": created.get("id"), **created}
