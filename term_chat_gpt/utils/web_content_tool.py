import io
import requests
import re

import PyPDF2
from bs4 import BeautifulSoup
from readability import Document
from playwright.sync_api import sync_playwright
from langchain.tools import BaseTool

from term_chat_gpt.utils.logger_config import setup_logger

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
LOGGING_LEVEL = "DEBUG"
LOG = setup_logger(__name__, LOGGING_LEVEL)


class WebContentTool(BaseTool):
    name = "query_webpage"
    description = "Browse a webpage and retrieve the main textual content."

    def _run(self, url: str) -> str:
        """Useful for browsing websites and scraping the text information."""
        LOG.info(f"Extracting content from {url}")
        try:
            with sync_playwright() as p:
                # Launch a headless browser
                browser = p.chromium.launch(headless=True)
                # Create a new browser context
                context = browser.new_context(
                    java_script_enabled=True,
                    user_agent=USER_AGENT,
                )
                # Open a new page
                page = context.new_page()
                # Navigate to the URL
                response = page.goto(url, wait_until="domcontentloaded")
                # Get the page source
                page_source = page.content()
                # Close the browser
                browser.close()
                # Use readability to extract the main content

                doc = Document(page_source)
                # Parse the main content with BeautifulSoup
                soup = BeautifulSoup(doc.summary(), 'html.parser')
                # Remove unwanted elements like scripts and styles
                for tag in soup(['script', 'style']):
                    tag.decompose()
                # Get the text content
                text = soup.get_text()
                return self.format_for_return(text)
        except Exception as e:
            LOG.error(
                f"Failed to load webpage from {url}: {e}. I will retry via requests")
            return self._requests_get(url)

    def format_for_return(self, text):
        text = re.sub(r'\n+', '\n', text)
        paragraphs = text.split("\n")
        paragraphs = [" ".join([t.strip() for t in p.split() if len(t.strip()) > 0])
                      for p in paragraphs]
        return "\n\n".join([p for p in paragraphs if len(p) > 0])

    def _requests_get(self, url) -> str:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.3",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
        }
        response = requests.get(url, headers=headers)

        content_type = response.headers["Content-Type"].lower()
        content = None

        if "application/pdf" in content_type:
            pdf_bytes = response.content
            return self.extract_text_from_pdf(pdf_bytes)
        elif "text/html" in content_type:
            content = response.text

        return content

    def extract_text_from_pdf(self, pdf_data: bytes) -> str:
        with io.BytesIO(pdf_data) as buffer:
            pdf_reader = PyPDF2.PdfReader(buffer)

            text = ""
            for page_num in range(len(pdf_reader.pages)):
                text += pdf_reader.pages[page_num].extract_text()

        return text

    async def _arun(self, url: str) -> str:
        raise NotImplementedError
