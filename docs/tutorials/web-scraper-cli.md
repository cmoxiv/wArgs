# Building a Web Scraper CLI

Create a powerful web scraping tool with wArgs for extracting data from websites, handling pagination, and exporting results.

## Overview

Build a CLI that can:
- Scrape web pages with custom selectors
- Handle pagination automatically
- Extract structured data (links, images, text)
- Export to JSON, CSV, or Markdown
- Respect robots.txt and rate limiting
- Handle authentication and cookies

**Prerequisites:**
- Python 3.8+
- wArgs: `pip install git+https://github.com/cmoxiv/wArgs.git`
- BeautifulSoup4: `pip install beautifulsoup4`
- Requests: `pip install requests`

## Complete Implementation

```python
from wArgs import wArgs
from pathlib import Path
from typing import Literal
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import csv
import time
from dataclasses import dataclass, asdict

@dataclass
class ScrapedItem:
    """Represents a scraped item."""
    url: str
    title: str
    content: str
    links: list[str]
    images: list[str]

@wArgs
class WebScraper:
    """Web scraping CLI tool with export capabilities."""

    def __init__(
        self,
        user_agent: str = "wArgs-Scraper/1.0",
        timeout: int = 30,
        delay: float = 1.0,
        verbose: bool = False,
    ):
        """Initialize web scraper.

        Args:
            user_agent: User agent string for requests
            timeout: Request timeout in seconds
            delay: Delay between requests (rate limiting)
            verbose: Show detailed output
        """
        self.user_agent = user_agent
        self.timeout = timeout
        self.delay = delay
        self.verbose = verbose
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})

    def scrape(
        self,
        url: str,
        output: Path,
        format: Literal["json", "csv", "md"] = "json",
        max_pages: int = 1,
    ):
        """Scrape a website and save results.

        Args:
            url: Starting URL to scrape
            output: Output file path
            format: Export format (json, csv, md)
            max_pages: Maximum pages to scrape
        """
        items = []
        current_url = url

        for page_num in range(max_pages):
            if self.verbose:
                print(f"\nScraping page {page_num + 1}/{max_pages}: {current_url}")

            # Scrape current page
            item = self._scrape_page(current_url)
            if item:
                items.append(item)

            # Find next page link (common pagination patterns)
            next_url = self._find_next_page(current_url, item)
            if not next_url or page_num + 1 >= max_pages:
                break

            current_url = next_url
            time.sleep(self.delay)

        # Export results
        self._export(items, output, format)
        print(f"\n✓ Scraped {len(items)} page(s)")
        print(f"✓ Saved to {output}")

    def extract(
        self,
        url: str,
        selector: str,
        attribute: str | None = None,
    ):
        """Extract specific data using CSS selector.

        Args:
            url: URL to scrape
            selector: CSS selector for elements
            attribute: HTML attribute to extract (default: text content)
        """
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        elements = soup.select(selector)

        print(f"\nFound {len(elements)} element(s) matching '{selector}':\n")

        for i, elem in enumerate(elements[:20], 1):  # Limit to 20
            if attribute:
                value = elem.get(attribute, "")
            else:
                value = elem.get_text(strip=True)

            print(f"{i}. {value}")

        if len(elements) > 20:
            print(f"\n... and {len(elements) - 20} more")

    def links(
        self,
        url: str,
        internal_only: bool = False,
        output: Path | None = None,
    ):
        """Extract all links from a page.

        Args:
            url: URL to scrape
            internal_only: Only include internal links
            output: Optional file to save links
        """
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        base_domain = urlparse(url).netloc

        links = []
        for a_tag in soup.find_all("a", href=True):
            href = urljoin(url, a_tag["href"])

            # Filter internal/external
            if internal_only and urlparse(href).netloc != base_domain:
                continue

            links.append(href)

        # Remove duplicates and sort
        links = sorted(set(links))

        print(f"\nFound {len(links)} {'internal ' if internal_only else ''}link(s):\n")

        for link in links[:50]:  # Show first 50
            print(f"  • {link}")

        if len(links) > 50:
            print(f"\n... and {len(links) - 50} more")

        # Save to file if requested
        if output:
            output.write_text("\n".join(links))
            print(f"\n✓ Saved {len(links)} links to {output}")

    def images(
        self,
        url: str,
        download_dir: Path | None = None,
    ):
        """Extract and optionally download images.

        Args:
            url: URL to scrape
            download_dir: Directory to download images (optional)
        """
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        images = []

        for img in soup.find_all("img", src=True):
            src = urljoin(url, img["src"])
            alt = img.get("alt", "")
            images.append({"src": src, "alt": alt})

        print(f"\nFound {len(images)} image(s):\n")

        for i, img in enumerate(images[:20], 1):
            print(f"{i}. {img['src']}")
            if img["alt"]:
                print(f"   Alt: {img['alt']}")

        # Download images if directory specified
        if download_dir:
            download_dir.mkdir(parents=True, exist_ok=True)

            for i, img in enumerate(images, 1):
                try:
                    img_response = self.session.get(img["src"], timeout=self.timeout)
                    img_response.raise_for_status()

                    # Extract filename from URL
                    filename = Path(urlparse(img["src"]).path).name or f"image_{i}.jpg"
                    file_path = download_dir / filename

                    file_path.write_bytes(img_response.content)

                    if self.verbose:
                        print(f"Downloaded: {filename}")

                    time.sleep(self.delay)

                except Exception as e:
                    if self.verbose:
                        print(f"Failed to download {img['src']}: {e}")

            print(f"\n✓ Downloaded {len(images)} images to {download_dir}")

    def table(
        self,
        url: str,
        output: Path,
        table_index: int = 0,
    ):
        """Extract HTML table data to CSV.

        Args:
            url: URL containing the table
            output: Output CSV file
            table_index: Index of table to extract (0-based)
        """
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        tables = soup.find_all("table")

        if not tables:
            print("No tables found on page")
            return

        if table_index >= len(tables):
            print(f"Error: Only {len(tables)} table(s) found")
            return

        table = tables[table_index]

        # Extract headers
        headers = []
        for th in table.find_all("th"):
            headers.append(th.get_text(strip=True))

        # Extract rows
        rows = []
        for tr in table.find_all("tr"):
            cells = tr.find_all(["td", "th"])
            if cells:
                row = [cell.get_text(strip=True) for cell in cells]
                rows.append(row)

        # Write to CSV
        with output.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if headers:
                writer.writerow(headers)
            writer.writerows(rows)

        print(f"\n✓ Extracted table with {len(rows)} rows to {output}")

    def _scrape_page(self, url: str) -> ScrapedItem | None:
        """Scrape a single page."""
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Extract title
            title = soup.find("title")
            title_text = title.get_text(strip=True) if title else ""

            # Extract main content
            # Try common content selectors
            content_elem = (
                soup.find("article")
                or soup.find("main")
                or soup.find("div", class_="content")
                or soup.body
            )
            content = content_elem.get_text(strip=True) if content_elem else ""

            # Extract links
            links = [urljoin(url, a["href"]) for a in soup.find_all("a", href=True)]

            # Extract images
            images = [urljoin(url, img["src"]) for img in soup.find_all("img", src=True)]

            return ScrapedItem(
                url=url,
                title=title_text,
                content=content[:500],  # Truncate for demo
                links=list(set(links)),
                images=list(set(images)),
            )

        except Exception as e:
            if self.verbose:
                print(f"Error scraping {url}: {e}")
            return None

    def _find_next_page(self, current_url: str, item: ScrapedItem) -> str | None:
        """Find next page link from common pagination patterns."""
        for link in item.links:
            # Common pagination patterns
            if any(x in link.lower() for x in ["next", "page=", "p="]):
                return link
        return None

    def _export(self, items: list[ScrapedItem], output: Path, format: str):
        """Export scraped items to file."""
        if format == "json":
            data = [asdict(item) for item in items]
            output.write_text(json.dumps(data, indent=2))

        elif format == "csv":
            with output.open("w", newline="", encoding="utf-8") as f:
                if items:
                    fieldnames = ["url", "title", "content", "links", "images"]
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()

                    for item in items:
                        row = asdict(item)
                        row["links"] = "; ".join(row["links"][:5])
                        row["images"] = "; ".join(row["images"][:5])
                        writer.writerow(row)

        elif format == "md":
            lines = ["# Scraped Content\n"]
            for item in items:
                lines.append(f"## {item.title}\n")
                lines.append(f"**URL**: {item.url}\n")
                lines.append(f"**Content**: {item.content}\n")
                lines.append(f"**Links**: {len(item.links)}\n")
                lines.append(f"**Images**: {len(item.images)}\n\n")

            output.write_text("\n".join(lines))

if __name__ == "__main__":
    WebScraper()
```


