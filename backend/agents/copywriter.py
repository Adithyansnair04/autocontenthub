"""
Creative Copywriter Agent
Transforms the fact sheet into platform-specific content with brand voice alignment
and trend-aware context for timely, resonant output.
"""

from backend.services.llm_client import call_llm
from backend.models.schemas import FactSheet, BrandStyle, TrendContext, ContentPiece, ContentDomain


# ── Context builders ──

def _build_brand_context(brand_style: BrandStyle) -> str:
    """Build brand voice instructions from the analyzed brand style."""
    if not brand_style or not brand_style.tone:
        return "Write in a professional, clear, and engaging tone."

    parts = ["BRAND VOICE REQUIREMENTS:"]
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


def _build_trend_context(trend_context: TrendContext, platform: str = "") -> str:
    """Build trend intelligence context to give the copywriter timely, resonant angles."""
    if not trend_context:
        return ""

    parts = ["CURRENT TREND INTELLIGENCE (use this to make content feel timely and credible):"]

    if trend_context.industry_trends:
        parts.append(f"- Industry Trends RIGHT NOW: {' | '.join(trend_context.industry_trends[:4])}")

    if platform and trend_context.platform_trends.get(platform):
        platform_tips = trend_context.platform_trends[platform]
        parts.append(f"- What's working on this platform NOW: {' | '.join(platform_tips[:3])}")

    if trend_context.dominant_tensions:
        parts.append(f"- Key tensions your audience feels: {' | '.join(trend_context.dominant_tensions[:3])}")

    if trend_context.urgency_signals:
        parts.append(f"- Urgency signals to reference: {' | '.join(trend_context.urgency_signals[:2])}")

    if trend_context.content_angles:
        parts.append(f"- Fresh content angles to consider: {' | '.join(trend_context.content_angles[:3])}")

    if trend_context.trending_vocabulary:
        parts.append(f"- Trending vocabulary to use naturally: {', '.join(trend_context.trending_vocabulary[:5])}")

    if trend_context.avoid_overused_angles:
        parts.append(f"- AVOID these overused angles: {' | '.join(trend_context.avoid_overused_angles[:3])}")

    return "\n".join(parts)


ORIGINALITY_INSTRUCTIONS = """
ORIGINALITY RULES — FOLLOW STRICTLY:
1. NEVER start with "In today's fast-paced world" or any similar cliché opener.
2. NEVER use phrases like "game-changer", "cutting-edge", "revolutionary", "seamless", "leverage", "unlock the power of", "next-gen", "state-of-the-art".
3. DO NOT use generic filler sentences — every sentence must carry specific information or insight.
4. Start with a concrete fact, a compelling statement, or a vivid scenario. Avoid rhetorical questions as hooks.
5. Use active voice exclusively. Prioritize strong verbs over weak verbs + adverbs.
6. Include specific numbers, names, or details from the fact sheet.
7. Write as a knowledgeable human would — with confident personality, not robotic perfection.
8. Each sentence should earn its place — if it could be deleted without losing meaning, delete it.
"""


def generate_linkedin(
    fact_sheet: FactSheet,
    brand_style: BrandStyle,
    target_audience: str,
    trend_context: TrendContext = None,
) -> ContentPiece:
    """Generate a LinkedIn post trend-aware."""
    brand_ctx = _build_brand_context(brand_style)
    audience_ctx = _build_audience_context(target_audience)
    trend_ctx = _build_trend_context(trend_context, platform="linkedin")

    system_prompt = f"""You are a top-tier LinkedIn content strategist known for creating highly engaging, authentic, and concise posts that cut through the noise. Your posts build credibility and spark meaningful conversations.

{brand_ctx}

{audience_ctx}

{trend_ctx}

{ORIGINALITY_INSTRUCTIONS}

LINKEDIN-SPECIFIC RULES FOR PUNCHINESS & AUTHENTICITY:
- Length: 150-300 words (optimized for mobile scrolling and quick consumption).
- PUNCHY HOOK: The very first sentence MUST immediately highlight the single most impressive fact, specific result, or most compelling pain point/opportunity from the fact sheet. It must be a direct, declarative statement — never a question or soft opener. The tone should be urgent, decisive, and state why this matters NOW.
- TREND INTEGRATION: Naturally weave in 1-2 of the current industry trends or platform signals from the trend intelligence above. Make it feel like you're writing from inside the current conversation, not observing it from the outside.
- PARAGRAPH STRUCTURE ("LinkedIn Waterfall"): Each paragraph must be extremely concise, ideally 1 sentence, max 2 sentences. Ensure paragraphs visually break into 1-2 lines for maximum scannability.
- Use frequent line breaks between paragraphs for optimal readability.
- Inject 1-2 highly relevant emojis strategically. Avoid excessive use.
- End with a clear, concise, non-desperate call to action or a thought-provoking question that encourages comments.
- Use 3-5 relevant and specific hashtags at the end.
- Focus on verbs, not adjectives. Replace "is" and "are" with stronger action verbs where possible.
- Sound like a real professional sharing genuine insight, not a marketer broadcasting.
"""

    user_prompt = f"""Write a LinkedIn post based on this fact sheet and trend intelligence:

PRODUCT: {fact_sheet.product_name}
VALUE PROPOSITION: {fact_sheet.value_proposition}
KEY FEATURES: {', '.join(fact_sheet.core_features[:5])}
KEY BENEFITS: {', '.join(fact_sheet.key_benefits[:4])}
SUMMARY: {fact_sheet.raw_summary}

Identify the most impressive fact or benefit and craft a LinkedIn post that starts with an undeniable, urgent hook. Weave in a current industry trend or tension naturally. Maintain the brand voice. Keep every paragraph super short for the 'LinkedIn waterfall' effect."""

    content = call_llm(system_prompt, user_prompt, temperature=0.75)

    return ContentPiece(
        domain=ContentDomain.LINKEDIN,
        title=f"LinkedIn Post: {fact_sheet.product_name}",
        content=content,
        status="draft"
    )


