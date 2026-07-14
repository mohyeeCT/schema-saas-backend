from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from routers import jobs, schema

_ALLOWED_ORIGINS = {
    "https://copypilot.app",
    "https://www.copypilot.app",
    "http://localhost:3000",
}

app = FastAPI(
    title="CopyPilot Schema Generator Backend",
    description="Generate schema.org JSON-LD for CopyPilot users.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(_ALLOWED_ORIGINS),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "tool": "schema"}


@app.exception_handler(Exception)
async def _global_exception_handler(request: Request, exc: Exception):
    """Return browser-readable 500 responses for trusted CopyPilot origins."""
    headers = {}
    origin = request.headers.get("origin")
    if origin in _ALLOWED_ORIGINS:
        headers = {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
        }
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
        headers=headers,
    )


app.include_router(schema.router, prefix="/api/schema", tags=["schema"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