## CLI Help Output

```
$ python webscraper.py --help
usage: webscraper.py [-h] [--user-agent USER_AGENT] [--timeout TIMEOUT]
                     [--delay DELAY] [--verbose]
                     {extract,images,links,scrape,table} ...

Web scraping CLI tool with export capabilities.

positional arguments:
  {extract,images,links,scrape,table}
    extract             Extract specific data using CSS selector.
    images              Extract and optionally download images.
    links               Extract all links from a page.
    scrape              Scrape a website and save results.
    table               Extract HTML table data to CSV.

options:
  -h, --help            show this help message and exit
  --user-agent USER_AGENT
                        User agent string for requests (default: 'wArgs-Scraper/1.0')
  --timeout TIMEOUT     Request timeout in seconds (default: 30)
  --delay DELAY         Delay between requests (rate limiting) (default: 1.0)
  --verbose             Show detailed output (default: False)
```

## Usage Examples

### Scrape a website
```bash
$ python scraper.py scrape \
  --scrape-url "https://example.com" \
  --scrape-output results.json \
  --scrape-max-pages 3

Scraping page 1/3: https://example.com
Scraping page 2/3: https://example.com/page2
Scraping page 3/3: https://example.com/page3

✓ Scraped 3 page(s)
✓ Saved to results.json
```

