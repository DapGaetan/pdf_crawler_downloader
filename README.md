
## PDF Downloader Script
Description
This script logs into a website, navigates to a page containing PDF documents, and downloads them to a local folder.

### Requirements:
- Python 3.x


- Selenium: Used for automating browser actions.

- Requests: Used for downloading files.


- BeautifulSoup: Used for parsing HTML.

- python-dotenv: Used for loading environment variables from a .env file.


- python-dotenv: Used for loading environment variables from a .env file.

### Installation

#### Install Python packages by running:

```bash
python -m pip install selenium requests beautifulsoup4 python-dotenv
python -m pip install selenium requests beautifulsoup4 python-dotenv
```

### Install ChromeDriver (or choose another WebDriver for your browser):

- ChromeDriver: https://sites.google.com/a/chromium.org/chromedriver/


- Ensure it is placed in a directory included in your PATH.


### Configuration

#### Store credentials and settings in a .env file:

Create a `.env` file in the same directory as the script and add:

```
BASE_URL=https://my-url.io
LOGIN_URL=https://my-url.io/user/login
DOCS_URL=https://my-url.io/my-files
USERNAME=jhon.doe
PASSWORD=FrWin98
DOWNLOAD_FOLDER=pdfs/my-files-folder
```

#### Store credentials and settings in a .env file:

Create a `.env` file in the same directory as the script and add:

```
BASE_URL=https://my-url.io
LOGIN_URL=https://my-url.io/user/login
DOCS_URL=https://my-url.io/my-files
USERNAME=jhon.doe
PASSWORD=FrWin98
DOWNLOAD_FOLDER=pdfs/my-files-folder
```

## How to Use
Run the script:
```
python pdf_crawler.py
```

### The script will:
- Load configuration from the `.env` file.

- Log in to the site using the provided credentials.

- Load configuration from the `.env` file.

- Log in to the site using the provided credentials.

- Navigate to the document page.


- Download all PDF links to the specified folder.

#### Notes
The script disables SSL verification due to the use of `verify=False` in `requests.get()`. Use it cautiously, especially on untrusted sites.

Ensure that the element IDs (`edit-name`, `edit-pass`) match the actual HTML elements on the login page.