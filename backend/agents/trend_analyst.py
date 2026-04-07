"""
Trend Analyst Agent
Analyzes current industry trends relevant to the product/topic and generates
a TrendContext that enriches the copywriter's prompts with timely insights.
"""

from backend.services.llm_client import call_llm_json
from backend.models.schemas import FactSheet, TrendContext


TREND_SYSTEM_PROMPT = """You are a sharp market intelligence analyst with deep knowledge of technology, business, and consumer trends across LinkedIn, Twitter/X, email newsletters, and blog ecosystems.

Your job: given a product/topic fact sheet, synthesize the most relevant *current* industry trends, content patterns, and platform-specific hooks that a copywriter should weave into their content to make it feel timely, credible, and resonant.

RULES:
1. Be specific — no vague statements like "AI is growing fast". Name the actual trend, movement, or tension.
2. Focus on trends a professional audience would recognize and care about RIGHT NOW.
3. Include platform-specific content trends (what's performing on LinkedIn vs X vs blogs vs email currently).
4. Identify the dominant anxieties, aspirations, and debates in the product's industry.
5. Note any relevant regulatory, economic, or cultural shifts that add urgency to this topic.
6. Suggest 3–5 strong content angles/framings that feel fresh and trend-aligned.

Return ONLY valid JSON:
{
    "industry_trends": ["specific trend 1", "specific trend 2", ...],
    "platform_trends": {
        "linkedin": ["what's working on LinkedIn right now"],
        "twitter": ["what's working on X/Twitter right now"],
        "blog": ["what's working in long-form blog content right now"],
        "email": ["what's working in email right now"]
    },
    "dominant_tensions": ["key industry anxiety or debate 1", "key industry anxiety or debate 2", ...],
    "urgency_signals": ["economic/regulatory/cultural shift that creates urgency"],
    "content_angles": ["fresh angle 1", "fresh angle 2", "fresh angle 3"],
    "trending_vocabulary": ["term1", "term2", "term3"],
    "avoid_overused_angles": ["tired angle 1", "tired angle 2"]
}"""


def analyze_trends(fact_sheet: FactSheet, target_audience: str) -> TrendContext:
    """Analyze current industry trends relevant to the product and audience."""

    user_prompt = f"""Analyze current trends for this product and audience:

PRODUCT: {fact_sheet.product_name}
INDUSTRY/CATEGORY: {fact_sheet.value_proposition}
KEY FEATURES: {', '.join(fact_sheet.core_features[:5])}
KEY BENEFITS: {', '.join(fact_sheet.key_benefits[:4])}
TARGET AUDIENCE: {target_audience}
SUMMARY: {fact_sheet.raw_summary}

Identify the most relevant current industry trends, platform-specific content patterns, and fresh angles that will make the copywriter's content feel timely, urgent, and authentic. Be specific and actionable."""

    result = call_llm_json(TREND_SYSTEM_PROMPT, user_prompt, temperature=0.6)

    if result.get("parse_error"):
        # Graceful fallback — return empty context so copywriter still works
        return TrendContext(
            industry_trends=["Increasing demand for automation and efficiency"],
            platform_trends={
                "linkedin": ["Short-form insights with data points are performing well"],
                "twitter": ["Threads with numbered lists get higher engagement"],
                "blog": ["Practical how-to content outperforms thought leadership"],
                "email": ["Personalized subject lines improve open rates significantly"],
            },
            dominant_tensions=["Cost vs. quality trade-offs", "AI adoption vs. job security fears"],
            urgency_signals=["Economic pressure to do more with fewer resources"],
            content_angles=[
                "The efficiency angle — quantify the time/cost savings",
                "The risk angle — what happens if you don't adapt",
                "The social proof angle — others in your space are already doing this",
            ],
            trending_vocabulary=["ROI-driven", "outcome-focused", "workflow"],
            avoid_overused_angles=["'The future of X is here'", "'Transform your business'"],
        )

    platform_raw = result.get("platform_trends", {})

    return TrendContext(
        industry_trends=result.get("industry_trends", []),
        platform_trends={
            "linkedin": platform_raw.get("linkedin", []),
            "twitter": platform_raw.get("twitter", []),
            "blog": platform_raw.get("blog", []),
            "email": platform_raw.get("email", []),
        },
        dominant_tensions=result.get("dominant_tensions", []),
        urgency_signals=result.get("urgency_signals", []),
        content_angles=result.get("content_angles", []),
        trending_vocabulary=result.get("trending_vocabulary", []),
        avoid_overused_angles=result.get("avoid_overused_angles", []),
    )
