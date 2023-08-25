import time
import json
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from task_4.items import CoachItem


class CoachSpider(CrawlSpider):
    name = "coach_spider"
    allowed_domains = ["singapore.coach.com"]
    start_urls = ["https://singapore.coach.com/"]

    le_navbar = LinkExtractor(
        restrict_xpaths='//div[contains(@class, "nav-item") and contains(@class, "mega")]//a'
    )
    le_product = LinkExtractor(
        restrict_xpaths='//a[contains(@class, "product-item-link")]'
    )
    navbar_rule = Rule(le_navbar, callback="parse_item", follow=True)
    product_rule = Rule(le_product, callback="parse_item", follow=False)

    rules = (
        navbar_rule,
        product_rule,
    )

    def parse_item(self, response):
        start_time = int(time.time())
        coach_item = CoachItem()

        coach_item["skus"] = self.get_skus(response)
        coach_item["name"] = response.css("h1.page-title span::text").get()
        coach_item["category"] = self.get_category(response)

        coach_item["description"] = response.css(
            "div.product.attribute.description div.value li::text"
        ).getall()

        coach_item["image_url"] = response.css(
            'img[alt="main product photo"]::attr(src)'
        ).get()

        coach_item["price"] = (
            "Not Applicable"
            if (span := response.css(".product-info-price" " .price::text").get())
            is None
            else span.split("\xa0", 1)[1]
        )

        coach_item["currency"] = (
            "Not Applicable"
            if (span := response.css(".product-info-price" " .price::text").get())
            is None
            else span.split("\xa0", 1)[0]
        )

        coach_item["link"] = response.url
        coach_item["url_original"] = response.url
        coach_item["crawl_start_time"] = start_time
        coach_item["spider_name"] = self.name
        coach_item["brand"] = "Coach"
        coach_item["merch_info"] = "Not Applicable"
        coach_item["care"] = "Not Applicable"

        yield coach_item

    def find_sku_dict(self, text):
        pattern = r'"sku":\s*({[^}]*})'
        match = re.search(pattern, text)

        if match:
            return match.group(1)
        else:
            return {}

    def get_skus(self, response):
        script_text = response.css('script:contains("Magento_Swatches/js/swatch-renderer")::text').get()

        if not script_text:
            sku_value = response.css('form[data-product-sku]::attr(data-product-sku)').get()
            return "Not Applicable" if not sku_value else sku_value

        sku_dict = json.loads(self.find_sku_dict(script_text))
        skus = []

        for key, value in sku_dict.items():
            skus.append(value)

        return "Not Applicable" if skus == [] else skus

    def get_category(self, response):
        ecomm_category_match = re.search(r'"ecomm_category":"([^"]+)"', response.text)
        return (
            lambda match: match.group(1).replace("/", "").replace("\\", ",")
            if match
            else None
        )(ecomm_category_match)
