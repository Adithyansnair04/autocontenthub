"""
Researcher Agent
Extracts structured facts from source material to build a Source of Truth fact sheet.
"""

from backend.services.llm_client import call_llm_json
from backend.models.schemas import FactSheet


RESEARCH_SYSTEM_PROMPT = """You are a meticulous research analyst who extracts verified facts from source documents.

Your job is to read raw text (product pages, press releases, technical docs) and produce a structured fact sheet.

RULES:
1. Only include facts that are EXPLICITLY stated in the source — never infer or speculate
2. Flag any ambiguous claims where the source is unclear or could be misleading
3. Distinguish between features (what it does) and benefits (why it matters)
4. Extract technical specs, pricing, and any quantitative claims separately

Return your analysis as JSON with this exact structure:
{
    "product_name": "string",
    "value_proposition": "one-sentence summary of the core value",
    "core_features": ["feature1", "feature2", ...],
    "key_benefits": ["benefit1", "benefit2", ...],
    "technical_specs": ["spec1", "spec2", ...],
    "target_audience": "who this is for",
    "ambiguous_statements": ["claim that needs clarification", ...],
    "raw_summary": "2-3 sentence factual summary"
}"""


def extract_facts(source_text: str, target_audience: str = "") -> FactSheet:
    """Extract structured facts from source material."""

    user_prompt = f"""Analyze this source material and extract a verified fact sheet:

--- SOURCE MATERIAL ---
{source_text[:6000]}
--- END ---

Target audience context: {target_audience if target_audience else 'general professionals'}

Extract all facts, features, benefits, and flag any ambiguous claims."""

    result = call_llm_json(RESEARCH_SYSTEM_PROMPT, user_prompt)

    if result.get("parse_error"):
        # Fallback: create a basic fact sheet from the raw text
        return FactSheet(
            product_name="Unknown Product",
            value_proposition="See source material for details.",
            core_features=["See source material"],
            key_benefits=["See source material"],
            target_audience=target_audience or "general professionals",
            raw_summary=source_text[:500],
        )

    return FactSheet(
        product_name=result.get("product_name", "Unknown"),
        value_proposition=result.get("value_proposition", ""),
        core_features=result.get("core_features", []),
        key_benefits=result.get("key_benefits", []),
        technical_specs=result.get("technical_specs", []),
        target_audience=result.get("target_audience", target_audience),
        ambiguous_statements=result.get("ambiguous_statements", []),
        raw_summary=result.get("raw_summary", ""),
    )