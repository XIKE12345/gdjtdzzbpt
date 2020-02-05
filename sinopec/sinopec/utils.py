import hashlib


class CcgpUtil():
    NOTICE_TYPE_MAPPING = {
        '981': '更正公告',
        '982': '中标公告',
        '974': '公开招标',
        '977': '单一来源',
        '998': '公开招标',
        '999': '单一来源公告和公示',
        '1000': '竞争性谈判',
        '1003': '更正公告',
        '1004': '中标公告',
        '1012': '其它公告',
        '2653': '竞争性磋商',
        '2655': '成交公告',
        '2656': '废标公告',
        '2658': '终止公告'
    }

    @classmethod
    def get_notice_type(cls, type_code):
        """
        根据公告编码返回公告文本类型，如：更正公告
        :param type_code:
        :return:
        """

        if type_code in cls.NOTICE_TYPE_MAPPING:
            return cls.NOTICE_TYPE_MAPPING[type_code]

        return type_code

    @classmethod
    def get_unique_id(cls, plain_text):
        return hashlib.md5(plain_text.encode('utf-8')).hexdigest()
