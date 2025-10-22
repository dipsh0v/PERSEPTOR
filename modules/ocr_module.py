import time
import requests
import pytesseract
from PIL import Image
from io import BytesIO
from cairosvg import svg2png
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PyPDF2 import PdfReader
import os

# Use environment variable for tesseract path, fallback to common locations
pytesseract.pytesseract.tesseract_cmd = os.environ.get('TESSERACT_CMD', '/usr/bin/tesseract')

def get_dynamic_image_urls(url, wait_time=5):
    print("[*] Loading dynamic images, starting Selenium...")
    image_urls = []
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Use environment variable for Chrome binary path
    chrome_bin = os.environ.get('CHROME_BIN', '/usr/bin/chromium')
    if chrome_bin:
        chrome_options.binary_location = chrome_bin

    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        time.sleep(wait_time)
        images = driver.find_elements("tag name", "img")
        for img in images:
            src = img.get_attribute("src")
            if src and src.startswith("http"):
                image_urls.append(src)
        driver.quit()
    except Exception as ex:
        print(f"[!] Error retrieving dynamic images from {url}: {ex}")
    return list(set(image_urls))

def extract_image_urls_static(soup: BeautifulSoup, base_url: str):
    image_urls = []
    for img_tag in soup.find_all('img'):
        if 'src' in img_tag.attrs:
            img_url = img_tag['src']
            full_url = urljoin(base_url, img_url)
            image_urls.append(full_url)
    return list(set(image_urls))

def extract_text_from_images(image_urls):
    all_text = []
    for image_url in image_urls:
        print(f"[*] Processing image: {image_url}")
        try:
            resp = requests.get(image_url, timeout=10)
            if resp.status_code == 200:
                ctype = resp.headers.get("Content-Type", "").lower()
                if "svg" in ctype:
                    png_data = svg2png(bytestring=resp.content)
                    image = Image.open(BytesIO(png_data))
                else:
                    image = Image.open(BytesIO(resp.content))
                text = pytesseract.image_to_string(image)
                if text.strip():
                    extracted = f"[IMAGE_URL: {image_url}]\n{text.strip()}"
                    all_text.append(extracted)
            else:
                print(f"[!] Could not fetch image: {image_url} (status {resp.status_code})")
        except Exception as ex:
            print(f"[!] Error processing image {image_url}: {ex}")
    return "\n\n".join(all_text)

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    except Exception as e:
        print(f"[!] Error processing PDF: {pdf_path} - {e}")
    return text
