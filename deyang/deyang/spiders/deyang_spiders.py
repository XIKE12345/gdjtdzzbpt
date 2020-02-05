# -*- coding: utf-8 -*-
import scrapy
from bloom_filter import BloomFilter
from ..utils import CcgpUtil
from ..items import DeyangItem
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


class DeyangSpider(scrapy.Spider):
    # 四川德阳公共资源交易
    name = 'deyang_spider'
    allowed_domains = ['ggzyxx.deyang.gov.cn']

    #  初始化
    def __init__(self, *args, **kwargs):
        # // 要爬取网站的跟
        self.base_url = 'http://ggzyxx.deyang.gov.cn/'
        super(DeyangSpider, self).__init__(*args, **kwargs)
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
        _info_type = {
            "tradeinfo_jygcjs_": {"工程建设"}, "tradeinfo_jycg_": {"政府采购"},
            "tradeinfo_gygt_": {"国土矿业权"}
            # , "tradeinfo_jygzcq_": {"国资产权"}
        }

        for _info_item in (_info_type.keys()):
            _change_url = "http://ggzyxx.deyang.gov.cn/pub/{}/".format(_info_item)
            _page_url = "http://ggzyxx.deyang.gov.cn/pub/{}.html".format(_info_item)
            _page_meta = {"_info_item": _info_item}
            time.sleep(1)
            yield scrapy.Request(url=_page_url, callback=self.parse_init, meta={'_page_meta': _page_meta})

    def parse_init(self, response):
        """
        :param response:
        :return:
        """
        self._stop_parse = False
        _total_num = response.xpath('.//div[@class="pagenations"]/a/text()').extract[4]
        print(_total_num)
        print("----------------------------")

        # if int(_total_num) > 0:
        #     try:
        #         for _page_num_item in range(int(_total_num)):
        #             _page_init_detail_url = response.meta["_page_meta"]["_change_url"]
        #             _page_init_detail_url = _page_init_detail_url + "/{}.html".format(_page_num_item + 1)
        #             response.meta["_page_meta"]["_page_init_detail_url"] = _page_init_detail_url
        #
        #             time.sleep(1)
        #             yield scrapy.Request(url=_page_init_detail_url, callback=self.parse_detail,
        #                                  meta={'_page_meta': response.meta["_page_meta"]})
        #     except:
        #         logging.exception(' _total_num is faild {}'.format(response.url))

    def parse_detail(self, response):
        _info_type_detail = {
            {"tradeinfo_jygcjs_": "工程建设"}, {"tradeinfo_jycg_": "政府采购"},
            {"tradeinfo_gygt_": "国土矿业权"}
            # , {"tradeinfo_jygzcq_": "国资产权"}
        }

        item = DeyangItem()
        for selector in response.xpath('.//div[@class="search-result"]/ul/li'):
            time.sleep(random.randint(100, 200) / 1000.0)  # 100 - 200 ms
            # 公告所对应url
            _content_url = selector.xpath('./a/@href').extract_first()
            _detail_page_url = response.urljoin(_content_url)
            item['url'] = _detail_page_url

            # 唯一标识
            _unq_id = CcgpUtil.get_unique_id(_detail_page_url)
            item['_id'] = _unq_id

            # 如果是重复数据，不处理
            if _unq_id in self.bloom_filter:
                continue

            self.bloom_filter.add(_unq_id)

            # 公告所在地区
            item['area'] = "德阳市"

            print(_detail_page_url)
            # 公告所在具体地区
            # item['area_detail'] = self.__get_area_detail__(selector, _detail_page_url)

            # 招标人
            item['buyer'] = " "

            # 公告类型
            _index_detail = response.meta["_page_meta"]["_index"]
            _info_item_detail = response.meta["_page_meta"]["_info_item"]
            item['notice_type'] = _info_type_detail[_info_item_detail][_index_detail]

            # source
            item['source'] = "deYang"

            # site
            item['site'] = "deYang"

            # 公告所对应时间
            item['notice_time'] = self.__get_notice_time__(selector, _detail_page_url)
            # 公告的标题
            item['title'] = self.__get_title__(selector, _detail_page_url)

            # 内容
            item['content'] = self.__get_content__(selector, _detail_page_url)

            print(item)

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
            _bid_info = selector.xpath('./span[@class="time"]/text()').extract_first()
            if _bid_info:
                _ret = _bid_info.replace('-', '.') + " 00:00:00"
        except:
            logging.exception('{} get_notice_time failed'.format(url))
        return _ret

    @staticmethod
    def __get_title__(selector, url):
        _ret = ''
        try:
            _ret = selector.xpath('./a[@class="weekdays"]/text()').extract_first().replace('\\n', '').rstrip().lstrip()
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