def generate_blog(
    fact_sheet: FactSheet,
    brand_style: BrandStyle,
    target_audience: str,
    trend_context: TrendContext = None,
) -> ContentPiece:
    """Generate a blog post trend-aware."""
    brand_ctx = _build_brand_context(brand_style)
    audience_ctx = _build_audience_context(target_audience)
    trend_ctx = _build_trend_context(trend_context, platform="blog")

    system_prompt = f"""You are a senior content writer who crafts blog posts that are not just informative, but also engaging, authentic, and highly scannable for busy professionals. Your posts establish authority and provide immediate value.

{brand_ctx}

{audience_ctx}

{trend_ctx}

{ORIGINALITY_INSTRUCTIONS}

BLOG-SPECIFIC RULES FOR PUNCHINESS & AUTHENTICITY:
- Length: 500-700 words.
- Structure:
    - Compelling, benefit-driven HEADLINE (not clickbait, but impactful).
    - Hard-hitting HOOK paragraph (1-2 sentences) that establishes immediate relevance or highlights a key problem/solution. No fluff.
    - 3-5 concise BODY SECTIONS with descriptive subheadings (##). Each section should deliver a clear point.
    - Strong CONCLUSION with a single, clear Call to Action.
- TREND INTEGRATION: Open with or reference a current industry trend from the trend intelligence. Frame the product/topic as the response to something the reader already knows is happening. This instantly makes the post feel timely.
- PARAGRAPH STRUCTURE: Keep paragraphs short (2-4 sentences max) for enhanced scannability on mobile. Break up dense text.
- Use strong, active verbs. Avoid unnecessary adjectives and adverbs.
- Focus on conveying actionable insights and specific value, rather than generic descriptions.
- Tone: Authoritative, conversational, and genuinely insightful — like an expert sharing valuable knowledge.
- Format output in clean Markdown."""

    user_prompt = f"""Write a blog post based on this fact sheet and trend intelligence:

PRODUCT: {fact_sheet.product_name}
VALUE PROPOSITION: {fact_sheet.value_proposition}
FEATURES: {chr(10).join('- ' + f for f in fact_sheet.core_features)}
TECHNICAL SPECS: {chr(10).join('- ' + s for s in fact_sheet.technical_specs[:5])}
BENEFITS: {chr(10).join('- ' + b for b in fact_sheet.key_benefits)}
SUMMARY: {fact_sheet.raw_summary}

Craft a compelling and highly scannable blog post. Open by connecting to a current industry trend. Ensure the introduction grabs attention immediately, sections are well-structured with clear subheadings, and paragraphs are concise. Adhere to the brand voice and target audience."""

    content = call_llm(system_prompt, user_prompt, temperature=0.7)

    return ContentPiece(
        domain=ContentDomain.BLOG,
        title=f"Blog Post: {fact_sheet.product_name}",
        content=content,
        status="draft"
    )


