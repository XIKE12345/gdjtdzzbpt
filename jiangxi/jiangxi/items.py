# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JiangXiItem(scrapy.Item):
    """
    江西 Item定义
    """
    # 唯一标识, 用来数据排重，一般取url全路径的md5
    _id = scrapy.Field()

    # 网站
    site = scrapy.Field()

    # 公告来源
    source = scrapy.Field()

    # 标题
    title = scrapy.Field()

    # 原文地址
    url = scrapy.Field()

    # 地区
    area = scrapy.Field()

    # 具体地区，如：黑龙江省某市
    area_detail = scrapy.Field()

    # 公告类型，如：成交公告
    notice_type = scrapy.Field()

    # 公告时间
    notice_time = scrapy.Field()

    # 采购人
    buyer = scrapy.Field()

    # 正文内容
    content = scrapy.Field()
