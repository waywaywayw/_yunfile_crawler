# -*- coding: utf-8 -*-
"""
@author: waywaywayw
@date: 2018-10-18
"""
import os
import re
import numpy as np
import pandas as pd
import json
import requests
from bs4 import BeautifulSoup
from pprint import pprint

from atools_crawler.selenium.webdriver import MyWebDriver
from atools_NLP.files import MyFiles, legal_file_name
from atools_jsonDB.myjsondb import MyjsonDB


# 请求头(改改host)   NEED DO
headers = {'Connection': 'Keep-Alive'
           # ,'Host': 'zhannei.baidu.com'
           ,'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063'}
# 获取当前路径
current_path = os.path.dirname(os.path.abspath(__file__))
# 统计资源总数
global resource_cnt
# 爬取数据保存路径  NEED DO
output_path = os.path.join(current_path, '..', 'download_data', 'ted.com')


def get_resourcePage_list(start_url):
    """
    从start_url页面获取所有资源页面列表。
    :return 资源页面列表。dict格式，形如： resource_dict = [ {'url':'http:www.emmm.com', 'title':'emm'}, {'url':'http:www.233.com', 'title':'233'}]
    """
    def _parse_html(page_source):
        """分析页面源代码，获取resourcePage_list  NEED DO --->
        """
        my_driver = MyWebDriver(
            params={'headless': False, 'local_config': True, 'profile_dir': r'C:\Users\duoyi\AppData\Local\Google\Chrome\User Data'})
        # my_driver = MyWebDriver(params={'headless':False, 'ua':True})
        driver = my_driver.real_driver()
        ret_list = []
        # 创建soup
        soup = BeautifulSoup(page_source, 'html.parser')
        # 找到资源页列表
        resource_list_elem = soup.findAll('div', {'class': "post"})
        # 获取resourcePage
        for idx, resource_elem in enumerate(resource_list_elem):
            resource = {}
            # resource_elem = resource_elem.find('a', {'rel': 'bookmark'})
            # 获取resource的各种属性
            # dict格式. title项必须有, url项应该有，其他项可选
            # 获取title
            resource['title'] = resource_elem.find('h2', {'class': 'title'}).get_text().strip()

            # 获取yunfile_url
            href_list_elem = resource_elem.findAll('strong')[1:]
            res = {}
            for href_elem in href_list_elem:    # 遍历并访问每个yunfile_url
                res['yunfile_url'] = href_elem.find('a')['href']

                # 获取real_url
                try:
                    my_driver.get(res['yunfile_url'])
                except:
                    print('md 又超时了')
                    exit(1)
                    # driver.execute_script('window.stop()')  # 当页面加载时间超过设定时间，通过执行Javascript来stop加载，即可执行后续动作
                print('yunfile_url访问结束')
                res['real_url'] = driver.current_url
                res['file_name'] = driver.title
                # 获取file_size
                obj = re.search(r'</span>(.*?)</h2>', driver.page_source)
                try:
                    file_size = obj.group(1)
                    file_size = file_size.split('-')[-1].strip()
                except:  # 文件不存在
                    file_size = -1
                res['file_size'] = file_size
            resource['resource'] = res
            # 保存构造好的resourcePage
            ret_list.append(resource)
            # debug
            break
        driver.quit()
        return ret_list

    # 获取页面源代码(requests系)
    response = requests.get(start_url, headers=headers)
    page_source = response.content.decode('utf8')
    # debug. 将页面源代码写到临时html文件
    # with open('temp.html', 'r', encoding='utf8') as fout:
    #     fout.write(page_source)
    # debug. 直接输出页面源代码
    # pprint(page_source)

    resource_dict = _parse_html(page_source)
    return resource_dict


def get_resource_from_resourcePage(resource):
    """
    从单个资源页面爬取所需的资源。   NEED DO --->
    :return 资源页面的所有资源。dict格式，形如：resource_list = [ {'need_name1':'v1', 'need_name2':'v2'}, {'need_name3':'v3'}]
    """
    pass
    # return resource


def dereplicate():
    """去重"""
    pass

def work(url):
    """爬虫主流程
    """
    jsondb_path = os.path.join('..', 'json_db', 'guomoo.cc_luoli_jsondb.txt')
    jsondb = MyjsonDB(jsondb_path, duplicate_key=lambda x: x['resource']['file_name'])

    # 获取第page页的resourcePage_list.   每个resourcePage有title项和url项
    resource_list = get_resourcePage_list(url)
    # 获取资源列表
    # resource_list = get_resource_from_resourcePage(resourcePage)
    print('获取到的原始资源数量：', len(resource_list))

    # 去重（可选）
    jsondb.make_duplicate_set()
    resource_list = list(filter(lambda x: not jsondb.is_duplicate(x), resource_list))
    # exist_resourcePage = list(MyFiles(output_path).file_name_no_suffix())   # 获取已下载好的文件列表
    # exist_resourcePage = list(map(lambda x: x.split('_')[:-1], exist_resourcePage))  # 取_前面部分
    # for idx in range(len(resource_dict)-1, -1, -1):
    #     res = resource_dict[idx]
    #     raw_name_no_suffix = res[file_name].split('.')[:-1]
    #     if raw_name_no_suffix in exist_resourcePage:    # 如果满足特定条件，就删掉res
    #         resource_dict.pop(idx)
    print('过滤重复后，原始资源数量：', len(resource_list))

    # 当前的 resource_list 与 jsondb 合并
    jsondb.merge(resource_list, make_dup=False)
    print('合并后，目前jsondb的资源数量：', len(jsondb.resource_list))
    # 保存jsondb
    jsondb.save_to_file()
    print('jsondb已保存')
    # print('开始下载...')
    # 遍历resourcePage_list
    # for idx, resourcePage in enumerate(resource_dict):
    #     save_resources(resource_dict, jsondb)
    #     print('第{}个资源下载并保存完毕：{}'.format(idx, resourcePage[file_name]))
    #     # 总资源数+1
    #     global resource_cnt
    #     resource_cnt += 1
        # debug
        # break


def page_turning_mode(start_page, end_page):
    """翻页模式"""
    # 开启访问的URL  NEED DO
    start_url = 'https://www.guomoo.cc/category/luoli/page/{}'
    # 当前页数：page
    for page in range(start_page, end_page + 1):
        print('--- 第{}页 ---'.format(page))
        work(start_url.format(page))
        # debug
        # break


def main():
    global resource_cnt
    resource_cnt = 0
    # 翻页模式. 设置开始页和结束页   NEED TO
    start_page, end_page = 43, 45
    page_turning_mode(start_page, end_page)
    print('运行完毕. 下载的资源总数量：{}'.format(resource_cnt))


if __name__ == '__main__':
    main()