### Extract specific data
```bash
$ python scraper.py extract \
  --extract-url "https://example.com" \
  --extract-selector "h2.title"

Found 15 element(s) matching 'h2.title':

1. First Article Title
2. Second Article Title
3. Third Article Title
...
```

### Extract all links
```bash
$ python scraper.py links \
  --links-url "https://example.com" \
  --links-internal-only \
  --links-output links.txt

Found 42 internal link(s):

  • https://example.com/about
  • https://example.com/contact
  • https://example.com/products
  ...

✓ Saved 42 links to links.txt
```

### Download images
```bash
$ python scraper.py --WebScraper-verbose images \
  --images-url "https://example.com/gallery" \
  --images-download-dir ./images

Found 25 image(s):

1. https://example.com/img/photo1.jpg
2. https://example.com/img/photo2.jpg
...

Downloaded: photo1.jpg
Downloaded: photo2.jpg
...

✓ Downloaded 25 images to ./images
```

### Extract table to CSV
```bash
$ python scraper.py table \
  --table-url "https://example.com/data" \
  --table-output data.csv \
  --table-table-index 0

✓ Extracted table with 100 rows to data.csv
```

## Advanced Features

### Add authentication
```python
def login(self, username: str, password: str, login_url: str):
    """Login to website with credentials.

    Args:
        username: Username
        password: Password
        login_url: Login page URL
    """
    response = self.session.post(
        login_url,
        data={"username": username, "password": password}
    )

    if response.ok:
        print("✓ Logged in successfully")
    else:
        print("✗ Login failed")
```

### Respect robots.txt
```python
from urllib.robotparser import RobotFileParser

def _can_fetch(self, url: str) -> bool:
    """Check if URL can be fetched per robots.txt."""
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

    rp = RobotFileParser()
    rp.set_url(robots_url)
    rp.read()

    return rp.can_fetch(self.user_agent, url)
```

### Handle JavaScript (with Selenium)
```python
from selenium import webdriver
from selenium.webdriver.common.by import By

def scrape_js(self, url: str, wait_selector: str):
    """Scrape JavaScript-rendered content.

    Args:
        url: URL to scrape
        wait_selector: CSS selector to wait for
    """
    driver = webdriver.Chrome()
    driver.get(url)

    # Wait for dynamic content
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector))
    )

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    # Process soup...
```

## Complete Example

See [complete scraper example](https://github.com/cmoxiv/wArgs/tree/main/examples/use-cases/webscraper) with:
- Async scraping with asyncio
- Progress bars
- Error retry logic
- Custom headers and cookies
- Proxy support
- Data validation

## Best Practices

1. **Respect robots.txt** - Always check before scraping
2. **Rate limiting** - Use delays between requests
3. **User agent** - Identify your scraper properly
4. **Error handling** - Handle network errors gracefully
5. **Legal compliance** - Only scrape public data, respect ToS

## Related

- [[Building a Database CLI]] - Store scraped data
- [[Building a File Manager CLI]] - Organize downloads
- [Official Examples](https://cmoxiv.github.io/wArgs/examples/)
