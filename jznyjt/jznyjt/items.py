# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CommonRawItem(scrapy.Item):
    # _id: 公告唯一标识，算法: md5(公告正文链接)
    # area: 公告地点(省份)，中文，例如：北京、四川
    # area_detail：公告地点（地市），中文，例如：南京、南通
    # notice_time: 格式固定为 2019.02.02 21:21:21
    # buyer:  采购人，中文，例如：中央电视台
    # notice_type: 公告类型，中文，如：更正公告、中标候选人公示
    # tos: 业务类型，中文，如：工程建设，政府采购，土地使用权, 矿业权, 药品采购等
    # site:   网站的domain, 例如：jznyjt.gov.cn
    # source：信息来源细分，比如：http://www.ccgp.gov.cn/ 分为中央公告和地方公告
    # title：公告标题，中文
    # url：公告正文连接，如：http://www.ccgp.gov.cn/cggg/zygg/gzgg/201902/t20190202_11610905.htm
    # content：公告正文，base64(zlib(原文))

    # 唯一标识, 用来数据排重，一般取url全路径的md5
    _id = scrapy.Field()

    # 网站, 例如：jznyjt.gov.cn
    site = scrapy.Field()

    # 公告来源，如：中央公告
    source = scrapy.Field()

    # 标题
    title = scrapy.Field()

    # 原文地址
    url = scrapy.Field()

    # 地区，如：江苏
    area = scrapy.Field()

    # 地区，如：南通
    area_detail = scrapy.Field()

    # 公告类型，如：成交公告
    notice_type = scrapy.Field()

    # 业务类型，如：政府采购
    tos = scrapy.Field()

    # 公告时间
    notice_time = scrapy.Field()

    # 采购人
    buyer = scrapy.Field()

    # 正文内容
    content = scrapy.Field()

    # 时间戳
    time_stamp = scrapy.Field()

    # 正文内容
    tos_code = scrapy.Field()

    # 时间戳
    notice_type_code = scrapy.Field()
