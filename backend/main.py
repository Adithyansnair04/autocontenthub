"""
FastAPI backend for the Autonomous Content Factory.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.models.schemas import CampaignRequest, CampaignResult
from backend.services.orchestrator import run_campaign

app = FastAPI(
    title="Autonomous Content Factory",
    description="Multi-agent AI pipeline that transforms source material into platform-ready content",
    version="1.0.0",
)

# ── CORS (allow Streamlit frontend) ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "service": "Autonomous Content Factory",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/api/campaign", response_model=CampaignResult)
async def create_campaign(request: CampaignRequest):
    """Run the full content factory pipeline."""
    if not request.source_text.strip() and not request.source_url:
        raise HTTPException(
            status_code=400,
            detail="Please provide either source_text or source_url",
        )

    try:
        result = run_campaign(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Campaign failed: {str(e)}")