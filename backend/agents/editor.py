"""
Editor Agent
Reviews generated content for hallucinations, tone alignment, punchiness, and overall quality.
Can request revisions from the Copywriter.
"""

from backend.services.llm_client import call_llm_json, call_llm
from backend.models.schemas import FactSheet, BrandStyle, ContentPiece, ContentDomain

# Assuming ORIGINALITY_INSTRUCTIONS and platform-specific rules are accessible or re-defined here
# For a full application, you might centralize these or pass them from CreativeCopywriterAgent
# For this example, I'll replicate the core rules to ensure the Editor has them.

ORIGINALITY_INSTRUCTIONS_FOR_EDITOR = """
ORIGINALITY RULES — EDITOR MUST ENSURE STRICT ADHERENCE:
1. NO cliché openers (e.g., "In today's fast-paced world").
2. NO overused phrases (e.g., "game-changer", "cutting-edge", "revolutionary", "seamless", "leverage", "unlock the power of", "next-gen", "state-of-the-art").
3. NO generic filler sentences — every sentence must add specific information or insight.
4. Hook must be a concrete fact, compelling statement, or vivid scenario. NO rhetorical questions.
5. Must use active voice exclusively. Prioritize strong verbs over weak verbs + adverbs.
6. Must include specific numbers, names, or details from the fact sheet.
7. Must sound like a knowledgeable human with confident personality, not robotic perfection.
8. Every sentence must earn its place — delete if it could be removed without losing meaning.
"""

# Replicating platform-specific rules for the Editor to check against
# In a larger system, these might be shared/imported more cleanly.

LINKEDIN_SPECIFIC_RULES_FOR_EDITOR = """
LINKEDIN-SPECIFIC RULES — EDITOR MUST ENSURE STRICT ADHERENCE:
- Length: 150-300 words.
- PUNCHY HOOK: First sentence is an immediate, direct, declarative statement of the most impressive fact/result/pain point. No questions or soft openers. Tone is urgent, decisive.
- PARAGRAPH STRUCTURE ("LinkedIn Waterfall"): Each paragraph 1-2 sentences maximum, visually breaking into 1-2 lines. Frequent line breaks between paragraphs.
- Emojis: 1-2 highly relevant emojis strategically placed. No excessive use.
- CTA: Clear, concise, non-desperate call to action or thought-provoking question at the end.
- Hashtags: 3-5 relevant and specific hashtags at the end.
- Language: Focus on verbs, not adjectives. Avoid corporate jargon unless audience-specific.
"""

TWEET_THREAD_RULES_FOR_EDITOR = """
TWEET THREAD RULES — EDITOR MUST ENSURE STRICT ADHERENCE:
- Exactly 5 tweets in a thread.
- Each tweet < 280 characters. Strict adherence.
- Format: "1/ ...", "2/ ...", etc.
- TWEET 1 (THE HOOK): Strong, direct, undeniable declarative statement (fact, claim, problem). NO QUESTIONS.
- TWEETS 2-4: One concise, impactful piece of info/detail per tweet. Strong verbs.
- TWEET 5 (TAKEAWAY & CTA): Core value summary + single clear CTA.
- CHARACTER ECONOMY: No filler words (e.g., "innovative," "designed to help," "provides," "leverage," "seamless," "cutting-edge," "next-gen," "simply," "truly"). Prioritize strong, active verbs.
- EMOJI PLACEMENT: 1-2 highly relevant emojis per tweet, integrated naturally to break text and enhance readability.
- Language: Plain, conversational. Avoid jargon unless native to audience.
- Hashtags: Max 2 relevant hashtags in ENTIRE thread (ONLY in the last tweet).
"""

BLOG_SPECIFIC_RULES_FOR_EDITOR = """
BLOG-SPECIFIC RULES — EDITOR MUST ENSURE STRICT ADHERENCE:
- Length: 500-700 words.
- Structure: Compelling, benefit-driven HEADLINE. Hard-hitting HOOK paragraph (1-2 sentences). 3-5 concise BODY SECTIONS with descriptive subheadings (##). Strong CONCLUSION with single, clear CTA.
- PARAGRAPH STRUCTURE: Short paragraphs (2-4 sentences max) for scannability.
- Language: Strong, active verbs. Avoid unnecessary adjectives/adverbs. Focus on actionable insights, specific value.
- Content: Incorporate concrete examples or scenarios from fact sheet.
- Tone: Authoritative, conversational, insightful.
"""

