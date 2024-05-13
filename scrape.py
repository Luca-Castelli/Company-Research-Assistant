import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from cache import RedisCache

cache = RedisCache()


# Function to fetch and parse HTML content of a webpage
def parse_page(url):
    cached_content = cache.get(f"html:{url}")
    if cached_content:
        print(f"Using cached HTML for {url}")
        return BeautifulSoup(cached_content, "html.parser")
    try:
        response = requests.get(url)
        if response.status_code == 200:
            cache.set(f"html:{url}", response.content)
            return BeautifulSoup(response.content, "html.parser")
        else:
            print(f"Failed to retrieve {url} with status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"Request failed: {e}")
    return None


# Function to extract internal links from a webpage
def extract_internal_links(soup, base_url):
    internal_links = []
    for link in soup.find_all("a", href=True):
        href = link.get("href")
        absolute_url = urljoin(base_url, href)
        if absolute_url.startswith(base_url):
            internal_links.append(absolute_url)
    return internal_links


# Function to clean HTML text
def clean_html_text(text):
    return re.sub(r"\s+", " ", text).strip()


# Function to scrape text content from an HTML page
def scrape_text_from_html(url):
    cached_text = cache.get(f"text:{url}")
    if cached_text:
        print(f"Using cached text for {url}")
        return cached_text.decode()
    soup = parse_page(url)
    if soup:
        # Decompose unwanted elements
        for element in soup(["script", "style", "header", "footer", "nav"]):
            element.decompose()
        # Extract text from remaining elements
        text_elements = soup.find_all(["p", "h1", "h2", "h3"])
        text = "\n".join(
            clean_html_text(element.get_text())
            for element in text_elements
            if element.get_text().strip()
        )
        cache.set(f"text:{url}", text)
        return text
    return ""


# Main function to crawl the website and scrape text content
def scrape_website_text(base_url, limit=15):
    visited_urls = set()
    text = ""
    queue = [base_url]
    count = 0
    while queue and count < limit:
        url = queue.pop(0)
        if url not in visited_urls:
            print("Scraping:", url)
            visited_urls.add(url)
            page_text = scrape_text_from_html(url)
            text += page_text + "\n"
            internal_links = extract_internal_links(parse_page(url), base_url)
            queue.extend(internal_links)
        count += 1
    return text
