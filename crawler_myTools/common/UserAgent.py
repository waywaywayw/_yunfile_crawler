# -*- coding: utf-8 -*-
"""
@author: weijiawei
@date: 2018-09-04
"""

import random


class UA(object):
    def __init__(self):
        self._ua_common_list = [
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36']
        pass

    def get_random_ua(self):
        # randint函数是两边闭区间
        idx = random.randint(0, len(self._ua_common_list)-1)
        return self._ua_common_list[idx]
