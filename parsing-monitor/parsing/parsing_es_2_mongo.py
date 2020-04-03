# -*- coding: utf-8 -*-

from elasticsearch import Elasticsearch
from elasticsearch import helpers as es_helpers
import flask
import json
import logging
import logging.handlers
import pymongo
import uuid
import time
import threading
from flask_cors import CORS

# 初始化flask对象
app = flask.Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500 Mb limit
CORS(app, supports_credentials=True)
# 监听端口
LISTEN_PORT = 19999

es_host = 'http://192.168.100.166'
es = Elasticsearch(hosts=es_host, port=9200, timeout=15000)

# ========MongoDB parameters========
MONGDB_URI = 'mongodb://admin:123321@192.168.100.176:27017/'
MONGDB_DB_NAME = 'db_trade'
MONGDB_COLLECTION = 't_trade_error_info'
MONGO_CLIENT = None
MONGO_COL_OBJ = None
g_extract_condition = {}

g_thread_info = None

g_worker = None
TIME_STAMP = None
bid_notice_zbgg = ['0101', '0201', '0301', '0401', '0501', '0601', '0701']
bid_notice_zjjg = ['0102', '0202', '0302', '0402', '0502', '0602', '0702']

_doc_type = ["notice_countryAssets", "notice_engineer", "notice_land", "notice_other", "notice_purchase"]


@app.route('/es/parsing/data', methods=['POST'])
def build_app_request():
    """
    响应HTTP 请求
    :return:
    """
    global g_worker
    _ret = g_worker.handle_request(flask.request)
    return _ret.to_string()


class Response:
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg

    def to_string(self):
        return json.dumps({
            'code': self.code,
            'msg': self.msg
        }, ensure_ascii=False)


class Worker:
    def __init__(self):
        self.method_map = {
            # 'reqGetEsParsingInfo': _get_paring_info,
            'reqGetMongoErrorInfo': get_mongo_info,
        }

    @staticmethod
    def __parse_request_(data):
        """
        parse flask data or mqtt data
        :param data:
        :param request_type:
        :return:
        """
        _method, _payload = None, None

        try:
            if data.form and 'method' in data.form:
                logging.info("receive form data")
                # form request
                _method = data.form['method']
                _payload = data.form['payload']
            elif data.data:
                logging.info("receive json data")
                # json request
                _req = json.loads(data.data)
                if 'method' in _req and 'payload' in _req:
                    _method = _req['method']
                    _payload = _req['payload']
        except:
            logging.exception('__parse_request_ failed')

        return _method, _payload

    # 校验请求参数
    def handle_request(self, data):

        _method, _payload = self.__parse_request_(data)

        if _payload is None or _method is None:
            _resp = Response(501, [])
        elif _method not in self.method_map:
            _resp = Response(404, [])
        else:
            logging.info('receive method |{}| payload |{}|'.format(_method, _payload))
            _resp = self.method_map[_method](_payload)

        return _resp


# 向MongoDb插入异常数据
def add_error_to_mongo(hit):
    global g_extract_condition
    # mongoDb 引用
    global MONGO_COL_OBJ

    g_extract_condition = {"_id": str(uuid.uuid1()), "_source": hit}

    MONGO_COL_OBJ.insert_one(g_extract_condition)


# 获取mongodb数据
def get_mongo_info(payload):
    global g_extract_condition
    # mongoDb 引用
    global MONGO_COL_OBJ

    _result = None
    resp_result = []
    g_extract_condition = {}

    _page_num = '' if 'pageNum' not in payload else payload['pageNum']
    _page_size = '' if 'pageSize' not in payload else payload['pageSize']

    skip = _page_size * (_page_num - 1)

    _result = MONGO_COL_OBJ.find(g_extract_condition).limit(_page_size).skip(skip)
    for res in _result:
        resp_result.append(res)
    _resp = Response(200, resp_result)
    return _resp


