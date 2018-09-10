# -*- coding: utf-8 -*-
"""
@author: waywaywayw
@date: 2018-09-07
"""

import os, re
from bs4 import BeautifulSoup
import requests
import json

from crawler_myTools.selenium_tools.webdriver import MyWebDriver

from my_tools.my_files import MyFiles
from json_db.db_common import MyJsonDB


def filter_exist(driver, resource_list, db):
    # 过滤掉已经下载好的文件的dfpan地址列表
    for idx, resource in enumerate(resource_list):
        driver.get(resource['url'])
        # print(driver.title)
        res_name = driver.title
        res_url = driver.current_url
        if db.is_duplicate('name', res_name) or db.is_duplicate('url', res_url):
            resource_list.pop(idx)
        else:
            resource_list[idx]['name'] = res_name
            resource_list[idx]['url'] = driver.current_url

        # 之前request的版本.. 结果遇到了乱码..
        # response = requests.get(dfpan, proxies=proxies, headers=headers)
        # # <span id="file_show_filename">lf0905-.rar</span>
        # content = response.content.decode("utf8")
        # # debug, 保存内容
        # with open('temp.html', 'wb') as f:
        #     f.write(response.content)
        # # 找到该dfpan对应的文件名
        # searchObj = re.match(r'.*<span id="file_show_filename">(.*?)</span>.*', content, re.DOTALL)
        # res_name = searchObj.group(1)
        # print(res_name)
        # print(res_name.encode('utf8').decode('gb18030'))


def get_resouce_from_page(soup):
    # 找到response中所有的资源
    # dfpan_list = ['http://page2.dfpan.com/fs/3k2i3n1g7c6v339/', 'http://page2.dfpan.com/fs/bkeidncgcc4vdf9/']
    resource_list = []
    elem_dfpan = soup.findAll("div", {'class': "entry_body"})
    for elem in elem_dfpan:
        resource = {}
        # 获取标题和网址
        a_list = elem.findAll('a')
        for a in a_list:
            e_text = a.get_text()
            a_href = a['href']
            # 有特定符号putpan
            if (a_href.find('putpan') >= 0 or a_href.find('tadown') >= 0):
                # 获取网址
                resource['url'] = a['href']
                break
        # 获取可能的密码
        e_text = elem.get_text()
        if e_text.find('解压码') >= 0 and e_text.find('下载教程') >= 0:
            e_text_1 = re.split(r"解压码", e_text)[1]
            e_text_2 = re.split(r"下载教程", e_text_1)[0]
            resource['密码'] = e_text_2.strip()
        # add resource
        if resource:
            resource_list.append(resource)

    return resource_list


def write_to_db(db_path, save_path, resource_list):
    with open(save_path, 'a', encoding='utf8') as save_file, open(db_path, 'a', encoding='utf8') as db_file:
        for res in resource_list:
            save_file.write(res['url'] + '\n')
            db_file.write(json.dumps(res, ensure_ascii=False) + '\n')
            print(json.dumps(res, ensure_ascii=False))


if __name__ == '__main__':
    # 数据文件的地址
    db_path = os.path.join('output', 'db_xiaocao.txt')
    db = MyJsonDB(db_path, new_db=True)

    beg_page = 1
    end_page = 5
    # 遍历整个blog所有的页面
    for page in range(beg_page, end_page):
        # 填好url
        real_url = 'http://xcbz.blog.fc2blog.us/page-{}.html'.format(page)
        # 请求url
        response = requests.get(real_url)
        soup = BeautifulSoup(response.text, "html.parser")
        # 得到资源列表
        resource_list = get_resouce_from_page(soup)
        # 初步过滤：名字已存在的res ,丢弃
        print('page %d, resource_list len : %d' % (page, len(resource_list)))

        # 过滤掉已存在的文件
        driver = MyWebDriver(driver_type=2).driver()
        if not driver:  print('创建浏览器异常！')
        filter_exist(driver, resource_list, db)
        driver.close()

        # 保存需要的dfpan
        print('page %d, filterd resource_list len : %d' % (page, len(resource_list)))
        db.write_to_db(db_path, resource_list, write_mode='a', verbose=True)
