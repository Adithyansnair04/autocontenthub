"""
Brand Analyst Agent
Analyzes a brand's website to extract voice, tone, and style guidelines.
"""

from backend.services.llm_client import call_llm_json, call_llm
from backend.services.scraper import scrape_brand_website
from backend.models.schemas import BrandStyle


BRAND_ANALYSIS_SYSTEM_PROMPT = """You are a senior brand strategist with 20 years of experience in brand voice analysis.

Your job is to analyze raw website content and extract a precise brand style guide.

You must identify:
1. **Tone**: The emotional register (e.g., "warm and approachable", "authoritative and precise", "playful and irreverent")
2. **Voice Characteristics**: 3-5 adjectives describing the writing style
3. **Vocabulary Patterns**: Specific words, phrases, or jargon the brand favors
4. **Messaging Themes**: Core themes the brand repeatedly emphasizes
5. **Sample Phrases**: 3-5 actual phrases from the website that exemplify the brand voice
6. **Do Not Use**: Words or styles that would clash with this brand

Return your analysis as JSON with this exact structure:
{
    "brand_name": "string",
    "tone": "string describing the overall tone",
    "voice_characteristics": ["adj1", "adj2", "adj3"],
    "vocabulary_patterns": ["pattern1", "pattern2"],
    "messaging_themes": ["theme1", "theme2"],
    "sample_phrases": ["phrase1", "phrase2"],
    "do_not_use": ["avoid1", "avoid2"]
}"""


def analyze_brand(brand_url: str) -> BrandStyle:
    """Scrape brand website and analyze its style."""

    # Step 1: Scrape the website
    scraped = scrape_brand_website(brand_url)

    if "error" in scraped and not scraped.get("body_text_samples"):
        return BrandStyle(
            brand_name=brand_url,
            tone="professional and clear",
            voice_characteristics=["professional", "clear", "informative"],
            vocabulary_patterns=[],
            messaging_themes=[],
            sample_phrases=[],
            do_not_use=["slang", "overly casual language"],
            raw_excerpts="Could not scrape website. Using default professional style."
        )

    # Step 2: Compile scraped content for analysis
    content_for_analysis = _compile_scraped_content(scraped)

    # Step 3: Send to LLM for brand analysis
    user_prompt = f"""Analyze the following website content and extract the brand's voice and style:

--- WEBSITE CONTENT ---
{content_for_analysis}
--- END ---

Identify the brand's tone, voice characteristics, vocabulary patterns, messaging themes, 
sample phrases that exemplify their style, and words/styles to avoid."""

    result = call_llm_json(BRAND_ANALYSIS_SYSTEM_PROMPT, user_prompt)

    if result.get("parse_error"):
        # Fallback: use raw LLM response to build a basic style
        return BrandStyle(
            brand_name=scraped.get("brand_name", brand_url),
            tone="professional",
            voice_characteristics=["professional", "clear"],
            raw_excerpts=content_for_analysis[:2000]
        )

    return BrandStyle(
        brand_name=result.get("brand_name", scraped.get("brand_name", "")),
        tone=result.get("tone", "professional"),
        voice_characteristics=result.get("voice_characteristics", []),
        vocabulary_patterns=result.get("vocabulary_patterns", []),
        messaging_themes=result.get("messaging_themes", []),
        sample_phrases=result.get("sample_phrases", []),
        do_not_use=result.get("do_not_use", []),
        raw_excerpts=content_for_analysis[:2000]
    )


def _compile_scraped_content(scraped: dict) -> str:
    """Compile scraped data into a readable format for the LLM."""
    sections = []

    if scraped.get("brand_name"):
        sections.append(f"BRAND/TITLE: {scraped['brand_name']}")

    if scraped.get("meta_description"):
        sections.append(f"META DESCRIPTION: {scraped['meta_description']}")

    if scraped.get("headings"):
        sections.append(f"HEADINGS: {' | '.join(scraped['headings'][:15])}")

    if scraped.get("cta_texts"):
        sections.append(f"CALL-TO-ACTION BUTTONS: {' | '.join(scraped['cta_texts'])}")

    if scraped.get("about_text"):
        sections.append(f"ABOUT PAGE:\n{scraped['about_text'][:1500]}")

    if scraped.get("body_text_samples"):
        body = "\n".join(scraped["body_text_samples"][:12])
        sections.append(f"BODY CONTENT:\n{body[:3000]}")

    return "\n\n".join(sections)