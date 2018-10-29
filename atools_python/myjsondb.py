# -*- coding: utf-8 -*-
"""
@author: weijiawei
@date: 2018-09-06
"""

import os
import json
import pandas as pd
from pandas.io.json import json_normalize


class MyjsonDB(object):
    def __init__(self, db_path, duplicate_key=None, verbose=True):
        """
        初始化数据库，初始化res列表
        :param db_path:
        """
        self._db_path = db_path
        self._resource_dict = dict()    # 核心dict
        self._resource_dict['jsondb'] = []

        self._duplicate_key = duplicate_key # function
        self._duplicate_set = set()

        # 没找到数据库文件
        if not os.path.isfile(db_path):
            open(db_path, 'w', encoding='utf8').close()
            print('json文件 {} 不存在，已新建该文件'.format(db_path))
        else:
            if os.path.getsize(db_path):
                self.load_from_file(db_path)
                print('发现json文件 {} ，已读取内容'.format(db_path))
            else:
                print('发现json文件 {} ，但是文件为空，不读取'.format(db_path))

    def load_from_file(self, db_path, encoding='utf8'):
        """从 其他的json文件 中读取 resource_dict
        """
        with open(db_path, 'r', encoding=encoding) as fin:
            self._resource_dict = json.load(fin)
        return True

    def save_to_file(self, write_mode='w', encoding='utf8', verbose=False):
        """ 保存成 json 文件
        """
        # 写入数据库
        with open(self._db_path, write_mode, encoding=encoding) as fout:
            # 有中文需要：ensure_ascii=False
            json.dump(self._resource_dict, fout, ensure_ascii=False, sort_keys=True)
        return True

    def set_duplicate_key(self, duplicate_key):
        self._duplicate_key = duplicate_key

    def make_duplicate_set(self):
        """重新制作 duplicate_set"""
        self._duplicate_set = set()
        # 遍历 res_dict['db'] 建立判重set
        for resource in self.resource_list:
            self._duplicate_set.add(self._duplicate_key(resource))

    def is_duplicate(self, res):
        """使用 duplicate_set 去判重"""
        if self._duplicate_key(res) in self._duplicate_set:
            return True
        else:
            return False

    def merge(self, res_list, make_dup=True):
        if not self.resource_list: # 为空时直接覆盖
            self._resource_dict['jsondb'] = res_list
            return

        # 先更新 duplicate_set
        if make_dup:
            self.make_duplicate_set()
        # 再合并（同时去重）
        for res in res_list:
            if not self.is_duplicate(res):   # 不重复，才添加
                self.resource_list.append(res)

    def to_excel(self, output_path):
        df = json_normalize(self.resource_list)
        df.to_excel(output_path, index=False)

    @property
    def resource_dict(self):
        return self._resource_dict

    @property
    def resource_list(self):
        return self._resource_dict['jsondb']