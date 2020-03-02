from scrapy import cmdline

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# 招标公告-工程
cmdline.execute("scrapy crawl run_spider  -a start_time=2019:01:01 -a end_time=2020:01:21 -a type=gc_search -a start_page=1".split())
# 招标公告-货物
# cmdline.execute("scrapy crawl run_spider  -a start_time=2010:07:23 -a end_time=2020:01:21 -a type=hw_search -a start_page=1".split())
# 招标公告-服务
# cmdline.execute("scrapy crawl run_spider  -a start_time=2010:07:23 -a end_time=2020:01:21 -a type=fw_search -a start_page=1".split())
# 中标公告
# cmdline.execute("scrapy crawl run_spider  -a start_time=2010:07:23 -a end_time=2020:01:21 -a type=zb_search -a start_page=1".split())
# 网上询价
# cmdline.execute("scrapy crawl run_spider  -a start_time=2010:07:23 -a end_time=2020:01:21 -a type=xj_search -a start_page=1".split())
