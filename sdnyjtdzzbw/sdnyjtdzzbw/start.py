from scrapy import cmdline

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# 公开招标-工程
# cmdline.execute("scrapy crawl minegoods_spider  -a start_time=2010:07:23 -a end_time=2020:01:21 -a type=gkzb_gc_search -a start_page=1".split())
# 公开招标-货物
# cmdline.execute("scrapy crawl minegoods_spider  -a start_time=2010:07:23 -a end_time=2020:01:21 -a type=gkzb_hw_search -a start_page=1".split())
# 公开招标-服务
#cmdline.execute("scrapy crawl minegoods_spider  -a start_time=2010:07:23 -a end_time=2020:01:21 -a type=gkzb_fw_search -a start_page=1".split())
# 资格预审-工程
# cmdline.execute("scrapy crawl minegoods_spider  -a start_time=2010:07:23 -a end_time=2020:01:21 -a type=zgys_gc_search -a start_page=1".split())
# 资格预审-货物
# cmdline.execute("scrapy crawl minegoods_spider  -a start_time=2010:07:23 -a end_time=2020:01:21 -a type=zgys_hw_search -a start_page=1".split())
# 资格预审-服务
# cmdline.execute("scrapy crawl minegoods_spider  -a start_time=2010:07:23 -a end_time=2020:01:21 -a type=zgys_fw_search -a start_page=1".split())
# 变更公告-工程
# cmdline.execute("scrapy crawl minegoods_spider  -a start_time=2010:07:23 -a end_time=2020:01:21 -a type=bggg_gc_search -a start_page=1".split())
# 变更公告-货物
# cmdline.execute("scrapy crawl minegoods_spider  -a start_time=2010:07:23 -a end_time=2020:01:21 -a type=bggg_hw_search -a start_page=1".split())
# 变更公告-服务
# cmdline.execute("scrapy crawl minegoods_spider  -a start_time=2010:07:23 -a end_time=2020:01:21 -a type=bggg_fw_search -a start_page=1".split())
# 中标候选公示-工程
# cmdline.execute("scrapy crawl minegoods_spider  -a start_time=2010:07:23 -a end_time=2020:01:21 -a type=zbhx_gc_search -a start_page=1".split())
# 中标候选公示-货物
# cmdline.execute("scrapy crawl minegoods_spider  -a start_time=2010:07:23 -a end_time=2020:01:21 -a type=zbhx_hw_search -a start_page=1".split())
# 中标候选公示-服务
# cmdline.execute("scrapy crawl minegoods_spider  -a start_time=2010:07:23 -a end_time=2020:01:21 -a type=zbhx_fw_search -a start_page=1".split())
# 中标结果-工程
cmdline.execute("scrapy crawl minegoods_spider  -a start_time=2010:07:23 -a end_time=2020:01:21 -a type=zbjg_gc_search -a start_page=1".split())
# 中标结果-货物
# cmdline.execute("scrapy crawl minegoods_spider  -a start_time=2010:07:23 -a end_time=2020:01:21 -a type=zbjg_hw_search -a start_page=1".split())
# 中标结果-服务
# cmdline.execute("scrapy crawl minegoods_spider  -a start_time=2010:07:23 -a end_time=2020:01:21 -a type=zbjg_fw_search -a start_page=1".split())