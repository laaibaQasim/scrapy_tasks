import scrapy


class CoachItem(scrapy.Item):
    skus = scrapy.Field()
    name = scrapy.Field()
    category = scrapy.Field()
    link = scrapy.Field()
    brand = scrapy.Field()
    url_original = scrapy.Field()
    description = scrapy.Field()
    image_url = scrapy.Field()
    merch_info = scrapy.Field()
    price = scrapy.Field()
    currency = scrapy.Field()
    crawl_start_time = scrapy.Field()
    spider_name = scrapy.Field()
    care = scrapy.Field()
