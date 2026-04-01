"""
Creative Copywriter Agent
Transforms the fact sheet into platform-specific content with brand voice alignment.
"""

from backend.services.llm_client import call_llm
from backend.models.schemas import FactSheet, BrandStyle, ContentPiece, ContentDomain


# ── Platform-specific system prompts ──

def _build_brand_context(brand_style: BrandStyle) -> str:
    """Build brand voice instructions from the analyzed brand style."""
    if not brand_style or not brand_style.tone:
        return "Write in a professional, clear, and engaging tone."

    parts = [f"BRAND VOICE REQUIREMENTS:"]
    parts.append(f"- Overall Tone: {brand_style.tone}")

    if brand_style.voice_characteristics:
        parts.append(f"- Voice Traits: {', '.join(brand_style.voice_characteristics)}")

    if brand_style.vocabulary_patterns:
        parts.append(f"- Use vocabulary patterns like: {', '.join(brand_style.vocabulary_patterns[:5])}")

    if brand_style.messaging_themes:
        parts.append(f"- Emphasize these themes: {', '.join(brand_style.messaging_themes[:5])}")

    if brand_style.sample_phrases:
        parts.append(f"- Style reference phrases from the brand: {' | '.join(brand_style.sample_phrases[:3])}")

    if brand_style.do_not_use:
        parts.append(f"- AVOID using: {', '.join(brand_style.do_not_use)}")

    return "\n".join(parts)


def _build_audience_context(target_audience: str) -> str:
    """Build audience-specific instructions."""
    return f"""TARGET AUDIENCE: {target_audience}
Tailor your language, examples, and level of technical detail specifically for this audience.
Speak to their pain points, aspirations, and the language they use."""


ORIGINALITY_INSTRUCTIONS = """
ORIGINALITY RULES — FOLLOW STRICTLY:
1. NEVER start with "In today's fast-paced world" or any similar cliché opener
2. NEVER use phrases like "game-changer", "cutting-edge", "revolutionary", "seamless", "leverage", "unlock the power of"
3. DO NOT use generic filler sentences — every sentence must carry specific information or insight
4. Start with a concrete fact, a provocative question, or a vivid scenario
5. Use active voice exclusively
6. Include specific numbers, names, or details from the fact sheet
7. Write as a knowledgeable human would — with occasional personality, not robotic perfection
8. Each sentence should earn its place — if it could be deleted without losing meaning, delete it
"""


def generate_linkedin(fact_sheet: FactSheet, brand_style: BrandStyle, target_audience: str) -> ContentPiece:
    """Generate a LinkedIn post."""
    brand_ctx = _build_brand_context(brand_style)
    audience_ctx = _build_audience_context(target_audience)

    system_prompt = f"""You are a LinkedIn content strategist who writes posts that get genuine engagement — not vanity metrics.

{brand_ctx}

{audience_ctx}

{ORIGINALITY_INSTRUCTIONS}

LINKEDIN-SPECIFIC RULES:
- Length: 150-300 words (the sweet spot for LinkedIn)
- Open with a hook that stops the scroll — a bold statement, a surprising stat, or a relatable scenario
- Use short paragraphs (1-2 sentences max)
- Include line breaks for readability
- End with a clear but non-desperate call to action or thought-provoking question
- Use 3-5 relevant hashtags at the end
- DO NOT use excessive emojis (max 2-3 total, placed naturally)
- Sound like a real professional sharing genuine insight, not a marketer broadcasting"""

    user_prompt = f"""Write a LinkedIn post based on this fact sheet:

PRODUCT: {fact_sheet.product_name}
VALUE PROPOSITION: {fact_sheet.value_proposition}
KEY FEATURES: {', '.join(fact_sheet.core_features[:5])}
KEY BENEFITS: {', '.join(fact_sheet.key_benefits[:4])}
SUMMARY: {fact_sheet.raw_summary}

Write the LinkedIn post now. Make it original, specific, and genuinely useful to the reader."""

    content = call_llm(system_prompt, user_prompt, temperature=0.75)

    return ContentPiece(
        domain=ContentDomain.LINKEDIN,
        title=f"LinkedIn Post: {fact_sheet.product_name}",
        content=content,
        status="draft"
    )


