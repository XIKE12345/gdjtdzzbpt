# -*- coding: utf-8 -*-
import scrapy
from bloom_filter import BloomFilter
from ..utils import CcgpUtil
from ..items import SpicItem
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


class SpicSpider(scrapy.Spider):
    # 重点 启动参数
    name = 'spic_spider'
    allowed_domains = ['cpeinet.com.cn']

    #  初始化
    def __init__(self, *args, **kwargs):
        # // 要爬取网站的跟
        self.base_url = 'http://www.cpeinet.com.cn/'
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
        # 获取爬取时传过来的参数
        # command example:
        # py -3 -m scrapy crawl ccgp_search -a start_time="2019:01:01" -a end_time="2019:01:02"
        # assert self.start_time is not None
        # assert self.end_time is not None
        # self.scrawl_mode = ScrawlMode.REAL_TIME if str(self.start_time).lower() == 'now' else ScrawlMode.HISTORY
        #
        # if self.scrawl_mode == ScrawlMode.HISTORY:
        #     if (len(self.start_time) != 10 or len(self.end_time) != 10
        #             or self.start_time[4] != ':' or self.end_time[4] != ':'):
        #         logging.error('Bad date format. Example: 2019:01:01')
        #         return
        # else:
        #     # 取当天日期
        #     _dt = datetime.fromtimestamp(time.time())
        #     self.start_time = _dt.strftime("%Y:%m:%d")
        #     self.end_time = self.start_time
        #
        info_type = [1, 2, 3, 7, 33, 4, 5]
        for _info_item in info_type:
            _page_url = "http://www.cpeinet.com.cn/cpcec/bul/bul_list.jsp?type={}".format(_info_item)
            _page_meta = {
                "_info_item": _info_item,
                "_change_url": _page_url
            }
            time.sleep(1)
            yield scrapy.Request(url=_page_url, callback=self.parse_init, meta={'_page_meta': _page_meta})

    def parse_init(self, response):
        self._stop_parse = False
        _total_num = response.xpath('.//div[@class="page"]/font/text()').extract()[0]
        print(_total_num)

        if int(_total_num) > 0:
            try:
                for _page_num_item in range(int(_total_num)):
                    _page_init_detail_url = response.meta["_page_meta"]["_change_url"]
                    _page_init_detail_url = _page_init_detail_url + "/{}.html".format(_page_num_item + 1)
                    response.meta["_page_meta"]["_page_init_detail_url"] = _page_init_detail_url
                    # if self._stop_parse:
                    #     break
                    time.sleep(1)
                    yield scrapy.Request(url=_page_init_detail_url, callback=self.parse_detail,
                                         meta={'_page_meta': response.meta["_page_meta"]})
            except:
                logging.exception(' _total_num is faild {}'.format(response.url))

    def parse_datail(self, response):
        item = SpicItem()
        for selector in response.xpath('.//div[@class="article_list_lb"]/li'):
            time.sleep(random.randint(100, 200) / 1000.0)  # 100 - 200 ms
            # 公告所对应url
            _content_url = selector.xpath('.//span/a/@href').extract_first()
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
            item['area'] = "江西"

            print(_detail_page_url)
            # 公告所在具体地区
            # item['area_detail'] = self.__get_area_detail__(selector, _detail_page_url)

            # 招标人
            item['buyer'] = " "

            # 公告类型
            _index_detail = response.meta["_page_meta"]["_index"]
            _info_item_detail = response.meta["_page_meta"]["_info_item"]
            item['notice_type'] = _info_type_detail[_info_item_detail]["type"][_index_detail]

            # source
            item['source'] = "jx"

            # site
            item['site'] = "jx"

            # 公告所对应时间
            item['notice_time'] = self.__get_notice_time__(selector, _detail_page_url)
            # 公告的标题
            item['title'] = self.__get_title__(selector, _detail_page_url)

            # 内容
            item['content'] = self.__get_content__(selector, _detail_page_url)

            print(item)

        pass

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
