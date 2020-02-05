# -*- coding: utf-8 -*-


import sys
import scrapy
import requests
import json
import base64
import zlib
import time
from enum import Enum

print(sys.version)
print(scrapy)


class ScrawlMode(Enum):
    REAL_TIME = 0
    HISTORY = 1

