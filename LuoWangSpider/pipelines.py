# -*- coding: utf-8 -*-
import os
import json
import scrapy
import pymongo
from scrapy.exceptions import DropItem
from settings import FILES_STORE
from scrapy.pipelines.files import FilesPipeline


class Mp3Pipeline(FilesPipeline):
    '''
    自定义文件下载管道
    '''
    def get_media_requests(self, item, info):
        '''
        根据文件的url逐一发送请求
        :param item:

        :param info: 
        :return: 
        '''
        for music_url in item['music_urls']:
            yield scrapy.Request(url=music_url, meta={'item':item})

    def item_completed(self, results, item, info):
        '''
        处理请求结果
        :param results: 
        :param item: 
        :param info: 
        :return: 
        '''
        file_paths = [x['path'] for ok, x in results if ok]
        if not file_paths:
            raise DropItem("Item contains no files")

        for i in range(0, len(item['music_name'])):
            old_name = FILES_STORE + file_paths[i]
            new_name = FILES_STORE + 'Vol.' + item['vol_num'] + '_' + item['vol_title'] + '/' + item['music_name'][i] + '.mp3'

            # 文件重命名
            os.rename(old_name, new_name)
        return item

    def file_path(self, request, response=None, info=None):
        '''
        自定义文件保存路径
        :param request:
        :param response:
        :param info:
        :return:
        '''
        vol_title = request.meta['item']['vol_title']
        vol_num = request.meta['item']['vol_num']

        file_name = request.url.split('/')[-1]
        folder_name = 'Vol.' + vol_num + '_' + vol_title
        return '%s/%s' % (folder_name, file_name)

    def close_spider(self, spider):
        '''
        爬虫结束时删除系统自动创建的full文件夹.
        :param spider:
        :return:
        '''
        raw_folder = FILES_STORE + 'full'
        if os.path.exists(raw_folder):
            os.rmdir(raw_folder)

 # # 将文本文件保存为json格式
# class LuoWangSpiderPipeline(object):
#     def __init__(self):
#         self.json_file = open(r'F:\luowang\luowang.json', 'wb')
#
#     def process_item(self, item, spider):
#         self.json_file.write(json.dumps(dict(item),ensure_ascii=False) + '\n')
#         return item



class MongoPipeline(object):
    '''
    添加文件到mongodb
    '''

    def __init__(self, mongo_server, mongo_port, mongo_db, mongo_collection):
        self.mongo_server = mongo_server
        self.mongo_port = mongo_port
        self.mongo_db = mongo_db
        self.mongo_collection = mongo_collection

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_server=crawler.settings.get('MONGODB_SERVER'),
            mongo_port=crawler.settings.get('MONGODB_PORT'),
            mongo_db=crawler.settings.get('MONGODB_DB'),
            mongo_collection=crawler.settings.get('MONGODB_COLLECTION'),
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_server, self.mongo_port)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()
        
    # 利用update方法插入数据,
    # 第一个参数为更新条件,第二个参数是更新后的数据,
    # 第三个参数为True表示数据库中有该文档字段就更新,没有则添加,达到去重的效果
    def process_item(self, item, spider):
        self.db[self.mongo_collection].update({'vol_num': item['vol_num']}, {'$set': dict(item)}, True)
        return item
