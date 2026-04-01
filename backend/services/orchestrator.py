"""
Orchestrator — coordinates all agents in the content factory pipeline.
"""

import time
from datetime import datetime
from typing import Callable, Optional

from backend.models.schemas import (
    CampaignRequest, CampaignResult, BrandStyle, FactSheet,
    ContentPiece, ContentDomain, AgentLog
)
from backend.agents.brand_analyst import analyze_brand
from backend.agents.researcher import extract_facts
from backend.agents.copywriter import generate_content
from backend.agents.editor import review_content, revise_content
from backend.services.scraper import scrape_source_url
from backend.config import settings


def _log(agent: str, action: str, message: str) -> AgentLog:
    """Create a timestamped agent log entry."""
    return AgentLog(
        agent=agent,
        action=action,
        message=message,
        timestamp=datetime.now().strftime("%H:%M:%S")
    )


def run_campaign(
    request: CampaignRequest,
    on_log: Optional[Callable[[AgentLog], None]] = None
) -> CampaignResult:
    """
    Run the full content factory pipeline:
    1. Brand Analysis (if URL provided)
    2. Source Research & Fact Extraction
    3. Content Generation (for selected domains)
    4. Editorial Review & Revision Loop
    """
    result = CampaignResult()
    logs = []

    def log(agent: str, action: str, message: str):
        entry = _log(agent, action, message)
        logs.append(entry)
        result.agent_logs = logs
        if on_log:
            on_log(entry)

    # ══════════════════════════════════════════════
    # PHASE 1: Brand Style Analysis
    # ══════════════════════════════════════════════
    if request.brand_url:
        log("Brand Analyst", "🔍 Scraping", f"Analyzing brand website: {request.brand_url}")
        try:
            brand_style = analyze_brand(request.brand_url)
            result.brand_style = brand_style
            log("Brand Analyst", "✅ Complete",
                f"Brand voice identified: {brand_style.tone} | "
                f"Traits: {', '.join(brand_style.voice_characteristics[:3])}")
        except Exception as e:
            log("Brand Analyst", "⚠️ Warning", f"Brand analysis failed: {str(e)}. Using defaults.")
            brand_style = BrandStyle(tone="professional and clear",
                                     voice_characteristics=["professional", "clear", "trustworthy"])
            result.brand_style = brand_style
    else:
        brand_style = BrandStyle(tone="professional and clear",
                                 voice_characteristics=["professional", "clear", "trustworthy"])
        result.brand_style = brand_style
        log("Brand Analyst", "ℹ️ Skipped", "No brand URL provided. Using default professional style.")

    # ══════════════════════════════════════════════
    # PHASE 2: Source Material Processing
    # ══════════════════════════════════════════════
    source_text = request.source_text

    if request.source_url and not source_text.strip():
        log("Researcher", "🔍 Scraping", f"Fetching source content from: {request.source_url}")
        source_text = scrape_source_url(request.source_url)

    log("Researcher", "📊 Analyzing", "Extracting facts and building Source of Truth...")
    try:
        fact_sheet = extract_facts(source_text, request.target_audience)
        result.fact_sheet = fact_sheet
        log("Researcher", "✅ Complete",
            f"Fact sheet ready — Product: {fact_sheet.product_name} | "
            f"Features: {len(fact_sheet.core_features)} | "
            f"Ambiguous items: {len(fact_sheet.ambiguous_statements)}")

        if fact_sheet.ambiguous_statements:
            for stmt in fact_sheet.ambiguous_statements:
                log("Researcher", "⚠️ Ambiguous", f"Flagged: \"{stmt}\"")
    except Exception as e:
        log("Researcher", "❌ Error", f"Fact extraction failed: {str(e)}")
        result.status = "error"
        return result

    # ══════════════════════════════════════════════
    # PHASE 3: Content Generation
    # ══════════════════════════════════════════════
    for domain in request.selected_domains:
        log("Copywriter", "✍️ Writing", f"Generating {domain.value} content...")
        try:
            piece = generate_content(domain, fact_sheet, brand_style, request.target_audience)
            log("Copywriter", "📝 Draft Ready", f"{domain.value} first draft complete ({len(piece.content)} chars)")

            # ══════════════════════════════════════
            # PHASE 4: Editorial Review Loop
            # ══════════════════════════════════════
            for attempt in range(settings.MAX_EDITOR_RETRIES):
                log("Editor", "🔎 Reviewing", f"Reviewing {domain.value} draft (attempt {attempt + 1})...")

                review = review_content(piece, fact_sheet, brand_style)
                verdict = review.get("verdict", "APPROVED")
                score = review.get("score", 7)
                correction = review.get("correction_note", "")

                if verdict == "APPROVED" or score >= 7:
                    piece.status = "approved"
                    piece.editor_notes = f"Score: {score}/10. Approved."
                    log("Editor", "✅ Approved",
                        f"{domain.value} approved with score {score}/10")
                    break
                else:
                    issues = []
                    if review.get("hallucinations_found"):
                        issues.append(f"Hallucinations: {', '.join(review['hallucinations_found'][:2])}")
                    if review.get("tone_issues"):
                        issues.append(f"Tone: {', '.join(review['tone_issues'][:2])}")
                    if review.get("originality_issues"):
                        issues.append(f"Originality: {', '.join(review['originality_issues'][:2])}")

                    log("Editor", "❌ Rejected",
                        f"{domain.value} rejected (score {score}/10). Issues: {'; '.join(issues)}")
                    log("Editor", "📋 Correction Note", correction)
                    log("Copywriter", "🔄 Revising", f"Revising {domain.value} based on editor feedback...")

                    piece = revise_content(piece, correction, fact_sheet, brand_style, request.target_audience)
                    log("Copywriter", "📝 Revised", f"{domain.value} revision {piece.revision_count} complete")

            if piece.status != "approved":
                piece.status = "approved_with_caveats"
                log("Editor", "⚠️ Final Accept",
                    f"{domain.value} accepted after {settings.MAX_EDITOR_RETRIES} revisions")

            result.content_pieces.append(piece)

        except Exception as e:
            log("Copywriter", "❌ Error", f"Failed to generate {domain.value}: {str(e)}")
            result.content_pieces.append(ContentPiece(
                domain=domain, content=f"Error: {str(e)}", status="error"
            ))

    result.status = "complete"
    log("System", "🎉 Done", f"Campaign complete! {len(result.content_pieces)} content pieces generated.")
    return result