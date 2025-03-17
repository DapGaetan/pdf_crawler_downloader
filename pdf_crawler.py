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

# --- Load .env file ---
for var in ["BASE_URL", "LOGIN_URL", "DOCS_URL", "USERNAME", "PASSWORD", "DOWNLOAD_FOLDER"]:
    os.environ.pop(var, None)

env_path = find_dotenv()
if not env_path:
    raise FileNotFoundError("⚠️ No .env file found! Check its location.")
load_dotenv(env_path, override=True)

# --- Retrieve variables ---
BASE_URL = os.getenv("BASE_URL")
LOGIN_URL = os.getenv("LOGIN_URL")
DOCS_URL = os.getenv("DOCS_URL").split("&page=")[0]
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
DOWNLOAD_FOLDER = os.getenv("DOWNLOAD_FOLDER")

print("🔍 Starting script on:", DOCS_URL)

# --- Selenium configuration ---
chrome_options = Options()
chrome_options.add_argument("--incognito")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--start-maximized")

# --- Launch browser ---
driver = webdriver.Chrome(options=chrome_options)

# --- Login ---
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
    print("✅ Login successful")
except Exception as e:
    print("❌ Error during login:", e)
    driver.quit()
    exit(1)

time.sleep(5)

# --- Create download folder ---
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# --- Function to get PDF links on a page ---
def get_pdf_links():
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    pdf_links = set()

    # 🔹 1️⃣ PDF links in <a>
    for link in soup.find_all("a", href=True):
        if link["href"].endswith(".pdf"):
            pdf_links.add(link["href"])

    # 🔹 2️⃣ PDF links hidden in JS
    for script in soup.find_all("script"):
        if script.string and ".pdf" in script.string:
            for part in script.string.split('"'):
                if part.endswith(".pdf"):
                    pdf_links.add(part)

    # 🔹 3️⃣ Normalize URLs
    final_links = []
    for pdf_url in pdf_links:
        if not pdf_url.startswith("http"):
            pdf_url = BASE_URL + pdf_url
        final_links.append(pdf_url)

    print(f"📄 {len(final_links)} PDF files found!")
    return final_links

# --- Function to download PDFs ---
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
            print("❌ Error downloading", pdf_url, ":", e)

# --- Explore all pages ---
current_page = 0
while True:
    page_url = f"{DOCS_URL}&page={current_page}"
    print(f"📜 Exploring page {current_page}: {page_url}")

    driver.get(page_url)
    time.sleep(5)

    pdf_links = get_pdf_links()
    
    if not pdf_links:
        print("❌ No data found. Ending script.")
        break

    download_pdfs(pdf_links)
    current_page += 1

print("✅ End of script.")
driver.quit()
