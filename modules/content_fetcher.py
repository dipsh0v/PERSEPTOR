"""
PERSEPTOR v2.0 - Content Fetcher
Playwright-based dynamic content extraction with EasyOCR fallback.
Supports: images (static + dynamic), SVG, PDF text extraction.
"""

import os
import asyncio
import requests
from io import BytesIO
from PIL import Image
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from PyPDF2 import PdfReader
from typing import List, Optional
from modules.logging_config import get_logger

logger = get_logger("content_fetcher")

# OCR engine selection: try EasyOCR first, fallback to Tesseract
_ocr_engine = None

def _get_ocr_engine():
    """Lazy-load OCR engine. Prefers EasyOCR, falls back to Tesseract."""
    global _ocr_engine
    if _ocr_engine is not None:
        return _ocr_engine

    try:
        import easyocr
        _ocr_engine = ("easyocr", easyocr.Reader(['en'], gpu=False, verbose=False))
        logger.info("OCR engine: EasyOCR initialized")
    except ImportError:
        try:
            import pytesseract
            pytesseract.pytesseract.tesseract_cmd = os.environ.get(
                'TESSERACT_CMD', '/usr/bin/tesseract'
            )
            _ocr_engine = ("tesseract", pytesseract)
            logger.info("OCR engine: Tesseract initialized")
        except ImportError:
            _ocr_engine = ("none", None)
            logger.warning("No OCR engine available (install easyocr or pytesseract)")

    return _ocr_engine


def _ocr_image(image: Image.Image) -> str:
    """Run OCR on a PIL Image using the available engine."""
    engine_name, engine = _get_ocr_engine()

    if engine_name == "easyocr":
        import numpy as np
        img_array = np.array(image.convert("RGB"))
        results = engine.readtext(img_array, detail=0)
        return " ".join(results)
    elif engine_name == "tesseract":
        return engine.image_to_string(image)
    else:
        logger.warning("No OCR engine available, skipping image text extraction")
        return ""


# ─── Playwright-based Dynamic Content Fetching ───────────────────────────────

async def _fetch_dynamic_images_async(url: str, wait_time: int = 5) -> List[str]:
    """Fetch dynamically-loaded image URLs using Playwright."""
    image_urls = []
    try:
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"],
            )
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080},
            )
            page = await context.new_page()

            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)
            except Exception:
                # If networkidle times out, try domcontentloaded
                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=15000)
                except Exception as e:
                    logger.warning(f"Page load failed for {url}: {e}")
                    await browser.close()
                    return []

            # Wait for additional lazy-loaded content
            await page.wait_for_timeout(wait_time * 1000)

            # Scroll down to trigger lazy loading
            await page.evaluate("""
                async () => {
                    const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
                    for (let i = 0; i < 3; i++) {
                        window.scrollBy(0, window.innerHeight);
                        await delay(500);
                    }
                    window.scrollTo(0, 0);
                }
            """)

            await page.wait_for_timeout(1000)

            # Extract all image sources
            images = await page.query_selector_all("img")
            for img in images:
                src = await img.get_attribute("src")
                if src and src.startswith("http"):
                    image_urls.append(src)

                # Check data-src for lazy-loaded images
                data_src = await img.get_attribute("data-src")
                if data_src and data_src.startswith("http"):
                    image_urls.append(data_src)

            await browser.close()

    except ImportError:
        logger.warning("Playwright not installed, falling back to static image extraction")
    except Exception as e:
        logger.error(f"Error fetching dynamic images from {url}: {e}")

    return list(set(image_urls))


