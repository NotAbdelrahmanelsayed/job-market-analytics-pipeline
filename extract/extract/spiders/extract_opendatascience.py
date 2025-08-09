from datetime import datetime
import re
import scrapy
from bs4 import BeautifulSoup



def clean_text(html_or_none: str) -> str:
    if not html_or_none:
        return ""
    soup = BeautifulSoup(html_or_none, "html.parser")
    return " ".join(soup.stripped_strings)

class OpenDataScienceFeedSpider(scrapy.Spider):
    MAX_PAGES = 300
    name = "ods"
    allowed_domains = ["jobs.opendatascience.com"]

    custom_settings = {
        "DOWNLOAD_DELAY": 0.4,
        "RETRY_TIMES": 10,
        "DOWNLOAD_TIMEOUT": 60,
        "USER_AGENT": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/127.0 Safari/537.36"
        ),
        "DEPTH_LIMIT": MAX_PAGES,
    }


    def start_requests(self):
        url = "https://jobs.opendatascience.com/jobs/feed/?post_type=noo_job&s=&location=0&paged=1"
        yield scrapy.Request(
            url,
            headers={
                "Accept": "application/rss+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            },
            meta={"page": 1},
        )

    def parse(self, response):
        page = response.meta.get("page", 1)
        items = response.xpath("//channel/item")

        if not items:
            self.logger.info(f"No items on page {page}. Stopping.")
            return

        for post in items:
            title = post.xpath("normalize-space(title)").get(default="")
            link = post.xpath("link/text()").get(default="")
            pub_date = post.xpath("pubDate/text()").get(default="")

            # Prefer content:encoded; fall back to description
            encoded_html = post.xpath('string(*[local-name()="encoded"])').get(default="")
            desc_html = post.xpath("string(description)").get(default="")
            content_html = encoded_html or desc_html

            yield {
                "title": title,
                "link": link,
                "pubDate": pub_date,
                "content_text": clean_text(content_html),  # cleaned plaintext
            }

        # paginate while we still get items
        if page < self.MAX_PAGES:
            next_page = page + 1
            next_url = re.sub(r"paged=\d+", f"paged={next_page}", response.url)
            yield response.follow(
                next_url,
                callback=self.parse,
                headers=response.request.headers,
                meta={"page": next_page},
            )
        else:
            self.logger.info(f"Reached MAX_PAGES={self.MAX_PAGES}. Stopping.")
