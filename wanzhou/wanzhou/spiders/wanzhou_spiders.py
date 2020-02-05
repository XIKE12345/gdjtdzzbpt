# -*- coding: utf-8 -*-
import scrapy
from bloom_filter import BloomFilter
from ..utils import CcgpUtil
from ..items import WanzhouItem
import logging
import requests
import json
import base64
import zlib
import time
from enum import Enum
import random


class ScrawlMode(Enum):
    REAL_TIME = 0
    HISTORY = 1


class JiangxiSpider(scrapy.Spider):
    # 重点 启动参数
    name = 'wanzhouqu_spiders'
    allowed_domains = ['wzggzy.wz.gov.cn']

    #  初始化
    def __init__(self, *args, **kwargs):
        # // 要爬取网站的跟
        self.base_url = 'http://wzggzy.wz.gov.cn/'
        # super(QhSpider, self).__init__(*args, **kwargs)
        self.bloom_filter = BloomFilter(max_elements=1000000, error_rate=0.1, filename='bf.data')
        self.num = 0
        self.scrawl_mode = ScrawlMode.HISTORY
        self._stop_parse = False

    # main 启动函数
    def start_requests(self):
        """
        爬虫默认接口,启动方法
        :return:
        """

        info_type = {
            "01": {
                "name": "工程招投标",
                "type": [1, 2, 5]
            },

            "04": {
                "name": "政府采购",
                "type": [1, 2, 4]
            },

            "07": {
                "name": "土地交易",
                "type": [1, 3]
            },
            "08": {
                "name": "产权交易",
                "type": [1, 3]
            },
            "09": {
                "name": "竞选项目",
                "type": [1, 2, 3]
            }

        }
        for _info_item in list(info_type.keys()):
            for _index, _info_item_num in enumerate(info_type[_info_item]["type"]):
                _page_url = "http://wzggzy.wz.gov.cn/wzweb/jyxx/0010{}/0010{}00{}/".format(_info_item,
                                                                                           _info_item,
                                                                                           _info_item_num)
                _page_meta = {
                    "_info_item": _info_item,
                    "_info_item_num": _info_item_num,
                    "_index": _index,
                    "_change_url": _page_url,
                }
                time.sleep(1)
                yield scrapy.Request(url=_page_url, callback=self.parse_init, meta={'_page_meta': _page_meta})

    def parse_init(self, response):
        """
        :param response:
        :return:
        """
        self._stop_parse = False
        _info_type_detail = {
            "01": {
                "name": "工程招投标",
                "type": ["招标公告", "答疑补疑惑", "中标结果公示"]
            },

            "04": {
                "name": "政府采购",
                "type": ["采购公告", "答疑变更", "采购结果公示"]
            },

            "07": {
                "name": "土地交易",
                "type": ["出让公告", "成交公告"]
            },
            "08": {
                "name": "产权交易",
                "type": ["出让公告", "成交公告"]
            },
            "09": {
                "name": "竞选项目",
                "type": ["竞选公告", "答疑补遗", "竞选结果公示"]
            }
        }

        _page_url = "http://wzggzy.wz.gov.cn/wzweb/ZtbInfo/zhaobiao.aspx?categorynum=001009001&Paging=1"

        _r = requests.get(_page_url)
        _r.encoding = 'utf-8'
        _request = _r.text.encode('utf-8')

        _response = scrapy.http.HtmlResponse(url=_page_url, body=_r.text, encoding='utf-8')

        print(_response.url)
        print(_response.xpath('.//tbody').extract())

        # _total_num = _response.xpath('//div[@class="pageText xxxsHidden"]/text()').extract[0]

        # print(_total_num)
        # _total_num = _total_num.split('/')[1]
        # if int(_total_num) > 0:
        #     try:
        #         for _page_num_item in range(int(_total_num)):
        #             _page_init_detail_url = response.meta["_page_meta"]["_change_url"]
        #             _page_init_detail_url = _page_init_detail_url + "/{}.html".format(_page_num_item + 1)
        #             response.meta["_page_meta"]["_page_init_detail_url"] = _page_init_detail_url
        #             # if self._stop_parse:
        #             #     break
        #             time.sleep(1)
        #             yield scrapy.Request(url=_page_init_detail_url, callback=self.parse_detail,
        #                                  meta={'_page_meta': response.meta["_page_meta"]})
        #     except:
        #         logging.exception(' _total_num is faild {}'.format(response.url))

    #
    # self._stop_parse = False
    # _total_num = response.xpath('//div[@class="pageText xxxsHidden"]/text()').extract_first()
    # print(_total_num)
    # _total_num = _total_num.split('/')[1]
    # print(_total_num)
    # if int(_total_num) > 0:
    #     try:
    #         for _page_num_item in range(int(_total_num)):
    #             _page_init_detail_url = response.meta["_page_meta"]["_change_url"]
    #             _page_init_detail_url = _page_init_detail_url + "/{}.html".format(_page_num_item + 1)
    #             response.meta["_page_meta"]["_page_init_detail_url"] = _page_init_detail_url
    #             # if self._stop_parse:
    #             #     break
    #             time.sleep(1)
    #             yield scrapy.Request(url=_page_init_detail_url, callback=self.parse_detail,
    #                                  meta={'_page_meta': response.meta["_page_meta"]})
    #     except:
    #         logging.exception(' _total_num is faild {}'.format(response.url))

    @staticmethod
    def __get_area_detail__(selector, url):
        _ret = ''
        _area_detail = ["上绕市", "银川市", "石嘴山市", "吴忠市", "固原市", "中卫市"]

        try:
            _content_text = selector.xpath('string(./div[@class="ewb-info-a"]/a)').extract()[0]
            _content_text = ''.join(_content_text.split())
            for _item in _area_detail:
                if _item in _content_text:
                    _ret = _item
                    break
        except:
            logging.exception('{} get_area_detail__ failed'.format(url))

        return _ret

    @staticmethod
    def __get_notice_time__(selector, url):
        _ret = ''
        try:
            _bid_info = selector['showdate']
            if _bid_info:
                _ret = _bid_info.replace('-', '.')
            if len(_bid_info) == 10:
                _bid_info = _bid_info + " 00:00:00"
            else:
                _ret = _ret.split(" ")[0] + " 00:00:00"
        except:
            logging.exception('{} get_notice_time failed'.format(url))

        return _ret

    @staticmethod
    def __get_title__(selector, url):
        _ret = ''
        try:
            _ret = selector['title']
        except:
            logging.exception('{} get_title failed'.format(url))

        return _ret

    @staticmethod
    def __get_content__(selector, url):
        """
        正文内容
        如果提取正文内容失败，则判断此次爬取失败，所以这里不能用try except
        :param selector:
        :param url:
        :return:
        """
        _bad = False
        _ret = ''
        try:
            _r = requests.get(url, timeout=15)
            _r.encoding = 'utf-8'
            _ret = base64.b64encode(zlib.compress(_r.text.encode('utf-8'))).decode('utf-8')
        except:
            _bad = True

        # 如果有异常，重试一次
        if _bad:
            time.sleep(1)
            _r = requests.get(url, timeout=15)
            _r.encoding = 'utf-8'
            _ret = base64.b64encode(zlib.compress(_r.text.encode('utf-8'))).decode('utf-8')

        return _ret
