# -*- coding: utf-8 -*-
"""
@author: waywaywayw
@date: 2018-10-18
"""
import os
import re
import requests
from bs4 import BeautifulSoup

from atools_crawler.selenium.webdriver import MyWebDriver
from atools_python.myjsondb import MyjsonDB
from atools_crawler.module.template import (
    send_requests,
)


debug = False
# 请求头(改改host)   NEED DO
headers = {'Connection': 'Keep-Alive'
           # ,'Host': 'zhannei.baidu.com'
           , 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063'}

# 获取当前路径
current_path = os.path.dirname(os.path.abspath(__file__))
# 初始化jsondb
jsondb_path = os.path.join('..', 'json_db', 'guomoo.cc_guomo.txt')
jsondb = MyjsonDB(jsondb_path, duplicate_key=lambda x: x['yunfile_url'])
jsondb.make_duplicate_set()


def process_resource_list_page(start_url):
    """
    从start_url页面获取所有资源页面列表。
    :return 资源页面列表。dict格式，形如： resource_dict = [ {'url':'http:www.emmm.com', 'title':'emm'}, {'url':'http:www.233.com', 'title':'233'}]
    """
    def _parse_html(page_source, debug=False):
        """分析页面源代码，获取resourcePage_list  NEED DO --->
        """
        profile_dir = r'C:\Users\duoyi\AppData\Local\Google\Chrome\User Data'
        my_driver = MyWebDriver(
            params={'headless': True, 'local_config': True, 'profile_dir': profile_dir})
        # my_driver = MyWebDriver()
        driver = my_driver.real_driver()
        ret_list = []
        # 创建soup
        soup = BeautifulSoup(page_source, 'html.parser')
        # 找到资源页列表
        resource_list_elem = soup.findAll('div', {'class': "post"})
        # 获取resourcePage
        for idx, resource_elem in enumerate(resource_list_elem):

            # resource_elem = resource_elem.find('a', {'rel': 'bookmark'})
            # 获取resource的各种属性
            # dict格式. title项必须有, url项应该有，其他项可选
            # 获取title
            title = resource_elem.find('h2', {'class': 'title'}).get_text().strip()

            # 获取yunfile_url
            href_list_elem = resource_elem.findAll('strong')[1:]
            for href_elem in href_list_elem:    # 遍历并访问每个yunfile_url
                res = dict()
                res['title'] = title
                yun_url = href_elem.find('a')['href']
                res['yunfile_url'] = yun_url
                # 判重
                if jsondb.is_duplicate(res):
                    print('发现重复项:', res['title'])
                    continue
                # 获取 real_url
                try:
                    my_driver.get(res['yunfile_url'])
                except:
                    print('md 又超时了')
                    exit(1)
                    # driver.execute_script('window.stop()')  # 当页面加载时间超过设定时间，通过执行Javascript来stop加载，即可执行后续动作
                print('yunfile_url访问结束：', res['title'])
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
                # 保存构造好的resourcePage
                ret_list.append(res)
            if debug:
                break
        driver.quit()
        return ret_list

    page_source = send_requests(start_url)
    resource_list = _parse_html(page_source)
    return resource_list


def work(url):
    """爬虫主流程。
    遍历所有资源，保存在一个jsondb中。（只使用json）
    """
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
    for page in range(start_page, end_page + 1):
        print('--- 第{}页 ---'.format(page))
        # try:
        work(url.format(page))
        # except Exception as e:
        #     print('出现异常：', e)
        #     print('当前page:{}, 有可能是已到最后一页'.format(page))
        #     break
        if debug:
            break

    excel_output_path = os.path.join('..', 'output', 'guomoo.cc_guomo.xlsx')
    jsondb.to_excel(excel_output_path)

if __name__ == '__main__':
    # 翻页模式. 设置开始页和结束页   NEED TO
    start_page, end_page = 1, 1
    url = 'https://www.guomoo.cc/category/guomo/page/{}'
    page_turning_mode(url, start_page, end_page)
