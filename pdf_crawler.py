import os
import time
import requests
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Use environment variables
BASE_URL = os.getenv("BASE_URL")
LOGIN_URL = os.getenv("LOGIN_URL")
DOCS_URL = os.getenv("DOCS_URL")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
DOWNLOAD_FOLDER = os.getenv("DOWNLOAD_FOLDER")


# --- WebDriver Initialization ---
driver = webdriver.Chrome() 

# --- Login to the site ---
driver.get(LOGIN_URL)
time.sleep(2)

# Fill in the ID field
username_field = driver.find_element(By.ID, "edit-name")
username_field.send_keys(USERNAME)

# Fill in the password field
password_field = driver.find_element(By.ID, "edit-pass")
password_field.send_keys(PASSWORD)

# Submit the form
password_field.send_keys(Keys.RETURN)
time.sleep(5)

# --- Go to the documents page ---
driver.get(DOCS_URL)
time.sleep(5)

# Retrieve the loaded HTML
html = driver.page_source
soup = BeautifulSoup(html, "html.parser")

# --- Download the PDFs ---
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
links = soup.find_all("a", href=lambda href: href and href.endswith(".pdf"))

for link in links:
    pdf_url = link.get("href")
    if not pdf_url.startswith("http"):
        pdf_url = BASE_URL + pdf_url
    
    # Decode the URL to get the correct file name
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
        print("Downloaded:", file_path)
    except Exception as e:
        print("Error for", pdf_url, ":", e)

# --- Close the browser ---
driver.quit()
