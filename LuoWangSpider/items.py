# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class LuoWangSpiderItem(scrapy.Item):
    vol_num = scrapy.Field()
    vol_title = scrapy.Field()
    vol_time = scrapy.Field()
    music_name = scrapy.Field()
    music_author = scrapy.Field()
    music_urls = scrapy.Field()
    music_files = scrapy.Field()
