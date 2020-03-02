from scrapy import cmdline

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
cmdline.execute("scrapy crawl gjdw_dzsw_spider -a start_time=2019:01:01 -a end_time=2019:12:31 -a type=zygg -a force=''".split())
#cmdline.execute(['scrapy', 'crawl', 'ccgp_search'])
