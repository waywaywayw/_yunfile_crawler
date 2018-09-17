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
from jsonDB_myTools.common import MyJsonDB
from crawler_myTools.requests_tools.common_config import MyConfig


def filter_exist(driver, resource_list, db):
    ret_list = []
    # 过滤掉已经下载好的文件的dfpan地址列表
    for idx, resource in enumerate(resource_list):
        # 处理没有url的resource
        if resource.get('yunfile_url'):
            print('有yunfile的资源:', resource)
        elif resource.get('other_url'):
            print('无yunfile的资源:', resource)
        else:
            print('遇到异常的资源..')
            continue

        if resource.get('yunfile_url'):
            driver.get(resource['yunfile_url'][0])
            # print(driver.title)
            resource['name'] = driver.title
            resource['yunfile_url'] = driver.current_url
            if db.is_duplicate('name', resource) or db.is_duplicate('yunfile_url', resource):
                continue
            else:
                ret_list.append(resource)
        elif resource.get('other_url'):
            driver.get(resource['other_url'])
            # print(driver.title)
            resource['name'] = driver.title
            resource['other_url'] = driver.current_url
            #
            if db.is_duplicate('name', resource):
                continue
            else:
                ret_list.append(resource)
        else :
            print('未知异常！')
    return ret_list
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

def get_resouce_from_resouce_page(url):
    # 请求url
    response = requests.get(real_url, proxies=MyConfig.proxies, headers=MyConfig.headers)
    soup = BeautifulSoup(response.text, "html.parser")
    # 找到response中所有的资源
    # dfpan_list = ['http://page2.dfpan.com/fs/3k2i3n1g7c6v339/', 'http://page2.dfpan.com/fs/bkeidncgcc4vdf9/']
    resource_list = []
    elem_dfpan = soup.findAll("div", {'class': "post-panel"})
    for elem in elem_dfpan:
        elem = elem.find("div", {'class': "copy"})
        resource = {}
        resource['yunfile_url'] = []
        # 获取标题和网址
        if not elem:
            print('无资源存在')
            continue
        a_list = elem.findAll('a')
        for a in a_list:
            e_text = a.get_text()
            a_href = a['href']
            # 有特定符号putpan
            # print(e_text)
            # print(a_href)
            # yunfile
            if a_href and \
                    (a_href.find('putpan') >= 0 or a_href.find('tadown') >= 0 or a_href.find('filemarkets') >= 0
                     or a_href.find('yfdisk') >= 0 or a_href.find('5xpan') >= 0 or a_href.find('skpan') >= 0 or
                     a_href.find('pwpan') >= 0 or a_href.find('gmpan') >= 0 or a_href.find('dix3') >= 0 or a_href.find('srcpan') >= 0):
                # 获取标题(有可能和资源页面的不符，还需要真实访问一遍）
                resource['name'] = e_text
                # 获取网址
                resource['yunfile_url'].append(a['href'])
            # other
            if not resource.get('yunfile_url') and a_href and \
                    (a_href.find('678pan') >= 0 or a_href.find('yousuwp') >= 0):
                # 获取标题(有可能和资源页面的不符，还需要真实访问一遍）
                resource['name'] = e_text
                # 获取网址
                resource['other_url'] = a['href']
        # 获取可能的密码
        p_list = elem.findAll('p')
        for p in p_list:
            e_text = p.get_text()
            if e_text.find('密码') >= 0 or e_text.find('密碼') >= 0:
                e_text = e_text.split()[-1]
                text_l = re.split(r"[:：]", e_text)
                passwd_name = text_l[0].strip()
                passwd_value = ':'.join(text_l[1:]).strip()
                resource[passwd_name] = passwd_value
                break
        # add resource
        if resource:
            resource_list.append(resource)

    return resource_list


if __name__ == '__main__':
    # 数据文件的地址
    db_path = os.path.join('output', 'db_mrskinlover.txt')
    db = MyJsonDB(db_path)
    print('载入数据库..')
    print('已有{}个资源'.format(len(db.resource_list())))
    # test
    # resource_list = [{'url':'开心'}, {'url':'母鸡'}]
    # write_to_db(db_path, save_path, resource_list)

    beg_page = 15
    end_page = 25
    # 遍历整个blog所有的页面
    for page in range(beg_page, end_page):
        # 填好url
        url = 'http://mrskinlover.tumblr.com/'
        real_url = url + 'page/' + str(page)
        # 得到资源列表
        resource_list = get_resouce_from_resouce_page(real_url)
        # 初步过滤：名字已存在的res ,丢弃
        resource_list = list(filter(lambda x: not db.is_duplicate('name', x), resource_list))
        print('\npage {}, 初步过滤后，当前页的资源共{}个.'.format(page, len(resource_list)))
        if len(resource_list)==0:
            continue

        # 过滤掉已存在的文件
        driver = MyWebDriver(driver_type=2).driver()
        if not driver:  print('创建浏览器异常！')
        resource_list = filter_exist(driver, resource_list, db)
        driver.close()
        # print
        print('去重后，当前页的资源共{}个：'.format(len(resource_list)))
        for res in resource_list:
            print(res)

        # 保存需要的dfpan
        print('开始写入数据库')
        # 更新数据库里面的资源列表
        db.extend_resource_list(resource_list)
        db.write_to_db(write_mode='w', verbose=False)

    print('目前数据库的资源数：{}'.format(len(db.resource_list())))