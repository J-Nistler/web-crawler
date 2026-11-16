# web-crawler

An async web crawler written in Python. It starts at a URL, follows links on the
same domain, and writes the data from each page it visits to a JSON report.

Built as part of the Boot.dev "Build a Web Scraper in Python" course.

## Requirements

- Python 3.14 or later
- [uv](https://docs.astral.sh/uv/)

## Usage

```
uv run main.py URL [max_concurrency] [max_pages]
```

- `URL`: the page to start crawling from.
- `max_concurrency`: how many pages to fetch at once. The default is 3.
- `max_pages`: when to stop crawling. The default is 10.

For example:

```
uv run main.py https://learnwebscraping.dev/practice/ecommerce/ 3 10
```

The crawler prints each URL as it visits it, then writes `report.json`. The
report is a list of pages sorted by URL. Each page has these fields:

- `url`
- `heading`: the text of the first `<h1>`, or the first `<h2>` if there's no `<h1>`.
- `first_paragraph`: the text of the first `<p>`, preferring one inside `<main>`.
- `outgoing_links`: every link on the page, as full URLs.
- `image_urls`: every image on the page, as full URLs.

## Tests

```
uv run -m unittest -v
```
