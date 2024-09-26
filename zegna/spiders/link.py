import scrapy
from scrapy.cmdline import execute as ex
import json
from zegna.db_config import DbConfig
from zegna.items import storeLinksItem
obj = DbConfig()

class LinkSpider(scrapy.Spider):
    name = "link"
    # allowed_domains = ["."]
    start_urls = ["https://storelocator-webservice.zegna.com/services/V8/storeList.json?point_position=42.8400314,-85.4780751&r=200000000&displayCountry=IN&language=EN"]

    def parse(self, response):
        jsn = json.loads(response.text)
        for j in jsn:
            item = storeLinksItem()
            item['country'] = j['COUNTRY']
            if item['country'] == 'UNITED STATES':
                item['store_id'] = j['STORE_ID']
                item['store_name'] = j['NAME']
                item['lng'] = j['LONGITUDE']
                item['lat'] = j['LATITUDE']
                item['address'] = j['ADDRESS']
                item['phone'] = j['PHONE_NUMBER']
                item['state'] = j['STATE']
                item['city'] = j['CITY']
                item['postal_code'] = j['POSTAL_CODE']
                item['email'] = j['EMAIL']
                item['opening_hours'] = j['OPENING_HOURS']
                item['store_manager'] = j['STORE_MANAGER']
                item['store_manager_email'] = j['STORE_MANAGER_EMAIL']
                yield item

if __name__ == '__main__':
    ex("scrapy crawl link".split())