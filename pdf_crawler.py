import os
import time
import requests
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from dotenv import load_dotenv, find_dotenv

for var in ["BASE_URL", "LOGIN_URL", "DOCS_URL", "USERNAME", "PASSWORD", "DOWNLOAD_FOLDER"]:
    os.environ.pop(var, None)

env_path = find_dotenv()
if not env_path:
    raise FileNotFoundError("⚠️ No .env file found! Check its location.")
load_dotenv(env_path, override=True)

BASE_URL = os.getenv("BASE_URL")
LOGIN_URL = os.getenv("LOGIN_URL")
DOCS_URL = os.getenv("DOCS_URL").split("&page=")[0]
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
DOWNLOAD_FOLDER = os.getenv("DOWNLOAD_FOLDER")

print("🔍 Script starting on:", DOCS_URL)

chrome_options = Options()
chrome_options.add_argument("--incognito")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=chrome_options)

driver.get(LOGIN_URL)
driver.delete_all_cookies()
time.sleep(2)

try:
    username_field = driver.find_element(By.ID, "edit-name")
    username_field.clear()
    username_field.send_keys(USERNAME)

    password_field = driver.find_element(By.ID, "edit-pass")
    password_field.clear()
    password_field.send_keys(PASSWORD)

    password_field.send_keys(Keys.RETURN)
    print("✅ Successfully logged in")
except Exception as e:
    print("❌ Login error:", e)
    driver.quit()
    exit(1)

time.sleep(5)

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def get_pdf_links():
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    pdf_links = set()

    for link in soup.find_all("a", href=True):
        if link["href"].endswith(".pdf"):
            pdf_links.add(link["href"])

    for script in soup.find_all("script"):
        if script.string and ".pdf" in script.string:
            for part in script.string.split('"'):
                if part.endswith(".pdf"):
                    pdf_links.add(part)

    final_links = []
    for pdf_url in pdf_links:
        if not pdf_url.startswith("http"):
            pdf_url = BASE_URL + pdf_url
        final_links.append(pdf_url)

    print(f"📄 {len(final_links)} PDF files found!")
    return final_links

def download_pdfs(pdf_links):
    for pdf_url in pdf_links:
        file_name = os.path.basename(urllib.parse.unquote(pdf_url))
        file_path = os.path.join(DOWNLOAD_FOLDER, file_name)

        try:
            session = requests.Session()
            for cookie in driver.get_cookies():
                session.cookies.set(cookie['name'], cookie['value'])

            r = session.get(pdf_url, stream=True, verify=False)
            r.raise_for_status()
            
            with open(file_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            print("📥 Downloaded:", file_path)
        except Exception as e:
            print("❌ Download error for", pdf_url, ":", e)

def get_media_type(media_url):
    image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg"]
    video_extensions = [".mp4", ".webm", ".avi", ".mov"]
    audio_extensions = [".mp3", ".wav", ".flac", ".aac"]
    document_extensions = [".pdf"]

    if any(media_url.endswith(ext) for ext in image_extensions):
        return "photo"
    elif any(media_url.endswith(ext) for ext in video_extensions):
        return "video"
    elif any(media_url.endswith(ext) for ext in audio_extensions):
        return "audio"
    elif any(media_url.endswith(ext) for ext in document_extensions):
        return "document"
    else:
        return "other"

def download_media(media_url):
    media_type = get_media_type(media_url)
    media_folder = os.path.join(DOWNLOAD_FOLDER, media_type)
    os.makedirs(media_folder, exist_ok=True)
    
    file_name = os.path.basename(urllib.parse.unquote(media_url))
    file_path = os.path.join(media_folder, file_name)

    try:
        session = requests.Session()
        for cookie in driver.get_cookies():
            session.cookies.set(cookie['name'], cookie['value'])

        r = session.get(media_url, stream=True, verify=False)
        r.raise_for_status()
        
        with open(file_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"📥 Downloaded ({media_type}):", file_path)
    except Exception as e:
        print("❌ Download error for", media_url, ":", e)

def explore_media_page(media_url):
    driver.get(media_url)
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    layout_content = soup.find("div", class_="layout-content")
    media_link = None
    
    if layout_content:
        img_tag = layout_content.find("img", src=True)
        if img_tag:
            media_link = img_tag["src"]
    
    if media_link:
        if not media_link.startswith("http"):
            media_link = BASE_URL + media_link
        return media_link
    return None

current_page = 0
while True:
    page_url = f"{DOCS_URL}&page={current_page}"
    print(f"📜 Exploring page {current_page}: {page_url}")

    driver.get(page_url)
    time.sleep(5)
    
    pdf_links = get_pdf_links()
    if pdf_links:
        download_pdfs(pdf_links)

    rows = driver.find_elements(By.XPATH, "//tbody/tr")
    media_links = []
    
    for row in rows:
        try:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) > 2:
                link = cells[2].find_element(By.TAG_NAME, "a")
                media_page_url = link.get_attribute("href")
                media_links.append(media_page_url)
        except Exception as e:
            print(f"❌ Error fetching links: {e}")

    if not media_links:
        print("❌ No data found. Script ending.")
        break

    for media_url in media_links:
        print(f"🔗 Exploring media page: {media_url}")
        full_media_url = explore_media_page(media_url)
        if full_media_url:
            download_media(full_media_url)

    current_page += 1

print("✅ Script finished.")
driver.quit()