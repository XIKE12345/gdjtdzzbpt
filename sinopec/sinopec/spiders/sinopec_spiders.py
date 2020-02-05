# -*- coding: utf-8 -*-
import scrapy
from bloom_filter import BloomFilter
from ..utils import CcgpUtil
from ..items import SinopecItem
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
    name = 'sinopec_spider'
    allowed_domains = ['zgsh.sinopec.com']

    #  初始化
    def __init__(self, *args, **kwargs):
        # // 要爬取网站的跟
        self.base_url = 'http://zgsh.sinopec.com'
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
        _page_url = "http://zgsh.sinopec.com/supp/index.shtml"
        yield scrapy.Request(url=_page_url, callback=self.parse_init)

    def parse_init(self, response):
        self._stop_parse = False
        item = SinopecItem()

        for selector in response.xpath('.//div[@class="itemli"]'):
            # time.sleep(random.randint(100, 200) / 1000.0)  # 100 - 200 ms
            _content_url = selector.xpath('.//a/@href').extract_first()
            _detail_page_url = response.urljoin(_content_url)
            print(_content_url)
            return
            item['url'] = _detail_page_url
            # 唯一标识
            _unq_id = CcgpUtil.get_unique_id(_detail_page_url)
            item['_id'] = _unq_id

            self.bloom_filter.add(_unq_id)

            # 公告所在地区
            item['area'] = "中石化"

            # print(_detail_page_url)

            # 招标人
            item['buyer'] = " "

            # 公告类型
            item['notice_type'] = '招标公告'

            # source
            item['source'] = "sinopec"

            # site
            item['site'] = "sinopec"

            # 公告所对应时间
            item['notice_time'] = self.__get_notice_time__(selector, _detail_page_url)
            # 公告的标题
            item['title'] = self.__get_title__(selector, _detail_page_url)
            #
            # # 内容
            item['content'] = self.__get_content__(selector, _detail_page_url)

            print(item)
            yield item

    @staticmethod
    def __get_notice_time__(selector, url):
        _ret = ''
        try:
            _bid_info = selector.xpath('./div[@class="date"]/text()').extract_first()
            _bid_info = ''.join(_bid_info.split())
            if _bid_info:
                _ret = _bid_info.replace('/', '') + " 00:00:00"
        except:
            logging.exception('{} get_notice_time failed'.format(url))

        return _ret

    @staticmethod
    def __get_title__(selector, url):
        # print(selector.xpath('string()').extract_first())
        _ret = ''
        try:
            _ret = selector.xpath('string()').extract_first().replace('\n', '').rstrip().lstrip()
            _ret = ''.join(_ret.split())
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
