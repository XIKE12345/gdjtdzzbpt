from scrapy import cmdline

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# 招标公告-工程
cmdline.execute("scrapy crawl run_spider  -a start_time=2010:07:23 -a end_time=2020:01:21 -a type=zbgg_gc_search -a start_page=1".split())
# 招标公告-货物
# cmdline.execute("scrapy crawl run_spider  -a start_time=2010:07:23 -a end_time=2020:01:21 -a type=zbgg_hw_search -a start_page=1".split())
# 招标公告-服务
# cmdline.execute("scrapy crawl run_spider  -a start_time=2010:07:23 -a end_time=2020:01:21 -a type=zbgg_fw_search -a start_page=1".split())
# 非招标公告-工程
# cmdline.execute("scrapy crawl run_spider  -a start_time=2010:07:23 -a end_time=2020:01:21 -a type=fzbgg_gc_search -a start_page=1".split())
# 非招标公告-货物
# cmdline.execute("scrapy crawl run_spider  -a start_time=2010:07:23 -a end_time=2020:01:21 -a type=fzbgg_hw_search -a start_page=1".split())
# 非招标公告-服务
# cmdline.execute("scrapy crawl run_spider  -a start_time=2010:07:23 -a end_time=2020:01:21 -a type=fzbgg_fw_search -a start_page=1".split())
# 中标候选人-工程
# cmdline.execute("scrapy crawl run_spider  -a start_time=2010:07:23 -a end_time=2020:01:21 -a type=zbhx_gc_search -a start_page=1".split())
# 中标候选人-货物
# cmdline.execute("scrapy crawl run_spider  -a start_time=2010:07:23 -a end_time=2020:01:21 -a type=zbhx_hw_search -a start_page=1".split())
# 中标候选人-服务
# cmdline.execute("scrapy crawl run_spider  -a start_time=2010:07:23 -a end_time=2020:01:21 -a type=zbhx_fw_search -a start_page=1".split())
# 中标结果-工程
# cmdline.execute("scrapy crawl run_spider  -a start_time=2010:07:23 -a end_time=2020:01:21 -a type=zbjg_gc_search -a start_page=1".split())
# 中标结果-货物
# cmdline.execute("scrapy crawl run_spider  -a start_time=2010:07:23 -a end_time=2020:01:21 -a type=zbjg_hw_search -a start_page=1".split())
# 中标结果-服务
# cmdline.execute("scrapy crawl run_spider  -a start_time=2010:07:23 -a end_time=2020:01:21 -a type=zbjg_fw_search -a start_page=1".split())