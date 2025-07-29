import scrapy
from scrapy_playwright.page import PageMethod
from playwright.async_api import Page
from playwright.async_api import TimeoutError as PlaywrightTimeout


class DataEngJobsSpider(scrapy.Spider):
    name = "data_eng_job"

    def start_requests(self):
        yield scrapy.Request(
            url="https://dataengjobs.com/",
            callback=self.parse,
            meta={
                "playwright": True,
                "playwright_include_page": True,
            },
        )

    async def parse(self, response):

        page: Page = response.meta["playwright_page"]
        page_num = 1
        seen_links = set()

        while True:
            # Grab the full html
            html = await page.content()
            sel = scrapy.Selector(text=html)

            # Extract jobs
            job_list = sel.css("ul.jobs.cf > li")
            self.logger.info(f"page {page_num}: found {len(job_list)} jobs...")

            for job in job_list:
                job_link = job.css("a::attr(href)").get()
                if job_link not in seen_links:
                    seen_links.add(job_link)
                    yield response.follow(
                        job_link,
                        callback=self.parse_details,
                        meta={"playwright": True},
                        cb_kwargs={
                            "meta_data": {
                                "title": job.css("span.position::text").get(),
                                "company_name": job.css("span.company::text").get(),
                                "location": job.css("span.location .city::text").get(),
                                "remote_type": job.css("span.remote::text").get(),
                                "salary": job.css("span.salary::text").get(),
                                "timeago": job.css("span.timeago::text").get(),
                            }
                        },
                    )

            # Click on the next page
            try:
                await page.wait_for_selector(
                    '//button[contains(@class, "load-more-btn") and .//span[text()="Next page"]]',
                    timeout=3000,
                )
                await page.click(
                    '//button[contains(@class, "load-more-btn") and .//span[text()="Next page"]]'
                )
                await page.wait_for_timeout(1500)
                page_num += 1
            except PlaywrightTimeout:
                self.logger.info(f"No more pages..")
                break

        await page.close()

    async def parse_details(self, response, meta_data):
        description = response.css("div.description-wrap *::text").getall()
        description = " ".join([d.strip() for d in description if d.strip()])
        yield {**meta_data, "description": description}
