"""
Web scraper for brand website analysis.
Extracts text, headings, meta info, and content samples.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Optional


def scrape_brand_website(url: str) -> dict:
    """
    Scrape a brand website to extract style-relevant content.
    Returns structured data about the brand's web presence.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    result = {
        "brand_name": "",
        "tagline": "",
        "meta_description": "",
        "headings": [],
        "body_text_samples": [],
        "about_text": "",
        "navigation_items": [],
        "cta_texts": [],
        "footer_text": "",
        "page_titles": [],
    }

    try:
        # ── Scrape homepage ──
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        # Brand name from title
        title_tag = soup.find("title")
        if title_tag:
            result["brand_name"] = title_tag.get_text(strip=True)
            result["page_titles"].append(title_tag.get_text(strip=True))

        # Meta description
        meta = soup.find("meta", attrs={"name": "description"})
        if meta:
            result["meta_description"] = meta.get("content", "")

        # OG description as fallback
        og_desc = soup.find("meta", attrs={"property": "og:description"})
        if og_desc and not result["meta_description"]:
            result["meta_description"] = og_desc.get("content", "")

        # Headings
        for tag in ["h1", "h2", "h3"]:
            for h in soup.find_all(tag, limit=10):
                text = h.get_text(strip=True)
                if text and len(text) > 3:
                    result["headings"].append(text)

        # Body text — grab meaningful paragraphs
        for p in soup.find_all("p", limit=30):
            text = p.get_text(strip=True)
            if len(text) > 40:
                result["body_text_samples"].append(text)

        # Navigation items
        nav = soup.find("nav")
        if nav:
            for a in nav.find_all("a", limit=15):
                text = a.get_text(strip=True)
                if text and len(text) < 40:
                    result["navigation_items"].append(text)

        # CTA buttons
        for btn in soup.find_all(["button", "a"], class_=lambda c: c and any(
            k in str(c).lower() for k in ["cta", "btn", "button", "action"]
        ), limit=10):
            text = btn.get_text(strip=True)
            if text and len(text) < 60:
                result["cta_texts"].append(text)

        # Footer
        footer = soup.find("footer")
        if footer:
            result["footer_text"] = footer.get_text(separator=" ", strip=True)[:500]

        # ── Try to scrape /about page ──
        about_text = _try_scrape_subpage(url, ["/about", "/about-us", "/company"], headers)
        if about_text:
            result["about_text"] = about_text

        # ── Try to scrape /blog for style samples ──
        blog_text = _try_scrape_subpage(url, ["/blog", "/news", "/insights"], headers)
        if blog_text:
            result["body_text_samples"].append(f"[FROM BLOG] {blog_text}")

    except requests.RequestException as e:
        result["error"] = f"Failed to scrape {url}: {str(e)}"

    return result


def _try_scrape_subpage(base_url: str, paths: list[str], headers: dict) -> Optional[str]:
    """Try to scrape common subpages for additional content."""
    for path in paths:
        try:
            full_url = urljoin(base_url, path)
            resp = requests.get(full_url, headers=headers, timeout=10)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "lxml")
                paragraphs = []
                for p in soup.find_all("p", limit=15):
                    text = p.get_text(strip=True)
                    if len(text) > 50:
                        paragraphs.append(text)
                if paragraphs:
                    return " ".join(paragraphs[:8])
        except Exception:
            continue
    return None


def scrape_source_url(url: str) -> str:
    """Scrape a source document URL and extract its text content."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        # Remove script and style elements
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()

        text = soup.get_text(separator="\n", strip=True)
        # Clean up excessive whitespace
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines)
    except Exception as e:
        return f"Error scraping URL: {str(e)}"