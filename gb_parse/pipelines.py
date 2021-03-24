# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient
from scrapy import Request


class GbParsePipeline:
    def process_item(self, item, spider):
        return item


class GbParseMongoPipeline:
    def __init__(self):
        client = MongoClient()
        self.db = client["gb_parse_16_02_2021"]

    def process_item(self, item, spider):
        self.db[spider.name].insert_one(item)
        return item

class GbImageDownloadPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        for url in item.get("photos", []):
            yield Request(url)
        image = item["data"].get("profile_pic_url") or item["data"].get("display_url")
        if image:
            yield Request(image)

    def item_completed(self, results, item, info):
        if results:
            item["photos"] = [itm[1] for itm in results]
        return item