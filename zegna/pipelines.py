# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from zegna.items import storeLinksItem, dataItem
from zegna.db_config import DbConfig
obj = DbConfig()

class ZegnaPipeline:
    def process_item(self, item, spider):
        obj.create_data_table(obj.data_table)
        if isinstance(item, storeLinksItem):
            obj.insert_store_links_table(item)
        if isinstance(item, dataItem):
            obj.insert_data_table(item)
            obj.update_store_links_status(item['store_no'])
        return item
