import os
import dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from gb_parse.spiders.autoyoula import AutoyoulaSpider
from gb_parse.spiders.hh import HhSpider
from gb_parse.spiders.instagram import InstagramSpider
from gb_parse.spiders.zillow import ZillowSpider

if __name__ == "__main__":
    dotenv.load_dotenv(".env")
    tags = ["python"]
    crawler_settings = Settings()
    crawler_settings.setmodule("gb_parse.settings")
    crawler_proc = CrawlerProcess(settings=crawler_settings)
    #crawler_proc.crawl(AutoyoulaSpider)
    #crawler_proc.crawl(HhSpider)
    # crawler_proc.crawl(
    #     InstagramSpider,
    #     login=os.getenv("INST_LOGIN"),
    #     password=os.getenv("INST_PASSWORD"),
    #     tags=tags,
    # )
    crawler_proc.crawl(ZillowSpider)
    crawler_proc.start()