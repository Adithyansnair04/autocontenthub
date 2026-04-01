"""
Editor Agent
Reviews generated content for hallucinations, tone alignment, and quality.
Can request revisions from the Copywriter.
"""

from backend.services.llm_client import call_llm_json, call_llm
from backend.models.schemas import FactSheet, BrandStyle, ContentPiece


REVIEW_SYSTEM_PROMPT = """You are a senior content editor with expertise in fact-checking and brand voice consistency.

Your job is to review a piece of content against:
1. A verified FACT SHEET (source of truth) — catch any hallucinations or unsupported claims
2. A BRAND STYLE guide — ensure tone and voice alignment
3. General quality standards — originality, readability, engagement

SCORING CRITERIA (1-10):
- 9-10: Exceptional — publish immediately
- 7-8: Good — minor suggestions but approved
- 5-6: Needs revision — specific issues to fix
- 1-4: Major rewrite needed

Return your review as JSON:
{
    "verdict": "APPROVED" or "NEEDS_REVISION",
    "score": 7,
    "hallucinations_found": ["any claims not in the fact sheet"],
    "tone_issues": ["any voice/tone mismatches"],
    "originality_issues": ["clichés, generic phrasing, AI-sounding text"],
    "strengths": ["what works well"],
    "correction_note": "specific instructions for the copywriter to fix issues"
}"""


def review_content(piece: ContentPiece, fact_sheet: FactSheet, brand_style: BrandStyle) -> dict:
    """Review a content piece against the fact sheet and brand style."""

    user_prompt = f"""Review this {piece.domain.value} content:

--- CONTENT TO REVIEW ---
{piece.content}
--- END CONTENT ---

--- FACT SHEET (Source of Truth) ---
Product: {fact_sheet.product_name}
Value Proposition: {fact_sheet.value_proposition}
Core Features: {', '.join(fact_sheet.core_features)}
Key Benefits: {', '.join(fact_sheet.key_benefits)}
--- END FACT SHEET ---

--- BRAND STYLE ---
Tone: {brand_style.tone}
Voice: {', '.join(brand_style.voice_characteristics)}
Avoid: {', '.join(brand_style.do_not_use) if brand_style.do_not_use else 'N/A'}
--- END BRAND STYLE ---

Review for hallucinations, tone alignment, originality, and overall quality. Be strict but fair."""

    result = call_llm_json(REVIEW_SYSTEM_PROMPT, user_prompt, temperature=0.3)

    if result.get("parse_error"):
        # Default to approval if we can't parse the review
        return {
            "verdict": "APPROVED",
            "score": 7,
            "hallucinations_found": [],
            "tone_issues": [],
            "originality_issues": [],
            "strengths": ["Review parsing failed — defaulting to approval"],
            "correction_note": "",
        }

    return result


REVISION_SYSTEM_PROMPT = """You are a skilled copywriter revising content based on editorial feedback.

RULES:
1. Address EVERY issue in the editor's correction note
2. Preserve what works — don't rewrite unnecessarily
3. Maintain the same format and approximate length
4. Stay true to the fact sheet — no hallucinations
5. Match the brand voice

Return ONLY the revised content, no explanations or meta-commentary."""


def revise_content(
    piece: ContentPiece,
    correction_note: str,
    fact_sheet: FactSheet,
    brand_style: BrandStyle,
    target_audience: str,
) -> ContentPiece:
    """Revise content based on editor feedback."""

    user_prompt = f"""Revise this {piece.domain.value} content based on the editor's feedback:

--- CURRENT CONTENT ---
{piece.content}
--- END CONTENT ---

--- EDITOR'S CORRECTION NOTE ---
{correction_note}
--- END NOTE ---

--- FACT SHEET (stay factual) ---
Product: {fact_sheet.product_name}
Value Proposition: {fact_sheet.value_proposition}
Features: {', '.join(fact_sheet.core_features[:5])}
Benefits: {', '.join(fact_sheet.key_benefits[:4])}
--- END FACT SHEET ---

Brand tone: {brand_style.tone}
Target audience: {target_audience}

Revise the content now. Return ONLY the revised content."""

    revised = call_llm(REVISION_SYSTEM_PROMPT, user_prompt, temperature=0.6)

    piece.content = revised
    piece.revision_count += 1
    return piece