EMAIL_SPECIFIC_RULES_FOR_EDITOR = """
EMAIL-SPECIFIC RULES — EDITOR MUST ENSURE STRICT ADHERENCE:
- SUBJECT LINE: Compelling, clear, concise (< 60 chars). Focus: urgency/benefit/curiosity. No emojis/ALL CAPS.
- PREVIEW TEXT: Crisp extension of subject (< 90 chars). Intriguing.
- EMAIL BODY STRUCTURE:
    - Multiple, very short paragraphs (1-2 sentences each). No large blocks of text.
    - Sentence 1 (Hook): Directly address pain point, trend, or undeniable benefit.
    - Subsequent sentences: Concise evidence, specific feature, value.
    - Social proof/concrete results if applicable.
    - Clear CTA: One single, explicit Call to Action. No ambiguity.
- Tone: Personal, direct, authentic, value-focused. As if speaking to a respected colleague.
- Language: Active voice, strong verbs. Eliminate weak verbs/filler.
"""

# ── Main Editor Agent Code ──

REVIEW_SYSTEM_PROMPT = f"""You are a highly discerning and uncompromising Senior Content Editor. Your reputation is built on an eagle-eye for detail, absolute factual accuracy, strict brand voice adherence, and ensuring every piece of content is exceptionally punchy and engaging. You are the final gatekeeper.

You will evaluate content against the provided FACT SHEET, BRAND STYLE, and a detailed set of PLATFORM-SPECIFIC CONTENT RULES.

SCORING CRITERIA:
- 10: Flawless. Publish immediately.
- 9: Excellent. Minor cosmetic tweaks possible but perfectly aligns with all criteria.
- 7-8: Good, but has NOTICEABLE issues. REQUIRES REVISION. No exceptions.
- 1-6: SIGNIFICANT issues. REQUIRES REVISION.

If the content is NOT a 10, the verdict MUST be "NEEDS_REVISION". A score of 9 is the MINIMUM for "APPROVED".

Return ONLY valid JSON:
{{
    "verdict": "APPROVED" or "NEEDS_REVISION",
    "score": 8,
    "has_hallucinations": false,
    "has_tone_issues": false,
    "has_punchiness_issues": false,
    "correction_note": "If NEEDS_REVISION, provide a concise, bulleted list of *exact, actionable changes* needed, referencing specific rules. Be direct and unambiguous. If APPROVED, leave empty."
}}

{ORIGINALITY_INSTRUCTIONS_FOR_EDITOR}
"""

def _get_platform_rules_for_editor(domain: ContentDomain) -> str:
    """Helper to get domain-specific rules for the editor."""
    if domain == ContentDomain.LINKEDIN:
        return LINKEDIN_SPECIFIC_RULES_FOR_EDITOR
    elif domain == ContentDomain.TWEET:
        return TWEET_THREAD_RULES_FOR_EDITOR
    elif domain == ContentDomain.BLOG:
        return BLOG_SPECIFIC_RULES_FOR_EDITOR
    elif domain == ContentDomain.EMAIL:
        return EMAIL_SPECIFIC_RULES_FOR_EDITOR
    return "" # Should not happen with valid domains