# 中标结果
class filterErrorInfoZbjg(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    # 中标公告中中标金额为空/0，中标人名称为空的数据，作为异常数据
    # 查询
    def _query_by_es_and_add_2_Mongo(self):
        global es_host
        global es
        global _doc_type
        global bid_notice_zbgg
        global bid_notice_zjjg
        _index = "pub_res"

        _project_query_1 = {
            "query": {
                "terms": {
                    "_type": [
                        "notice_countryAssets",
                        "notice_engineer",
                        "notice_land",
                        "notice_other",
                        "notice_purchase"
                    ]
                }
            }
        }

        # scroll
        res1 = es_helpers.scan(es,
                               query=_project_query_1,
                               index="pub_res",
                               doc_type=_doc_type,
                               # preserve_order=True
                               # sort="create_date:asc",
                               )

        for hit in res1:
            hit_content_text = hit['_source'].copy()
            hit_content_text['content_text'] = ''
            # 招标公告 中预算金额和采购人名称为空的
            if hit_content_text['info_type'] in bid_notice_zbgg:
                if 'budget_price' in hit['_source']:
                    # 预算金额
                    if hit_content_text['budget_price'] is None or hit_content_text['budget_price'] == 0:
                        add_error_to_mongo(hit_content_text)
                else:
                    add_error_to_mongo(hit_content_text)
                if 'tender_org_name' in hit['_source']:
                    if hit_content_text['tender_org_name'] is None or hit_content_text['tender_org_name'] == '':
                        add_error_to_mongo(hit_content_text)
                else:
                    add_error_to_mongo(hit_content_text)
            # 招标结果
            if hit_content_text['info_type'] in bid_notice_zjjg:
                if 'bid_price' in hit['_source']:
                    if hit_content_text['bid_price'] is None or hit_content_text['bid_price'] == 0:
                        add_error_to_mongo()
                else:
                    add_error_to_mongo(hit_content_text)
                if 'bid_org_name' in hit['_source']:
                    if hit_content_text['bid_org_name'] is None or ['bid_org_name'] == '':
                        add_error_to_mongo()
                else:
                    add_error_to_mongo()

            # 判断重复
            if 'tender_org_name' in hit['_source'] and 'bid_org_name' in hit['_source'] and 'tender_agency_name' in \
                    hit['_source']:
                # 判断 两两是否相同(重复)
                # 招标人名称 大于1
                a = hit_content_text['tender_org_name'].size() > 1
                # 招标代理机构名称 大于1
                b = hit_content_text['tender_agency_name'].size() > 1
                # 招标人编码 大于1 个
                c = hit_content_text['tender_org_code'].size() > 1
                # 招标代理机构编码 大于 1
                d = hit_content_text['tender_agency_code'].size() > 1
                # 招标人名称和中标人名称相同
                e = hit_content_text['tender_org_name'] == hit_content_text['bid_org_name']
                # 招标人名称和招标代理机构名称相同
                f = hit_content_text['tender_org_name'] == hit_content_text['tender_agency_name']
                # 中标人名称和招标代理机构名称相同
                g = hit_content_text['bid_org_name'] == hit_content_text['tender_agency_name']
                if a or b or c or d or e or f or g:
                    add_error_to_mongo(hit_content_text)
            else:
                # 没有 tender_org_name ，bid_org_name ， tender_agency_name 字段，算作异常
                add_error_to_mongo(hit_content_text)
            # 判断多个数值
            if 'tender_org_code' in hit['_source'] and 'bid_org_code' in hit['_source'] and 'tender_agency_code' in \
                    hit['_source']:
                a1 = hit_content_text['tender_org_code'] == hit_content_text['bid_org_code']
                b1 = hit_content_text['tender_org_code'] == hit_content_text['tender_agency_code']
                c1 = hit_content_text['bid_org_code'] == hit_content_text['tender_agency_code']
                if a1 or b1 or c1:
                    add_error_to_mongo(hit_content_text)

    def run(self):
        MONGO_COL_OBJ.drop()
        self._query_by_es_and_add_2_Mongo()
        MONGO_CLIENT[MONGDB_DB_NAME]["t_trade_error_info"]
        time.sleep(30 * 60)


def init():
    global g_worker

    global MONGDB_URI
    global MONGDB_DB_NAME
    global MONGDB_COLLECTION
    global MONGO_CLIENT
    global MONGO_COL_OBJ
    global KAFKA_BOOTSTRAP_SERVERS
    global KAFKA_PRODUCER
    global EXTRACT_VERSION

    g_worker = Worker()
    # 初始化 MongoDB client
    MONGO_CLIENT = pymongo.MongoClient(MONGDB_URI)
    MONGO_COL_OBJ = MONGO_CLIENT[MONGDB_DB_NAME][MONGDB_COLLECTION]


def main_entry():
    """
        主函数入口
        :return:
        """
    global LISTEN_PORT
    global g_thread_info
    # 调用初始化方法
    init()
    # 开启线程
    # g_thread_info = filterErrorInfoZbgg()
    # g_thread_info.start()
    g_thread_info = filterErrorInfoZbjg()
    g_thread_info.start()
    # 启动接口
    app.run(host='0.0.0.0', port=LISTEN_PORT)


if __name__ == '__main__':
    main_entry()
