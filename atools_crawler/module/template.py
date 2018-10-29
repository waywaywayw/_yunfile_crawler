# -*- coding: utf-8 -*-
"""
@author: weijiawei
@date: 2018/10/29
"""
import os
import re
import json
import requests
from bs4 import BeautifulSoup
from atools_python.files import MyFiles
from atools_python.myjsondb import MyjsonDB


# 请求头(改改host)   NEED DO
headers = {'Connection': 'Keep-Alive'
           # ,'Host': 'zhannei.baidu.com'
           , 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063'}


def send_requests(start_url, my_webDriver=None):
    """发送请求，获取页面源代码"""
    if my_webDriver:  # selenium 系
        driver = my_webDriver.real_driver()
        driver.get(start_url)
        page_source = driver.page_source
    else:  # requests 系
        response = requests.get(start_url, headers=headers)
        # page_source = response.content.decode('utf8')
        page_source = response.text
    # debug. 将页面源代码写到临时html文件
    # with open('temp.html', 'r', encoding='utf8') as fout:
    #     fout.write(page_source)
    # debug. 直接输出页面源代码
    # pprint(page_source)
    return page_source


def _parse_html(page_source):
    """分析页面源代码，获取resourcePage_list  NEED DO --->
    """
    ret_list = []
    # 创建soup
    soup = BeautifulSoup(page_source, 'html.parser')
    # 找到资源页列表
    resource_list_elem = soup.findAll('div', {'class': "post"})     # #######
    # 获取resourcePage
    for idx, resource_elem in enumerate(resource_list_elem):
        resource = {}
        # resource_elem = resource_elem.find('a', {'rel': 'bookmark'})
        # 获取resource的各种属性。  dict格式. title项必须有, url项应该有，其他项可选
        # 获取title
        # resource['title'] = resource_elem.find('h2', {'class': 'title'}).get_text().strip()
        # resource['url'] = resource_elem.find('h2', {'class': 'title'}).get_text().strip()
        # ...
        # 保存构造好的resourcePage
        ret_list.append(resource)
        # debug
        # break
    return ret_list


def _parse_html_get_id(page_source):
    obj = re.search(r'"current_talk":"(\d*?)"', page_source)
    # print(obj.group(1))
    id = obj.group(1)
    return id


def _parse_json(page_source):
    """分析资源json，获取resourcePage_list  NEED DO --->
    """
    # 加载json, data_json是 dict 类型
    data_json = json.loads(page_source)
    # pprint(data_json)
    resource_list = []
    for cues in data_json['paragraphs']:
        for text in cues['cues']:
            sentence = text['text'].strip()
            res = dict()
            # 获取resource的各种属性   to do
            res['language'] = sentence
            resource_list.append(res)
    return resource_list


def process_resource_list_page(start_url, my_webDriver=None):
    """
    处理资源列表页。得到简略资源列表。（只包含少量项：url, title等）
    :return: 简略资源列表 resource_list
    """
    # 解析页面源代码
    def _parse_html(page_source):
        """分析页面源代码，获取resourcePage_list  NEED DO --->
        """
        ret_list = []
        # 创建soup
        soup = BeautifulSoup(page_source, 'html.parser')
        # 找到资源页列表
        resource_list_elem = soup.findAll('div', {'class': "post"})  # #######
        # 获取resourcePage
        for idx, resource_elem in enumerate(resource_list_elem):
            resource = {}
            # resource_elem = resource_elem.find('a', {'rel': 'bookmark'})
            # 获取resource的各种属性。  dict格式. title项必须有, url项应该有，其他项可选
            # 获取title
            # resource['title'] = resource_elem.find('h2', {'class': 'title'}).get_text().strip()
            # resource['url'] = resource_elem.find('h2', {'class': 'title'}).get_text().strip()
            # ...
            # 保存构造好的 resource
            ret_list.append(resource)
            # debug
            # break
        return ret_list

    page_source = send_requests(start_url, my_webDriver)
    resource_list = _parse_html(page_source)
    return resource_list


def process_resource_page(start_url, my_webDriver=None):
    """处理资源页。得到详细资源列表。（包含所需所有项）
    一般是通过请求url项得到资源。
    :return: 详细资源列表 resource_list
    """
    pass


def dereplicate_by_file(exist_path, resource_list, repeat_elem='title'):
    """
    根据已存在的文件（夹）去重。
    :param exist_path: 已存在的文件夹
    :param resource_list: 资源列表
    :param repeat_elem: 资源列表中待保存的文件项
    :return:
    """
    # 只取出文件名部分
    exist_file = set(MyFiles(exist_path).file_name_no_suffix())

    for idx in range(len(resource_list), -1, -1):
        if resource_list[idx][repeat_elem] in exist_file:
            del resource_list[idx]
    return resource_list


def work(url):
    """爬虫主流程。
    遍历所有资源，保存在一个jsondb中。（只使用json）
    """
    jsondb_path = os.path.join('..', 'json_db', 'guomoo.cc_luoli_jsondb.txt')
    jsondb = MyjsonDB(jsondb_path, duplicate_key=lambda x: x['file_name'])

    # 获取第page页的resourcePage_list.   每个resourcePage有title项和url项
    resource_list = process_resource_list_page(url)
    print('获取到的原始资源数量：', len(resource_list))

    # 当前的 resource_list 与 jsondb 合并
    jsondb.merge(resource_list, make_dup=False)
    print('合并后，目前jsondb的资源数量：', len(jsondb.resource_list))

    # 保存jsondb
    jsondb.save_to_file()
    print('jsondb已保存')


def page_turning_mode(url, start_page, end_page):
    """翻页模式"""
    global resource_cnt
    resource_cnt = 0
    # 遍历指定页数
    for page in range(start_page, end_page + 1):
        print('--- 第{}页 ---'.format(page))
        work(url.format(page))
        # debug
        # break
    print('运行完毕. 下载的资源总数量：{}'.format(resource_cnt))


if __name__ == '__main__':
    # 翻页模式. 设置开始页和结束页   NEED TO
    start_page, end_page = 43, 45
    url = 'https://www.guomoo.cc/category/luoli/page/{}'
    page_turning_mode(url, start_page, end_page)
