from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import jobs, schema

app = FastAPI(
    title="CopyPilot Schema Generator Backend",
    description="Generate schema.org JSON-LD for CopyPilot users.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://copypilot.app",
        "https://www.copypilot.app",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "tool": "schema"}


app.include_router(schema.router, prefix="/api/schema", tags=["schema"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
