import unittest
from crawl import (
    extract_page_data,
    get_first_paragraph_from_html,
    get_images_from_html,
    get_heading_from_html,
    get_urls_from_html,
    normalize_url,
)


class TestCrawl(unittest.TestCase):
    def test_normalize_url_https(self):
        input_url = "https://www.boot.dev/blog/path"
        actual = normalize_url(input_url)
        expected = "www.boot.dev/blog/path"
        self.assertEqual(actual, expected)

    def test_normalize_url_https_trailing_slash(self):
        input_url = "https://www.boot.dev/blog/path/"
        actual = normalize_url(input_url)
        expected = "www.boot.dev/blog/path"
        self.assertEqual(actual, expected)

    def test_normalize_url_http_trailing_slash(self):
        input_url = "http://www.boot.dev/blog/path/"
        actual = normalize_url(input_url)
        expected = "www.boot.dev/blog/path"
        self.assertEqual(actual, expected)

    def test_normalize_url_uppercase_scheme_and_host(self):
        input_url = "HTTPS://WWW.BOOT.DEV/blog/path"
        actual = normalize_url(input_url)
        expected = "www.boot.dev/blog/path"
        self.assertEqual(actual, expected)

    def test_normalize_url_root_with_trailing_slash(self):
        input_url = "https://www.boot.dev/"
        actual = normalize_url(input_url)
        expected = "www.boot.dev"
        self.assertEqual(actual, expected)

    def test_get_heading_from_html_basic(self):
        input_body = "<html><body><h1>Test Title</h1></body></html>"
        actual = get_heading_from_html(input_body)
        expected = "Test Title"
        self.assertEqual(actual, expected)

    def test_get_heading_from_html_h2_fallback(self):
        input_body = "<html><body><h2>Fallback Title</h2></body></html>"
        actual = get_heading_from_html(input_body)
        expected = "Fallback Title"
        self.assertEqual(actual, expected)

    def test_get_heading_from_html_prefers_h1_over_h2(self):
        input_body = "<html><body><h2>Second</h2><h1>First</h1></body></html>"
        actual = get_heading_from_html(input_body)
        expected = "First"
        self.assertEqual(actual, expected)

    def test_get_heading_from_html_strips_whitespace_and_nested_tags(self):
        input_body = "<html><body><h1>\n  <span>Nested</span> Title  \n</h1></body></html>"
        actual = get_heading_from_html(input_body)
        expected = "NestedTitle"
        self.assertEqual(actual, expected)

    def test_get_heading_from_html_no_heading(self):
        input_body = "<html><body><p>No heading here</p></body></html>"
        actual = get_heading_from_html(input_body)
        expected = ""
        self.assertEqual(actual, expected)

    def test_get_heading_from_html_empty_string(self):
        actual = get_heading_from_html("")
        expected = ""
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_basic(self):
        input_body = "<html><body><p>First paragraph.</p><p>Second paragraph.</p></body></html>"
        actual = get_first_paragraph_from_html(input_body)
        expected = "First paragraph."
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_main_priority(self):
        input_body = """<html><body>
            <p>Outside paragraph.</p>
            <main>
                <p>Main paragraph.</p>
            </main>
        </body></html>"""
        actual = get_first_paragraph_from_html(input_body)
        expected = "Main paragraph."
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_main_without_paragraph(self):
        input_body = """<html><body>
            <p>Outside paragraph.</p>
            <main><h1>No paragraphs in main</h1></main>
        </body></html>"""
        actual = get_first_paragraph_from_html(input_body)
        expected = "Outside paragraph."
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_strips_whitespace(self):
        input_body = "<html><body><p>\n   Padded text.   \n</p></body></html>"
        actual = get_first_paragraph_from_html(input_body)
        expected = "Padded text."
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_no_paragraph(self):
        input_body = "<html><body><h1>Only a heading</h1></body></html>"
        actual = get_first_paragraph_from_html(input_body)
        expected = ""
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_empty_string(self):
        actual = get_first_paragraph_from_html("")
        expected = ""
        self.assertEqual(actual, expected)

    def test_get_urls_from_html_absolute(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><a href="https://crawler-test.com"><span>Boot.dev</span></a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://crawler-test.com"]
        self.assertEqual(actual, expected)

    def test_get_urls_from_html_relative(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><a href="/path/one"><span>Boot.dev</span></a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/path/one"]
        self.assertEqual(actual, expected)

    def test_get_urls_from_html_multiple_links(self):
        input_url = "https://crawler-test.com"
        input_body = """<html><body>
            <a href="/path/one">One</a>
            <div><a href="https://other.com/path/two">Two</a></div>
            <a href="three">Three</a>
        </body></html>"""
        actual = get_urls_from_html(input_body, input_url)
        expected = [
            "https://crawler-test.com/path/one",
            "https://other.com/path/two",
            "https://crawler-test.com/three",
        ]
        self.assertEqual(actual, expected)

    def test_get_urls_from_html_skips_anchors_without_href(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><a>No href</a><a href="/ok">OK</a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/ok"]
        self.assertEqual(actual, expected)

    def test_get_urls_from_html_no_links(self):
        input_url = "https://crawler-test.com"
        input_body = "<html><body><p>No links here</p></body></html>"
        actual = get_urls_from_html(input_body, input_url)
        expected = []
        self.assertEqual(actual, expected)

    def test_get_images_from_html_relative(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><img src="/logo.png" alt="Logo"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/logo.png"]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_absolute(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><img src="https://cdn.example.com/banner.jpg"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://cdn.example.com/banner.jpg"]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_multiple_images(self):
        input_url = "https://crawler-test.com"
        input_body = """<html><body>
            <img src="/one.png">
            <div><img src="images/two.gif" alt="Two"></div>
            <img src="https://other.com/three.svg">
        </body></html>"""
        actual = get_images_from_html(input_body, input_url)
        expected = [
            "https://crawler-test.com/one.png",
            "https://crawler-test.com/images/two.gif",
            "https://other.com/three.svg",
        ]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_missing_src(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><img alt="No src"><img src=""><img src="/ok.png"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/ok.png"]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_no_images(self):
        input_url = "https://crawler-test.com"
        input_body = "<html><body><p>No images here</p></body></html>"
        actual = get_images_from_html(input_body, input_url)
        expected = []
        self.assertEqual(actual, expected)

    def test_extract_page_data_basic(self):
        input_url = "https://crawler-test.com"
        input_body = """<html><body>
            <h1>Test Title</h1>
            <p>This is the first paragraph.</p>
            <a href="/link1">Link 1</a>
            <img src="/image1.jpg" alt="Image 1">
        </body></html>"""
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://crawler-test.com",
            "heading": "Test Title",
            "first_paragraph": "This is the first paragraph.",
            "outgoing_links": ["https://crawler-test.com/link1"],
            "image_urls": ["https://crawler-test.com/image1.jpg"],
        }
        self.assertEqual(actual, expected)

    def test_extract_page_data_subpage_relative_urls(self):
        input_url = "https://crawler-test.com/blog/post"
        input_body = """<html><body>
            <h2>Fallback Heading</h2>
            <p>Outside paragraph.</p>
            <main><p>Main paragraph.</p></main>
            <a href="next">Next</a>
            <a href="https://other.com/page">Other</a>
            <img src="pic.png">
            <img alt="No src">
        </body></html>"""
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://crawler-test.com/blog/post",
            "heading": "Fallback Heading",
            "first_paragraph": "Main paragraph.",
            "outgoing_links": [
                "https://crawler-test.com/blog/next",
                "https://other.com/page",
            ],
            "image_urls": ["https://crawler-test.com/blog/pic.png"],
        }
        self.assertEqual(actual, expected)

    def test_extract_page_data_empty_page(self):
        input_url = "https://crawler-test.com"
        input_body = "<html><body></body></html>"
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://crawler-test.com",
            "heading": "",
            "first_paragraph": "",
            "outgoing_links": [],
            "image_urls": [],
        }
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
