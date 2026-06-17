import math

from fastapi import HTTPException


def enforce_job_start(
    sb,
    user_id: str,
    tool: str,
    row_count: int,
    max_rows: int,
    exclude_job_id: str | None = None,
) -> None:
    if row_count > max_rows:
        raise HTTPException(
            status_code=400,
            detail=f"{tool} jobs can include up to {max_rows} URLs.",
        )

    query = (
        sb.table("jobs")
        .select("id")
        .eq("user_id", user_id)
        .eq("tool", tool)
        .in_("status", ["running", "cancelling"])
    )
    active = query.execute().data or []
    if exclude_job_id:
        active = [row for row in active if row.get("id") != exclude_job_id]
    if active:
        raise HTTPException(
            status_code=409,
            detail=f"A {tool} job is already running. Wait for it to finish before starting another.",
        )


def enforce_rate_limit(
    sb,
    user_id: str,
    tool: str,
    action: str,
    limit: int,
    window_seconds: int = 600,
) -> None:
    try:
        response = sb.rpc("check_rate_limit", {
            "p_user_id": user_id,
            "p_tool": tool,
            "p_action": action,
            "p_limit": limit,
            "p_window_seconds": window_seconds,
        }).execute()
        data = (response.data or [{}])[0]
    except Exception:
        return

    if data.get("allowed", True):
        return

    retry_after = int(data.get("retry_after_seconds") or window_seconds)
    minutes = max(1, math.ceil(retry_after / 60))
    raise HTTPException(
        status_code=429,
        detail=f"Too many {action} requests. Please wait {minutes} minutes before trying again.",
        headers={"Retry-After": str(retry_after)},
    )
