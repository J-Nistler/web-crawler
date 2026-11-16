import asyncio
import sys

from crawl import crawl_site_async
from json_report import write_json_report

USAGE = "usage: uv run main.py URL [max_concurrency] [max_pages]"


def parse_positive_int(value: str, name: str) -> int:
    try:
        number = int(value)
    except ValueError:
        number = 0
    if number < 1:
        print(f"{name} must be a positive integer, got {value!r}")
        print(USAGE)
        sys.exit(1)
    return number


async def main():
    if len(sys.argv) < 2:
        print("no website provided")
        print(USAGE)
        sys.exit(1)
    if len(sys.argv) > 4:
        print("too many arguments provided")
        print(USAGE)
        sys.exit(1)

    base_url = sys.argv[1]
    max_concurrency = parse_positive_int(sys.argv[2], "max_concurrency") if len(sys.argv) > 2 else 3
    max_pages = parse_positive_int(sys.argv[3], "max_pages") if len(sys.argv) > 3 else 10

    print(
        f"starting crawl of: {base_url} "
        f"(max_concurrency={max_concurrency}, max_pages={max_pages})"
    )

    page_data = await crawl_site_async(base_url, max_concurrency, max_pages)

    write_json_report(page_data)
    print(f"found {len(page_data)} pages, report written to report.json")

if __name__ == "__main__":
    asyncio.run(main())