def review_content(piece: ContentPiece, fact_sheet: FactSheet, brand_style: BrandStyle) -> dict:
    """Review a content piece against the fact sheet and brand style."""

    platform_rules = _get_platform_rules_for_editor(piece.domain)

    user_prompt = f"""Review this {piece.domain.value} content:

--- CONTENT TO REVIEW ---
{piece.content}

--- FACT SHEET (Source of Truth) ---
Product: {fact_sheet.product_name}
Features: {', '.join(fact_sheet.core_features)}
Benefits: {', '.join(fact_sheet.key_benefits)}
Value Proposition: {fact_sheet.value_proposition}
Summary: {fact_sheet.raw_summary}

--- BRAND STYLE (Tone, Voice, Language Guidelines) ---
Overall Tone: {brand_style.tone}
Voice Characteristics: {', '.join(brand_style.voice_characteristics) if brand_style.voice_characteristics else 'N/A'}
Vocabulary Patterns: {', '.join(brand_style.vocabulary_patterns) if brand_style.vocabulary_patterns else 'N/A'}
Messaging Themes: {', '.join(brand_style.messaging_themes) if brand_style.messaging_themes else 'N/A'}
Sample Phrases: {', '.join(brand_style.sample_phrases) if brand_style.sample_phrases else 'N/A'}
AVOID using (Explicitly Forbidden): {', '.join(brand_style.do_not_use) if brand_style.do_not_use else 'N/A'}

--- PLATFORM-SPECIFIC CONTENT RULES FOR {piece.domain.value.upper()} ---
{platform_rules}

Evaluate the content rigorously against ALL the above criteria.
Focus particularly on the punchiness of the hook, adherence to originality rules, character economy (if applicable), factual accuracy, and brand tone.
If ANY significant issue is found, verdict must be NEEDS_REVISION and score must be < 9.
Provide precise, actionable bullet points in the correction_note if revisions are needed.
"""
    # OPTIMIZATION: Dropped temperature to 0.2 for strict, analytical grading.
    # New boolean 'has_punchiness_issues' added to the expected JSON structure.
    result = call_llm_json(REVIEW_SYSTEM_PROMPT, user_prompt, temperature=0.2)

    if result.get("parse_error"):
        # Fail-deadly. Never auto-approve on a system failure.
        return {
            "verdict": "NEEDS_REVISION",
            "score": 4, # Low score to indicate a critical system issue
            "has_hallucinations": True, # Assume worst if parsing fails
            "has_tone_issues": True,
            "has_punchiness_issues": True, # Assume worst if parsing fails
            "correction_note": "SYSTEM ERROR: Editor failed to parse review. Copywriter, please do a general polish ensuring strict adherence to the Fact Sheet, Brand Voice, and platform rules. Pay special attention to the hook and removing filler words."
        }

    # Ensure verdict aligns with score for strictness
    if result.get("score") < 9 and result.get("verdict") == "APPROVED":
        result["verdict"] = "NEEDS_REVISION"
        if not result["correction_note"]:
            result["correction_note"] = "Score below 9 requires revision. Please review against all guidelines."
    elif result.get("score") >= 9 and result.get("verdict") == "NEEDS_REVISION":
         # If the LLM gives a high score but says NEEDS_REVISION, respect the revision call
         # but ensure a correction_note exists if it doesn't.
        if not result["correction_note"]:
            result["correction_note"] = "High score but needs refinement. Please review against all guidelines."
    
    return result

REVISION_SYSTEM_PROMPT = """You are a highly skilled and precise Copywriter. Your only task is to revise content based on a clear, actionable editor's correction note.

RULES:
1. ADDRESS EVERY SINGLE POINT in the editor's correction note exactly and meticulously.
2. PRESERVE the core message, platform-specific structure, original hooks (unless specifically instructed to change), and trending angles.
3. Your revised content MUST stay strictly factual to the provided context. No new information.
4. Maintain the specified brand voice and target audience.
5. Apply all character economy and punchiness rules from the platform guidelines.
6. Return ONLY the revised content. DO NOT include any intro/outro text, explanations, or notes. Just the final content.
7. Be concise and efficient in your revisions.
"""

def revise_content(
    piece: ContentPiece,
    correction_note: str,
    fact_sheet: FactSheet,
    brand_style: BrandStyle,
    target_audience: str,
) -> ContentPiece:
    """Revise content based on editor feedback."""

    user_prompt = f"""Revise this {piece.domain.value} content:

--- CURRENT CONTENT ---
{piece.content}

--- EDITOR'S URGENT CORRECTION NOTE ---
{correction_note}

--- CORE CONTEXT FOR REVISION ---
Product: {fact_sheet.product_name}
Target Audience: {target_audience}
Brand Tone: {brand_style.tone}
Key features: {', '.join(fact_sheet.core_features[:5])}
Key benefits: {', '.join(fact_sheet.key_benefits[:4])}
Value Proposition: {fact_sheet.value_proposition}

Your revision must directly address the editor's notes while enhancing punchiness and adhering to all brand and platform guidelines.
"""
    # OPTIMIZATION: Lowered temperature to 0.3 for precision editing.
    revised = call_llm(REVISION_SYSTEM_PROMPT, user_prompt, temperature=0.3)

    piece.content = revised
    piece.revision_count += 1
    return piece