
from bs4 import BeautifulSoup
import requests
import time
import datetime
import re
import os
import random

from selenium import webdriver
# 引入配置对象DesiredCapabilities
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from crawler_myTools.selenium_tools.webdriver import MyWebDriver


if __name__ == '__main__':

    driver = MyWebDriver(driver_type=2).webdriver_Chrome()
    # 1. 自动登录
    login_url = 'http://www.yunfile.com/'
    driver.get(login_url)
    # 点击登录按钮
    button = driver.find_element_by_css_selector("#login_a")
    driver.execute_script("$(arguments[0]).click()", button)
    print("点击登录按钮")
    # 输入用户名和密码
    username = 'kingcv'
    passwd = 'selina123'
    driver.find_element_by_css_selector("#login_userid").send_keys(username)
    driver.find_element_by_css_selector("#login_password").send_keys(passwd)
    time.sleep(1)
    # 确认登录
    button = driver.find_element_by_css_selector("#LoginButton")
    driver.execute_script("$(arguments[0]).click()", button)
    time.sleep(1)

    # 2. 访问资源页面
    yunfile_url_list = []
    # 读取需要的资源列表
    need_path = os.path.join('output', 'yunfile_mrskinlover.txt')
    with open(need_path, 'r', encoding='utf8') as fin:
        for line in fin:
            yunfile_url_list.append(line.strip())
    # 遍历下载需要的资源列表
    for yunfile_url in yunfile_url_list:
        def entry_url(driver, yunfile_url):
            while True:
                try:
                    driver.get(yunfile_url)
                    # 如果出现验证码页面，等待5分钟
                    vcode = driver.find_element_by_css_selector("#cvimgvip")
                    print('出现验证码，休息5分钟..')
                    time.sleep(60 * 5)
                except Exception as e:
                    print('未出现验证码')
                    break

        entry_url(driver, yunfile_url)

        # 3. 点击下载
        download_url_elem_list = [
            '#skyblue_content > div.downpage > div > div:nth-child(3) > table > tbody > tr:nth-child(3) > td > table > tbody > tr > td > a',
            '#skyblue_content > div.downpage > div > div:nth-child(3) > table > tbody > tr:nth-child(2) > td > table > tbody > tr > td > a',
            '#skyblue_content > div.downpage > div > div:nth-child(3) > table > tbody > tr:nth-child(1) > td > table > tbody > tr > td > a']
        elem_idx = random.randint(0, len(download_url_elem_list)-1)
        nowTime = time.strftime('%Y%m%d.%H.%M.%S')
        t = driver.get_screenshot_as_file('%s.png' % nowTime)
        print('截图结果%s' % t)
        # 点击某种高速下载按钮
        button = driver.find_element_by_css_selector(download_url_elem_list[0])
        driver.execute_script("$(arguments[0]).click()", button)
        print('已点击下载按钮')
        # button = driver.find_element_by_css_selector(download_url_elem_list[1])
        # driver.execute_script("$(arguments[0]).click()", button)
        # print('再次已点击下载按钮')
        # time.sleep(3)
        # debug
        break

    while True:
        print('等待下载完毕.. 需要手动结束程序..')
        time.sleep(60)
        pass
    pass