def generate_blog(fact_sheet: FactSheet, brand_style: BrandStyle, target_audience: str) -> ContentPiece:
    """Generate a blog post."""
    brand_ctx = _build_brand_context(brand_style)
    audience_ctx = _build_audience_context(target_audience)

    system_prompt = f"""You are a senior content writer who creates blog posts that people actually read and share.

{brand_ctx}

{audience_ctx}

{ORIGINALITY_INSTRUCTIONS}

BLOG-SPECIFIC RULES:
- Length: 500-700 words
- Structure: Compelling headline → Hook paragraph → 2-3 body sections with subheadings → Conclusion with CTA
- The headline must be specific and benefit-driven (not clickbait)
- First paragraph must establish WHY the reader should care within 2 sentences
- Use subheadings (##) to break up sections
- Include at least one concrete example or scenario
- Conclude with a specific next step, not a vague "learn more"
- Tone: Authoritative but approachable — like explaining to a smart colleague
- Format output in clean Markdown"""

    user_prompt = f"""Write a blog post based on this fact sheet:

PRODUCT: {fact_sheet.product_name}
VALUE PROPOSITION: {fact_sheet.value_proposition}
FEATURES: {chr(10).join('- ' + f for f in fact_sheet.core_features)}
TECHNICAL SPECS: {chr(10).join('- ' + s for s in fact_sheet.technical_specs[:5])}
BENEFITS: {chr(10).join('- ' + b for b in fact_sheet.key_benefits)}
SUMMARY: {fact_sheet.raw_summary}

Write the complete blog post now in Markdown format."""

    content = call_llm(system_prompt, user_prompt, temperature=0.7)

    return ContentPiece(
        domain=ContentDomain.BLOG,
        title=f"Blog Post: {fact_sheet.product_name}",
        content=content,
        status="draft"
    )


def generate_tweet_thread(fact_sheet: FactSheet, brand_style: BrandStyle, target_audience: str) -> ContentPiece:
    """Generate a Twitter/X thread."""
    brand_ctx = _build_brand_context(brand_style)
    audience_ctx = _build_audience_context(target_audience)

    system_prompt = f"""You are a Twitter/X power user who crafts threads that get bookmarked and shared.

{brand_ctx}

{audience_ctx}

{ORIGINALITY_INSTRUCTIONS}

TWEET THREAD RULES:
- Write exactly 5 tweets in a thread
- Each tweet MUST be under 280 characters
- Format: "1/ ...", "2/ ...", etc.
- Tweet 1: The hook — make it impossible to not click "Show thread"
- Tweets 2-4: One key insight/feature per tweet with a specific detail
- Tweet 5: The takeaway + CTA
- Use plain language, no jargon unless your audience expects it
- Max 2 hashtags in the entire thread (only in the last tweet)
- Sound confident and direct, not promotional"""

    user_prompt = f"""Write a 5-tweet thread about:

PRODUCT: {fact_sheet.product_name}
VALUE PROPOSITION: {fact_sheet.value_proposition}
KEY FEATURES: {', '.join(fact_sheet.core_features[:4])}
KEY BENEFITS: {', '.join(fact_sheet.key_benefits[:3])}

Write the 5-tweet thread now. Each tweet must be under 280 characters."""

    content = call_llm(system_prompt, user_prompt, temperature=0.8)

    return ContentPiece(
        domain=ContentDomain.TWEET,
        title=f"Tweet Thread: {fact_sheet.product_name}",
        content=content,
        status="draft"
    )


def generate_email(fact_sheet: FactSheet, brand_style: BrandStyle, target_audience: str) -> ContentPiece:
    """Generate an email teaser."""
    brand_ctx = _build_brand_context(brand_style)
    audience_ctx = _build_audience_context(target_audience)

    system_prompt = f"""You are an email copywriter with a 40%+ open rate track record.

{brand_ctx}

{audience_ctx}

{ORIGINALITY_INSTRUCTIONS}

EMAIL-SPECIFIC RULES:
- Write a SUBJECT LINE (compelling, under 60 characters, no ALL CAPS)
- Write a PREVIEW TEXT (the snippet shown in inbox, under 90 characters)
- Write the EMAIL BODY: 1 paragraph (3-5 sentences)
  - Sentence 1: Acknowledge a pain point or recent development
  - Sentence 2-3: Present the solution with one specific detail
  - Sentence 4: Social proof or concrete result if available
  - Sentence 5: Clear CTA (one single action)
- Format:
  SUBJECT: ...
  PREVIEW: ...
  BODY:
  ...
- Sound personal, like a 1-on-1 message, not a mass blast"""

    user_prompt = f"""Write an email teaser for:

PRODUCT: {fact_sheet.product_name}
VALUE PROPOSITION: {fact_sheet.value_proposition}
KEY BENEFIT: {fact_sheet.key_benefits[0] if fact_sheet.key_benefits else fact_sheet.value_proposition}
AUDIENCE: {fact_sheet.target_audience}

Write the email now with SUBJECT, PREVIEW, and BODY sections."""

    content = call_llm(system_prompt, user_prompt, temperature=0.7)

    return ContentPiece(
        domain=ContentDomain.EMAIL,
        title=f"Email: {fact_sheet.product_name}",
        content=content,
        status="draft"
    )


# ── Main dispatcher ──

GENERATORS = {
    ContentDomain.LINKEDIN: generate_linkedin,
    ContentDomain.BLOG: generate_blog,
    ContentDomain.TWEET: generate_tweet_thread,
    ContentDomain.EMAIL: generate_email,
}


def generate_content(
    domain: ContentDomain,
    fact_sheet: FactSheet,
    brand_style: BrandStyle,
    target_audience: str
) -> ContentPiece:
    """Generate content for a specific domain/platform."""
    generator = GENERATORS.get(domain)
    if not generator:
        return ContentPiece(domain=domain, content="Unsupported domain", status="error")
    return generator(fact_sheet, brand_style, target_audience)