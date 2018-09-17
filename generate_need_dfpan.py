# -*- coding: utf-8 -*-
"""
@author: waywaywayw
@date: 2018-09-07
"""

import os
from my_tools.my_files import MyFiles
from jsonDB_myTools.common import MyJsonDB


if __name__ == '__main__':
    # 获取已下载好的文件
    exist_path = os.path.join('E:\\', 'yunfile', '小草版主')
    exist_files = MyFiles(exist_path).fin_files()
    # 读取数据库的资源
    db_path = os.path.join('output', 'db_xiaocao.txt')
    resource_list = MyJsonDB(db_path).resource_list()
    # 需要生成的待下载文件
    save_path = os.path.join('output', 'yunfile_xiaocao.txt')
    save_file = open(save_path, 'w')

    # 挨个判断，如果下载文件不存在，那么写入need_dfpan.txt
    # downed =
    resource_list = list(filter(lambda x: x['name'] not in exist_files, resource_list))
    for idx, resource in enumerate(resource_list):
        if resource.get('yunfile_url'):
            save_file.write(resource['yunfile_url']+'\n')
            print('找到还未下载的资源：', resource)
        elif resource.get('other_url'):
            print('找到还未下载的非yunfile资源：', resource)
        else :
            print('异常的资源..')

    print('写入', save_path, '成功')
    save_file.close()