import os, re
from bs4 import BeautifulSoup
import requests
import json

from crawler_myTools.selenium_tools.webdriver import MyWebDriver

from my_tools.my_files import MyFiles
from json_db.db_common import MyJsonDB

proxies = {
    'http': 'http://127.0.0.1:54422',
    'https': 'https://127.0.0.1:54422',
}


def get_exist_files(exist_path):
    return MyFiles(exist_path).fin_files()


def filter_exist(driver, resource_list, db):
    # 过滤掉已经下载好的文件的dfpan地址列表
    for idx, resource in enumerate(resource_list):
        driver.get(resource['url'])
        # print(driver.title)
        res_name = driver.title
        res_url = driver.current_url
        if res_name in exist_files or db.is_duplicate('name', res_name) or db.is_duplicate('url', res_url):
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
    elem_dfpan = soup.findAll("div", {'class': "copy"})
    for elem in elem_dfpan:
        resource = {}
        # 获取标题和网址
        a_list = elem.findAll('a')
        for a in a_list:
            e_text = a.get_text()
            a_href = a['href']
            # 有特定符号putpan
            if a_href and e_text.find('点击进入下载') < 0 and \
                    (a_href.find('putpan') >= 0 or a_href.find('tadown') >= 0):
                # 获取标题(有可能和资源页面的不符，还需要真实访问一遍）
                resource['name'] = e_text
                # 获取网址
                resource['url'] = a['href']
                break
        # 获取可能的密码
        p_list = elem.findAll('p')
        for p in p_list:
            e_text = p.get_text()
            if e_text.find('密码') >= 0:
                text_l = re.split(r"[:：]", e_text)
                passwd_name = text_l[0]
                passwd_value = ':'.join(text_l[1:])
                resource[passwd_name] = passwd_value
        # add resource
        if resource:
            resource_list.append(resource)

    return resource_list

def load_db(db_path, resource_list):

    pass

def write_to_db(db_path, save_path, resource_list):
    with open(save_path, 'a', encoding='utf8') as save_file, open(db_path, 'a', encoding='utf8') as db_file:
        for res in resource_list:
            save_file.write(res['url'] + '\n')
            db_file.write(json.dumps(res, ensure_ascii=False) + '\n')
            print(json.dumps(res, ensure_ascii=False))


if __name__ == '__main__':
    # 获取已下载好的文件
    # exist_path = os.path.join('F:\\', 'mrskinlover')
    exist_path = os.path.join('H:\\', 'yunfile', 'mrskinlover', 'mrskinlover')
    exist_files = get_exist_files(exist_path)
    # 数据文件的地址
    save_path = os.path.join('output', 'need_dfpan.txt')
    db_path = os.path.join('output', 'db.txt')
    db = MyJsonDB(db_path)
    # test
    # resource_list = [{'url':'开心'}, {'url':'母鸡'}]
    # write_to_db(db_path, save_path, resource_list)

    beg_page = 4
    end_page = 100
    # 遍历整个blog所有的页面
    for page in range(beg_page, end_page):
        # 填好url
        url = 'http://mrskinlover.tumblr.com/'
        real_url = url + 'page/' + str(page)

        # 请求url
        response = requests.get(real_url, proxies=proxies)
        soup = BeautifulSoup(response.text, "html.parser")
        # 得到资源列表
        resource_list = get_resouce_from_page(soup)
        # 初步过滤：名字已存在的res ,丢弃
        resource_list = list(filter(lambda x: not db.is_duplicate('name', x), resource_list))
        print('page %d, resource_list len : %d' % (page, len(resource_list)))

        # 过滤掉已存在的文件
        driver = MyWebDriver(driver_type=2).driver()
        if not driver:  print('创建浏览器异常！')
        filter_exist(driver, resource_list, db)
        driver.close()

        # 保存需要的dfpan
        print('page %d, filterd resource_list len : %d' % (page, len(resource_list)))
        write_to_db(db_path, save_path, resource_list)
