from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import time
from task_4.items import CoachItem
from task_4.field_setter import ItemSetter, ResponseHolder


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
        ResponseHolder().set_response(response)

        field_setter = ItemSetter()
        field_setter.set_fields()
        fields = field_setter.get_fields()

        item = CoachItem(
            skus=fields["Skus"],
            name=fields["Name"],
            category=fields["Category"],
            description=fields["Description"],
            image_url=fields["ImageUrl"],
            price=fields["Price"],
            currency=fields["Currency"],
            Link=response.url,
            url_original=response.url,
            crawl_start_time=start_time,
            spider_name=self.name,
            brand="coach",
            merch_info="Not Applicable",
            care="Not Applicable",
        )
        yield item
