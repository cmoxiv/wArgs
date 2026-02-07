#!/usr/bin/env python3
"""Web Scraper CLI example - simplified version for help output."""

from wArgs import wArgs
from pathlib import Path
from typing import Literal

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
        print(f"Scraping {url}")

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
        print(f"Extracting from {url} with selector {selector}")

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
        print(f"Extracting links from {url}")

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
        print(f"Extracting images from {url}")

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
        print(f"Extracting table from {url}")

if __name__ == "__main__":
    WebScraper()
