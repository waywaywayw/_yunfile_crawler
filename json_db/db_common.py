# -*- coding: utf-8 -*-
"""
@author: weijiawei
@date: 2018-09-06
"""

import os, re
import json


class MyJsonDB(object):
    def __init__(self, db_path):
        """
        初始化数据库，初始化res列表
        :param db_path:
        """
        self._db_path = db_path
        # self._db_name = db_name
        self._resource_list = self.load_from_db()
        pass

    def is_duplicate(self, key_name, res, res_db=None):
        """
        判重
        :param res: 需要判重的数据
        :param res_db: 资源数据库
        :param key_name: 判重的关键key的name
        :return:
        """
        if not res_db:
            res_db = self._resource_list

        ret = False
        for r in res_db:
            if res==r[key_name]:
                ret = True
        return ret

    def load_from_db(self, encoding='utf8'):
        """
        从db中读取resource_list
        :return:
        """
        resource_list = []
        with open(self._db_path, 'r', encoding=encoding) as fin:
            for line in fin:
                res = json.loads(line.strip())
                resource_list.append(res)
        return resource_list

    def write_to_db(self, save_path, resource_list=None, encoding='utf8', verbose=False):
        """
        将json列表格式的resource_list写入db, 遇到重复的自动不添加
        :param db_path:
        :param resource_list:
        :return: 写入成功，返回True
        """
        if not resource_list:
            resource_list = self._resource_list
        # 写入数据库
        with open(save_path, 'w', encoding=encoding) as db_file:
            for res in resource_list:
                # 有中文需要：ensure_ascii=False
                res_json = json.dumps(res, ensure_ascii=False)
                # 实际写入
                db_file.write(res_json + '\n')
                if verbose:
                    print(res_json)
        return True

    def resource_list(self):
        return self._resource_list