def get_dynamic_image_urls(url: str, wait_time: int = 5) -> List[str]:
    """Synchronous wrapper for async Playwright image extraction."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Already in an async context, create a new loop in a thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run, _fetch_dynamic_images_async(url, wait_time)
                )
                return future.result(timeout=60)
        else:
            return loop.run_until_complete(_fetch_dynamic_images_async(url, wait_time))
    except RuntimeError:
        return asyncio.run(_fetch_dynamic_images_async(url, wait_time))
    except Exception as e:
        logger.error(f"Error in dynamic image extraction: {e}")
        return []


# ─── Playwright-based Full Page Content ──────────────────────────────────────

async def _fetch_page_content_async(url: str, wait_time: int = 5) -> dict:
    """
    Fetch full page content using Playwright (JavaScript-rendered).
    Returns: {text, images, title, url}
    """
    result = {"text": "", "images": [], "title": "", "url": url}

    try:
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-features=IsolateOrigins,site-per-process",
                ],
            )
            context = await browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/131.0.0.0 Safari/537.36"
                ),
                viewport={"width": 1920, "height": 1080},
                locale="en-US",
                timezone_id="America/New_York",
            )

            # Hide webdriver flag to bypass bot detection
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            """)

            page = await context.new_page()

            try:
                await page.goto(url, wait_until="networkidle", timeout=45000)
            except Exception:
                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                except Exception as e:
                    logger.warning(f"Page load failed: {e}")
                    await browser.close()
                    return result

            # Try to dismiss cookie consent banners
            try:
                for selector in [
                    "button:has-text('Accept')",
                    "button:has-text('I agree')",
                    "button:has-text('Got it')",
                    "button:has-text('OK')",
                    "[id*='cookie'] button",
                    "[class*='cookie'] button",
                    "[id*='consent'] button",
                ]:
                    btn = await page.query_selector(selector)
                    if btn and await btn.is_visible():
                        await btn.click()
                        await page.wait_for_timeout(1000)
                        break
            except Exception:
                pass

            await page.wait_for_timeout(wait_time * 1000)

            # Extract text content
            result["text"] = await page.evaluate("() => document.body.innerText || ''")
            result["title"] = await page.title()

            # Extract images
            images = await page.query_selector_all("img")
            for img in images:
                src = await img.get_attribute("src")
                if src and src.startswith("http"):
                    result["images"].append(src)
                data_src = await img.get_attribute("data-src")
                if data_src and data_src.startswith("http"):
                    result["images"].append(data_src)

            result["images"] = list(set(result["images"]))
            await browser.close()

    except ImportError:
        logger.warning("Playwright not available for full page content extraction")
    except Exception as e:
        logger.error(f"Error fetching page content: {e}")

    return result


def fetch_page_content(url: str, wait_time: int = 5) -> dict:
    """Synchronous wrapper for full page content extraction."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run, _fetch_page_content_async(url, wait_time)
                )
                return future.result(timeout=60)
        else:
            return loop.run_until_complete(_fetch_page_content_async(url, wait_time))
    except RuntimeError:
        return asyncio.run(_fetch_page_content_async(url, wait_time))
    except Exception as e:
        logger.error(f"Error in page content extraction: {e}")
        return {"text": "", "images": [], "title": "", "url": url}


# ─── Static Image Extraction ─────────────────────────────────────────────────

def extract_image_urls_static(soup: BeautifulSoup, base_url: str) -> List[str]:
    """Extract image URLs from parsed HTML (static, no JS)."""
    image_urls = []
    for img_tag in soup.find_all('img'):
        src = img_tag.get('src') or img_tag.get('data-src')
        if src:
            full_url = urljoin(base_url, src)
            image_urls.append(full_url)
    return list(set(image_urls))


# ─── Image OCR Processing ────────────────────────────────────────────────────

def extract_text_from_images(image_urls: List[str], max_images: int = 30) -> str:
    """Extract text from a list of image URLs using OCR."""
    all_text = []
    processed = 0

    for image_url in image_urls[:max_images]:
        try:
            resp = requests.get(image_url, timeout=15)
            if resp.status_code != 200:
                logger.debug(f"Could not fetch image: {image_url} (status {resp.status_code})")
                continue

            ctype = resp.headers.get("Content-Type", "").lower()

            # Handle SVG
            if "svg" in ctype:
                try:
                    from cairosvg import svg2png
                    png_data = svg2png(bytestring=resp.content)
                    image = Image.open(BytesIO(png_data))
                except ImportError:
                    logger.debug(f"cairosvg not available, skipping SVG: {image_url}")
                    continue
            else:
                image = Image.open(BytesIO(resp.content))

            # Skip very small images (likely icons/decorations)
            width, height = image.size
            if width < 50 or height < 50:
                continue

            text = _ocr_image(image)
            if text and text.strip():
                extracted = f"[IMAGE_URL: {image_url}]\n{text.strip()}"
                all_text.append(extracted)
                processed += 1

        except Exception as e:
            logger.debug(f"Error processing image {image_url}: {e}")

    logger.info(f"OCR processed {processed}/{len(image_urls[:max_images])} images")
    return "\n\n".join(all_text)


# ─── PDF Processing ──────────────────────────────────────────────────────────

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a local PDF file."""
    text = ""
    try:
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        logger.info(f"Extracted text from PDF: {pdf_path} ({len(reader.pages)} pages)")
    except Exception as e:
        logger.error(f"Error processing PDF {pdf_path}: {e}")
    return text


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """Extract text from PDF bytes (for upload support)."""
    text = ""
    try:
        reader = PdfReader(BytesIO(pdf_bytes))
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        logger.info(f"Extracted text from PDF upload ({len(reader.pages)} pages)")
    except Exception as e:
        logger.error(f"Error processing PDF bytes: {e}")
    return text


