# -*- coding: utf-8 -*-
import scrapy
from bloom_filter import BloomFilter
from ..utils import CcgpUtil
from ..items import JiangXiItem
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
    name = 'jiangxi_spider'
    allowed_domains = ['jxsggzy.cn']

    #  初始化
    def __init__(self, *args, **kwargs):
        # // 要爬取网站的跟
        self.base_url = 'http://jxsggzy.cn/web/'
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
        # py -3 -m scrapy crawl jiangxi_spider -a start_time="2019:01:01" -a end_time="2019:01:02"
        # assert self.start_time is not None
        # assert self.end_time is not None
        # self.scrawl_mode = ScrawlMode.REAL_TIME if str(self.start_time).lower() == 'now' else ScrawlMode.HISTORY
        #
        # if self.scrawl_mode == ScrawlMode.HISTORY:
        #     if (len(self.start_time) != 10 or len(self.end_time) != 10
        #             or self.start_time[4] != ':' or self.end_time[4] != ':'):
        #         logging.error('Bad date format. Example: 2019:01:01')
        #         return
        # else:x
        #     # 取当天日期
        #     _dt = datetime.fromtimestamp(time.time())
        #     self.start_time = _dt.strftime("%Y:%m:%d")
        #     self.end_time = self.start_time
        #
        info_type = {
            "01": {
                "name": "房屋及市政工程",
                "type": [1, 2, 3, 4]
            },
            "02": {
                "name": "交通工程",
                "type": [2, 3, 5]
            },
            "03": {
                "name": "水利工程",
                "type": [1, 2, 3, 4, 5]
            },
            "05": {
                "name": "重点工程",
                "type": [1, 2, 3, 4]
            },
            "06": {
                "name": "政府采购",
                "type": [1, 2, 3, 4, 5, 6]
            },
            "07": {
                "name": "国土资源交易",
                "type": [1, 2]
            },
            "08": {
                "name": "产权交易",
                "type": [3, 1, 2]
            },
            "09": {
                "name": "林权交易",
                "type": [1, 2]
            },
            "10": {
                "name": "医药采购",
                "type": [1, 2]
            },
            "13": {
                "name": "其他项目",
                "type": [1, 2]
            }
        }
        for _info_item in list(info_type.keys()):
            for _index, _info_item_num in enumerate(info_type[_info_item]["type"]):
                _change_url = "http://jxsggzy.cn/web/jyxx/0020{}/0020{}00{}".format(_info_item,
                                                                                      _info_item,
                                                                                      _info_item_num)

                _page_url = "http://jxsggzy.cn/web/jyxx/0020{}/0020{}00{}/1.html".format(_info_item,
                                                                                              _info_item,
                                                                                              _info_item_num)
                _page_meta = {
                    "_info_item": _info_item,
                    "_info_item_num": _info_item_num,
                    "_index": _index,
                    "_change_url": _change_url,
                }
                time.sleep(1)
                yield scrapy.Request(url=_page_url, callback=self.parse_init, meta={'_page_meta': _page_meta})

    def parse_init(self, response):
        """
        :param response:
        :return:
        """
        self._stop_parse = False
        _total_num = response.xpath('//span[@id="index"]/text()').extract_first()
        _total_num = _total_num.split('/')[1]
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

    def parse_detail(self, response):
        # print(1)
        _info_type_detail = {
            "01": {
                "name": "房屋及市政工程",
                "type": ["招标公告", "答疑澄清", "文件下载", "中标公告"]
            },
            "02": {
                "name": "交通工程",
                "type": ["招标公告", "补疑书", "中标公告"]
            },
            "03": {
                "name": "水利工程",
                "type": ["资格预审公告/招标公告", "澄清补遗", "文件下载", "中标候选人公示", "中标结果公示"]
            },
            "05": {
                "name": "重点工程",
                "type": ["招标公告", "答疑澄清", "文件下载", "结果公示"]
            },
            "06": {
                "name": "政府采购",
                "type": ["采购公告", "变更公告", "答疑澄清", "结果公示", "单一来源公告", "合同公示"]
            },
            "07": {
                "name": "国土资源交易",
                "type": ["交易公告", "成交公告"]
            },
            "08": {
                "name": "产权交易",
                "type": ["信息披露", "交易公告", "成交公告"]
            },
            "09": {
                "name": "林权交易",
                "type": ["信息披露", "成交公示"]
            },
            "10": {
                "name": "医药采购",
                "type": ["采购公告", "结果公示"]
            },
            "13": {
                "name": "其他项目",
                "type": ["交易公告", "成交公示"]
            }
        }

        item = JiangXiItem()

        for selector in response.xpath('.//div[@class="ewb-infolist"]/ul/li'):
            time.sleep(random.randint(100, 200) / 1000.0)  # 100 - 200 ms
            # 公告所对应url
            _content_url = selector.xpath('.//a/@href').extract_first()
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

            item['bid_type'] = _info_type_detail[_info_item_detail]["name"]
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
            # if self.start_time or self.end_time:
            #     try:
            #         self.start_time = self.start_time.split(" ")[0].replace(":", ".")
            #         self.end_time = self.end_time.split(" ")[0].replace(":", ".")
            #
            #         if len(self.start_time) == 10:
            #             self.start_time = self.start_time + " 00:00:00"
            #
            #         if len(self.end_time) == 10:
            #             self.end_time = self.end_time + " 00:00:00"
            #
            #     except:
            #         logging.exception(
            #             'self.start_time {} or self.end_time failed {}'.format(self.start_time,
            #                                                                    self.end_time))
            # print(self.start_time, item['notice_time'])
            # if self.start_time > item['notice_time'] or self.end_time < item['notice_time']:
            #     self._stop_parse = True
            #     logging.info('time interval')
            #     return
            # else:
            #     self._stop_parse = False

            # 公告的标题
            item['title'] = self.__get_title__(selector, _detail_page_url)

            # 内容
            item['content'] = self.__get_content__(selector, _detail_page_url)

            print(item)
            yield item

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
            _bid_info = selector.xpath('.//span[@class="ewb-list-date"]/text()').extract_first()
            if _bid_info:
                _ret = _bid_info.replace('-', '.') + " 00:00:00"
        except:
            logging.exception('{} get_notice_time failed'.format(url))

        return _ret

    @staticmethod
    def __get_title__(selector, url):
        _ret = ''
        try:
            _ret = selector.xpath('./a[@class="ewb-list-name"]/text()').extract_first().replace('\\n', '').rstrip().lstrip()
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
