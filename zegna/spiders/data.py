import os.path
from zegna.items import dataItem
import scrapy
import datetime
from scrapy.cmdline import execute as ex
from zegna.db_config import DbConfig
from zegna.common_func import create_md5_hash, page_write
from fake_useragent import UserAgent
ua = UserAgent()
today_date = datetime.datetime.today().strftime("%d_%m_%Y")
obj = DbConfig()


class DataSpider(scrapy.Spider):
    name = "data"
    handle_httpstatus_list = [403, 401, 404, 301]

    def start_requests(self):
        obj.cur.execute(f"select * from {obj.store_links_table} where status=0")
        rows = obj.cur.fetchall()
        for row in rows:
            store_id = row['store_id']
            address = row['address'].lower()
            address_list = address.split()
            address_url = '-'.join(address_list)
            city = row['city']
            city_list = city.split()
            city_url = '-'.join(city_list)
            store_url = f'https://www.zegna.com/in-en/store-locator/store-detail/united-states/{city_url.lower()}/{address_url}.{store_id}/'
            store_url = store_url.replace('#', '')
            hashid = create_md5_hash(store_url)
            pagesave_dir = rf"C:/Users/Actowiz/Desktop/pagesave/zegna/{today_date}"
            file_name = fr"{pagesave_dir}/{hashid}.html"
            row['file_name'] = file_name
            row['hashid'] = hashid
            row['pagesave_dir'] = pagesave_dir
            row['store_url'] = store_url
            if os.path.exists(file_name):
                yield scrapy.Request(
                    url= 'file:////'+file_name,
                    callback= self.parse,
                    cb_kwargs= row
                )
            else:
                headers = {
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'accept-language': 'en-US,en;q=0.9',
                    'cache-control': 'max-age=0',
                    'priority': 'u=0, i',
                    'user-agent': ua.random,
                }
                yield scrapy.Request(
                    url= store_url,
                    headers= headers,
                    callback= self.parse,
                    cb_kwargs= row
                )

    def parse(self, response, **kwargs):
        file_name = kwargs['file_name']
        if not(os.path.exists(file_name)):
            page_write(kwargs['pagesave_dir'], file_name, response.text)

        opening_hours = kwargs['opening_hours']
        opening_hours_split = opening_hours.split(',')
        weekdays_dict = {
            '1': 'Sunday',
            '2': 'Monday',
            '3': 'Tuesday',
            '4': 'Wednesday',
            '5': 'Thursday',
            '6': 'Friday',
            '7': 'Saturday'
                         }
        store_timings = list()
        for hour in opening_hours_split:
            hour_split = hour.split(':')
            day = weekdays_dict[str(hour_split[0])]
            timings = f'{hour_split[1]}:{hour_split[2]}-{hour_split[3]}:{hour_split[4]}'
            store_timings.append(f'{day}: {timings}')
        store_timings_final = ' | '.join(store_timings)
        direction_url = f"https://www.google.com/maps/dir/?api=1&destination={kwargs['lat']},{kwargs['lng']}"

        item = dataItem()
        item['store_no'] = kwargs['store_id']
        item['name'] = kwargs['store_name']
        item['latitude'] = kwargs['lat']
        item['longitude'] = kwargs['lng']
        item['street'] = kwargs['address']
        item['city'] = kwargs['city']
        item['state'] = kwargs['state']
        item['zip_code'] = kwargs['postal_code']
        item['county'] = kwargs['city']
        item['phone'] = kwargs['phone']
        item['open_hours'] = store_timings_final
        item['url'] = kwargs['store_url']
        item['provider'] = "Zegna"
        item['category'] = "Apparel And Accessory Stores"
        item['updated_date'] = datetime.datetime.today().strftime("%d-%m-%Y")
        item['country'] = "US"
        item['status'] = "Open"
        item['direction_url'] = direction_url
        item['pagesave_path'] = file_name
        yield item


if __name__ == '__main__':
    ex("scrapy crawl data".split())