# ─── Smart URL Fetcher ────────────────────────────────────────────────────────

_FETCH_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
}

def _smart_fetch_url(url: str) -> tuple:
    """
    Fetch URL content with fallback strategy:
    1. requests + BeautifulSoup with proper headers
    2. If text is too short (<200 chars) or HTTP fails, use Playwright for JS-rendered pages
    Returns (text_content, soup, used_playwright)
    """
    soup = None
    text_content = ""
    http_failed = False

    # Step 1: Try standard HTTP fetch with proper headers
    try:
        session = requests.Session()
        session.headers.update(_FETCH_HEADERS)
        resp = session.get(url, timeout=30, allow_redirects=True)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "html.parser")
    except requests.exceptions.RequestException as e:
        # Retry once with SSL verification disabled (some sites have cert issues)
        logger.warning(f"HTTP fetch failed for {url}: {e} — retrying with verify=False")
        try:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            resp = requests.get(url, timeout=30, headers=_FETCH_HEADERS,
                                allow_redirects=True, verify=False)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, "html.parser")
        except requests.exceptions.RequestException as e2:
            logger.warning(f"HTTP retry also failed for {url}: {e2} — will try Playwright")
            http_failed = True

    if soup is None:
        soup = BeautifulSoup("", "html.parser")

    # Remove script/style/nav/footer noise before extracting text
    if not http_failed:
        for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "aside"]):
            tag.decompose()

    import re as _re

    # Try multiple strategies to find the main content area (best match wins)
    best_text = ""

    # Strategy 1: Common article body class names
    _content_classes = [
        "articlebody", "article-body", "article-content",
        "entry-content", "post-body", "post-content",
        "story-body", "content-body", "blog-content",
        "article__body", "articleBody",
    ]
    for cls_name in _content_classes:
        el = soup.find(class_=lambda x: x and cls_name in str(x).lower())
        if el:
            candidate = el.get_text(separator="\n", strip=True)
            if len(candidate) > len(best_text):
                best_text = candidate

    # Strategy 2: <article> or <main> tags
    if len(best_text) < 200:
        for tag_name in ["article", "main"]:
            el = soup.find(tag_name)
            if el:
                candidate = el.get_text(separator="\n", strip=True)
                if len(candidate) > len(best_text):
                    best_text = candidate

    # Strategy 3: Largest <div> with significant text (heuristic)
    if len(best_text) < 200:
        for div in soup.find_all("div"):
            div_text = div.get_text(separator="\n", strip=True)
            if len(div_text) > len(best_text) and len(div_text) > 300:
                # Avoid huge wrapper divs — check text density
                html_len = len(str(div))
                if html_len > 0 and len(div_text) / html_len > 0.15:
                    best_text = div_text

    # Strategy 4: Full page text as last resort
    if len(best_text) < 200:
        best_text = soup.get_text(separator="\n", strip=True)

    text_content = _re.sub(r'\n{3,}', '\n\n', best_text).strip()

    # Step 2: If HTTP failed or text is too short, try Playwright for JS-rendered content
    if http_failed or len(text_content) < 200:
        reason = "HTTP failed" if http_failed else f"only {len(text_content)} chars"
        logger.info(f"Static fetch insufficient ({reason}), trying Playwright...")
        try:
            pw_result = fetch_page_content(url, wait_time=12)
            pw_text = pw_result.get("text", "")
            if len(pw_text) > len(text_content):
                logger.info(f"Playwright got {len(pw_text)} chars (vs {len(text_content)} static)")
                text_content = pw_text
                return text_content, soup, True
        except Exception as e:
            logger.warning(f"Playwright fallback failed: {e}")

    return text_content, soup, False
