# -*- coding: utf-8 -*-
"""
@author: waywaywayw
@date: 2018-09-07
"""

import os
from atools_python.files import MyFiles
from atools_python.myjsondb import MyjsonDB


# 获取已下载好的文件
exist_path = os.path.join('C:\\', 'Users', 'duoyi', 'Documents', 'temp')


def generate_url(project_name):
    # 读取数据库的资源
    db_path = os.path.join('json_db', project_name + '.txt')
    resource_list = MyjsonDB(db_path).resource_list
    # 需要生成的待下载文件
    save_path = os.path.join('output', project_name + '.txt')
    save_file = open(save_path, 'w')

    # 清理已下载好的文件中小于200k的文件
    for exist_file in MyFiles(exist_path):
        if os.path.getsize(exist_file) < 200*1024:
            os.remove(exist_file)

    # 找到 resource_list 中还没下载的资源
    # 1. 去重
    print('找到资源数：', len(resource_list))
    for idx in range(len(resource_list)-1, -1, -1):
        file_name_lower = resource_list[idx]['file_name'].lower()
        file_name = '.'.join(file_name_lower.split('.')[:-1])
        for exist_file in MyFiles(exist_path):
            # 文件已存在 并且 文件大小大于200k
            if file_name in exist_file.lower() and os.path.getsize(exist_file) > 200*1024:
                del resource_list[idx]
    print('过滤name后的资源数：', len(resource_list))
    # 2. 保存
    for idx, resource in enumerate(resource_list):
        if resource.get('yunfile_url'):
            if resource['file_name'] != "":
                save_file.write(resource['yunfile_url'] + '\n')
                print('找到还未下载的资源：', resource)
            else:
                print('不存在name？')
        else:
            print('异常的资源..')

    print('写入', save_path, '成功')
    save_file.close()


if __name__ == '__main__':
    generate_url('guomoo.cc_guomo')