
## PDF Downloader Script
Description
This script logs into a website, navigates to a page containing PDF documents, and downloads them to a local folder.

### Requirements:
- Python 3.x
- Selenium: Used for automating browser actions.

- Requests: Used for downloading files.
- BeautifulSoup: Used for parsing HTML.
### Installation

#### Install Python packages by running:

```bash
python -m pip install selenium requests beautifulsoup4
```

### Install ChromeDriver (or choose another WebDriver for your browser):

- ChromeDriver: https://sites.google.com/a/chromium.org/chromedriver/
- Ensure it is placed in a directory included in your PATH.
### Configuration
#### Edit the following variables in the script:

- BASE_URL : The base URL of the site you're downloading PDFs from.

- LOGIN_URL: The login page URL.

- DOCS_URL: The URL of the page containing the PDF links.

- USERNAME: Your login username.

- PASSWORD: Your login password.

- DOWNLOAD_FOLDER: The folder where PDFs will be saved.

## How to Use
Run the script:
````bash
python pdf_downloader.py
````

### The script will:
- Login to the site with the provided credentials.
- Navigate to the document page.
- Download all PDF links to the specified folder.

#### Notes
The script disables SSL verification due to the use of verify=False in requests.get(). Use it cautiously, especially on trusted sites.
Ensure that the element IDs (edit-name, edit-pass) match the actual HTML elements on the login page.