def generate_tweet_thread(
    fact_sheet: FactSheet,
    brand_style: BrandStyle,
    target_audience: str,
    trend_context: TrendContext = None,
) -> ContentPiece:
    """Generate a Twitter/X thread trend-aware."""
    brand_ctx = _build_brand_context(brand_style)
    audience_ctx = _build_audience_context(target_audience)
    trend_ctx = _build_trend_context(trend_context, platform="twitter")

    system_prompt = f"""You are a viral Twitter/X power user who crafts threads that are incredibly punchy, authentic, and designed for maximum mobile engagement. Your threads cut through noise, deliver immense value, and get bookmarked/shared repeatedly.

{brand_ctx}

{audience_ctx}

{trend_ctx}

{ORIGINALITY_INSTRUCTIONS}

TWEET THREAD RULES FOR PUNCHINESS & AUTHENTICITY:
- Write exactly 5 tweets in a thread.
- Each tweet MUST be under 280 characters. Be ruthless with character count.
- Format: "1/ ...", "2/ ...", etc.
- TWEET 1 (THE HOOK): A strong, direct, undeniable declarative statement. Present a startling fact, bold claim, or reference a pressing industry tension from the trend intelligence. AVOID ALL QUESTIONS. Make it instantly clear why the reader must click "Show thread."
- TWEETS 2-4: Each tweet delivers one concise, impactful piece of information or specific detail. Use strong verbs. Cut all weak words.
- TWEET 5 (THE TAKEAWAY & CTA): Summarize the core actionable value. Include one clear, concise Call to Action. Add 2 max trending hashtags here only.
- CHARACTER ECONOMY: Ruthlessly eliminate filler words. Favor strong, active verbs over adjectives. Be direct, like a Nike ad.
- EMOJI PLACEMENT: 1-2 relevant emojis per tweet to break up text. Never as a substitute for compelling text.
- TREND REFERENCE: At least one tweet should reference or allude to a current industry trend, giving the thread a "right now" feeling.
- Sound confident, direct, authoritative, and human — not promotional or robotic.
"""

    user_prompt = f"""Write a 5-tweet thread about:

PRODUCT: {fact_sheet.product_name}
VALUE PROPOSITION: {fact_sheet.value_proposition}
KEY FEATURES: {', '.join(fact_sheet.core_features[:4])}
KEY BENEFITS: {', '.join(fact_sheet.key_benefits[:3])}
SUMMARY: {fact_sheet.raw_summary}

Craft a 5-tweet thread adhering strictly to all rules. Start with an exceptionally punchy, direct statement that references a current industry trend or tension. Integrate emojis naturally. Each tweet under 280 chars."""

    content = call_llm(system_prompt, user_prompt, temperature=0.8)

    return ContentPiece(
        domain=ContentDomain.TWEET,
        title=f"Tweet Thread: {fact_sheet.product_name}",
        content=content,
        status="draft"
    )


def generate_email(
    fact_sheet: FactSheet,
    brand_style: BrandStyle,
    target_audience: str,
    trend_context: TrendContext = None,
) -> ContentPiece:
    """Generate an email teaser trend-aware."""
    brand_ctx = _build_brand_context(brand_style)
    audience_ctx = _build_audience_context(target_audience)
    trend_ctx = _build_trend_context(trend_context, platform="email")

    system_prompt = f"""You are a master email copywriter with a track record of 40%+ open rates and high conversion. You craft authentic, direct, and value-driven emails that feel like a personal message, not a mass blast.

{brand_ctx}

{audience_ctx}

{trend_ctx}

{ORIGINALITY_INSTRUCTIONS}

EMAIL-SPECIFIC RULES FOR PUNCHINESS & AUTHENTICITY:
- SUBJECT LINE: Must be compelling, clear, concise (under 60 characters). Focus on urgency, benefit, or curiosity. No emojis. No ALL CAPS.
- PREVIEW TEXT: A crisp extension of the subject line (under 90 characters). Creates further intrigue without being redundant.
- EMAIL BODY STRUCTURE:
  - Use multiple, very short paragraphs (1-2 sentences each) for scannability and a conversational feel. No large blocks of text.
  - Opening hook: Directly reference a current industry trend or urgency signal from the trend intelligence. This immediately signals you're in the same conversation as the reader.
  - Middle: Provide concise evidence, a specific feature, or a compelling use case. Focus on direct value.
  - Include social proof or a concrete (even hypothetical) result if applicable.
  - Clear CTA: End with one single, explicit Call to Action. No ambiguity.
- Tone: Personal, direct, authentic, and value-focused. Write as if speaking to a respected colleague. Avoid overly formal or corporate language.
- Use active voice and strong verbs. Eliminate any weak verbs or filler words.
"""

    user_prompt = f"""Write a concise and impactful email teaser for:

PRODUCT: {fact_sheet.product_name}
VALUE PROPOSITION: {fact_sheet.value_proposition}
KEY BENEFIT: {fact_sheet.key_benefits[0] if fact_sheet.key_benefits else fact_sheet.value_proposition}
AUDIENCE: {fact_sheet.target_audience}
SUMMARY: {fact_sheet.raw_summary}

Craft an email with a compelling SUBJECT, intriguing PREVIEW, and a BODY that opens with a current industry trend or urgency signal, uses short paragraphs, and ends with a clear CTA. Make it feel like a personal, high-value message."""

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
    target_audience: str,
    trend_context: TrendContext = None,
) -> ContentPiece:
    """Generate content for a specific domain/platform."""
    generator = GENERATORS.get(domain)
    if not generator:
        return ContentPiece(domain=domain, content="Unsupported domain", status="error")
    return generator(fact_sheet, brand_style, target_audience, trend_context)