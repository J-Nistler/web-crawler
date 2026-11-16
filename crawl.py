import asyncio
from urllib.parse import urljoin, urlsplit

import aiohttp
from bs4 import BeautifulSoup, Tag


def normalize_url(url):
    parts = urlsplit(url)
    host = parts.netloc.lower()
    path = parts.path.rstrip("/")
    return f"{host}{path}"


def get_heading_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    h_tag = soup.find("h1") or soup.find("h2")
    return h_tag.get_text(strip=True) if isinstance(h_tag, Tag) else ""


def get_first_paragraph_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    main = soup.find("main")
    p_tag = main.find("p") if isinstance(main, Tag) else None
    if p_tag is None:
        p_tag = soup.find("p")
    return p_tag.get_text(strip=True) if isinstance(p_tag, Tag) else ""


def get_urls_from_html(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    urls = []
    for a_tag in soup.find_all("a"):
        if not isinstance(a_tag, Tag):
            continue
        href = a_tag.get("href")
        if isinstance(href, str) and href.strip():
            urls.append(urljoin(base_url, href.strip()))
    return urls


def get_images_from_html(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    images = []
    for img_tag in soup.find_all("img"):
        if not isinstance(img_tag, Tag):
            continue
        src = img_tag.get("src")
        if isinstance(src, str) and src.strip():
            images.append(urljoin(base_url, src.strip()))
    return images


def extract_page_data(html: str, page_url: str) -> dict:
    return {
        "url": page_url,
        "heading": get_heading_from_html(html),
        "first_paragraph": get_first_paragraph_from_html(html),
        "outgoing_links": get_urls_from_html(html, page_url),
        "image_urls": get_images_from_html(html, page_url),
    }



class AsyncCrawler:
    def __init__(self, base_url: str, max_concurrency: int = 3, max_pages: int = 10):
        self.base_url = base_url
        self.base_domain = urlsplit(base_url).netloc.lower()
        self.page_data: dict[str, dict] = {}
        self.visited: set[str] = set()
        self.lock = asyncio.Lock()
        self.max_concurrency = max_concurrency
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.session: aiohttp.ClientSession | None = None
        self.max_pages = max_pages
        self.should_stop = False
        self.all_tasks: set[asyncio.Task] = set()

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={"User-Agent": "BootCrawler/1.0"},
            timeout=aiohttp.ClientTimeout(total=10),
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session is not None:
            await self.session.close()

    async def add_page_visit(self, normalized_url: str) -> bool:
        async with self.lock:
            if self.should_stop:
                return False
            if len(self.visited) >= self.max_pages:
                # Stop scheduling new pages; fetches already underway finish normally.
                self.should_stop = True
                print("Reached maximum number of pages to crawl.")
                return False
            if normalized_url in self.visited:
                return False
            self.visited.add(normalized_url)
            return True

    async def get_html(self, url: str) -> str:
        if self.session is None:
            raise RuntimeError("AsyncCrawler must be used in an 'async with' block")
        async with self.session.get(url) as response:
            if response.status >= 400:
                raise Exception(f"HTTP error {response.status} fetching {url}")
            content_type = response.headers.get("content-type", "")
            if "text/html" not in content_type.lower():
                raise Exception(f"expected text/html from {url}, got {content_type!r}")
            return await response.text()

    async def crawl_page(self, current_url: str) -> None:
        if self.should_stop:
            return

        if urlsplit(current_url).netloc.lower() != self.base_domain:
            return

        normalized_url = normalize_url(current_url)
        if not await self.add_page_visit(normalized_url):
            return

        async with self.semaphore:
            print(f"crawling {current_url}")
            try:
                html = await self.get_html(current_url)
            except Exception as e:
                print(f"  error fetching {current_url}: {e!r}")
                return

        data = extract_page_data(html, current_url)
        async with self.lock:
            self.page_data[normalized_url] = data

        tasks = []
        for next_url in data["outgoing_links"]:
            if self.should_stop:
                break
            task = asyncio.create_task(self.crawl_page(next_url))
            self.all_tasks.add(task)
            tasks.append(task)

        try:
            await asyncio.gather(*tasks)
        finally:
            for task in tasks:
                self.all_tasks.discard(task)

    async def crawl(self) -> dict[str, dict]:
        await self.crawl_page(self.base_url)
        return self.page_data


async def crawl_site_async(
    base_url: str, max_concurrency: int = 3, max_pages: int = 10
) -> dict[str, dict]:
    async with AsyncCrawler(base_url, max_concurrency, max_pages) as crawler:
        return await crawler.crawl()
