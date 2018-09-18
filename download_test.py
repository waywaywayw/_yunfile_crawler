from selenium import webdriver
# 引入配置对象DesiredCapabilities

import pytesseract
from bs4 import BeautifulSoup
import requests
import time
from PIL import Image
import datetime
import re
import os

from selenium import webdriver
# 引入配置对象DesiredCapabilities
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


cur_work_window = ""


# 设置模拟浏览器参数
def getPageSource(givenURL) :
    # test...............
    # 模拟浏览器..获取页面...
    # PhantomJS 的参数设置----------------------------------------------------------------------------------------->
    # 定义配置字典..
    # dcap = dict(DesiredCapabilities.PHANTOMJS)
    # # 从USER_AGENTS列表中随机选一个浏览器头，伪装浏览器
    # ua = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
    # dcap["phantomjs.page.settings.userAgent"] = ua
    # # 不载入图片，爬页面速度会快很多
    # dcap["phantomjs.page.settings.loadImages"] = True
    # 设置代理
    # service_args = ['--proxy=127.0.0.1:4860', '--proxy-type=socks5']

    # 打开带配置信息的phantomJS浏览器
    PhantomJSPath = ''
    # driver = webdriver.PhantomJS(desired_capabilities=dcap)
    # PhantomJS 的参数设置----------------------------------------------------------------------------------------->
    # profile_dir = r"C:\Users\Administrator\AppData\Roaming\Mozilla\Firefox\Profiles\jrukv9ya.default"
    # profile = webdriver.FirefoxProfile(profile_dir)

    while True:
        try :
            profile = webdriver.FirefoxProfile()
            # profile.set_preference('permissions.default.image', 2)  # 某些firefox只需要这个
            profile.set_preference('browser.download.dir', 'E:\\')
            profile.set_preference('browser.download.folderList', 2)
            profile.set_preference('browser.download.manager.showWhenStarting', False)
            profile.set_preference('browser.helperApps.neverAsk.saveToDisk',
                                   'application/rar;application/octet-stream;application/zip')
            # 禁用flash
            profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')

            driver = webdriver.Firefox(firefox_profile=profile)
            # test..
            # driver.get('http://sahitest.com/demo/saveAs.htm')
            # driver.find_element_by_xpath('//a[text()="testsaveas.zip"]').click()
            # time.sleep(3)

            # 设置10秒页面超时返回，类似于requests.get()的timeout选项，driver.get()没有timeout选项
            driver.implicitly_wait(10)
            #  以前遇到过driver.get(url)一直不返回，但也不报错的问题，这时程序会卡住，设置超时选项能解决这个问题。
            driver.set_page_load_timeout(60)
            # 设置10秒脚本超时时间
            driver.set_script_timeout(20)

            if downdowndown(driver, givenURL) is True :
                break
        except Exception as e :
            print('异常原因%s' %e)
            # clear_page(cur_work_window, driver)
    return


def downdowndown(driver, givenURL) :
    driver.get(givenURL)
    # time.sleep(1)
    # driver.maximize_window()  # 将浏览器最大化
    # driver.maximize_window()
    print(driver)

    # 确定工作页面
    work_window = None
    all_handles = driver.window_handles
    print('当前的句柄数 : ' + str(len(all_handles)))
    for handle in all_handles:
        driver.switch_to.window(handle)
        if driver.current_url.find('.dfpan.com') != -1:  # 找到了
            work_window = handle
        else:
            driver.close()
    if not work_window:
        print('没找到工作页面?????')
        return
    driver.switch_to.window(work_window)
    global cur_work_window
    cur_work_window = work_window

    print("当前工作的页面URL ： " + driver.current_url)

    # 开始操作
    print('开始操作')
    try :
        # 0判断是否键入限制
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        interval_div = soup.find('div', {'id': 'interval_div'})

        if  interval_div != None and interval_div.attrs['style'] != 'display: none;':
            print('已进入限制状态.. 还需等待' + str(driver.find_element_by_css_selector('#down_interval_tag').text) + '分钟..')
            time.sleep(int(driver.find_element_by_css_selector('#down_interval_tag').text) *60)

        # 1点击
        button = driver.find_element_by_css_selector("#inputDownWait>input")
        driver.execute_script("$(arguments[0]).click()", button)
        print("点击普通下载")
        time.sleep(1)
        clear_page(work_window, driver)

        # 2关闭登陆框
        button = driver.find_element_by_css_selector("#login_registBox2>div.dialog_title>span.ui_dialog_close")
        driver.execute_script("$(arguments[0]).click()", button)
        print("关闭登陆框")

        # 3获取验证码图片
        #driver.get_screenshot_as_file('vcode.png')
        imgelement = driver.find_element_by_css_selector('#cvimg2')
        imgelement.screenshot('real_code.png')

        # 用pytesseract库识别验证码
        code_img = Image.open('real_code.png')
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
        tessdata_dir_config = '--tessdata-dir "C:\\Program Files (x86)\\Tesseract-OCR\\tessdata" digits'
        code_text = pytesseract.image_to_string(code_img, config=tessdata_dir_config).replace(' ', '')  # 使用image_to_string识别验证码
        print('猜测 code_text : ' + code_text)
        if len(code_text) != 4  :
            print('识别验证码长度错误.. 准备刷新页面..')
            # 等待刷新..
            # driver.refresh()
            time.sleep(1)
            return False

        vcode = code_text
        #vcode = input("enter vcode : ")
        print("获取验证码over")

        # 向输入框中输入验证码
        input_code = driver.find_element_by_css_selector("#vcode").send_keys(vcode)
        time.sleep(1.5)
        button = driver.find_element_by_css_selector("#slow_button")
        driver.execute_script("$(arguments[0]).click()", button)
        print("输入验证码over")
        time.sleep(1)
        nowTime = time.strftime('%Y%m%d.%H.%M.%S_wait')
        t = driver.get_screenshot_as_file('%s.jpg' % nowTime)
        clear_page(work_window, driver)

        wait_div_flag = False
        while True :
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            wait_div = soup.find('div', {'id':'wait_div'})
            interval_div = soup.find('div', {'id':'interval_div'})
            putong_button = soup.find('div', {'id':'inputDownWait'})

            if putong_button!=None and interval_div.attrs['style'] !='display: none;' :
                print('又出现了普通下载按钮.. 应该是验证码识别错了.. 重新来一次.. ')
                # 等待刷新..
                time.sleep(1)
                return False
            elif soup.find('div', {'id':'premium_div', 'style':"display: ;"}) :
                if wait_div_flag is False :
                    print('无操作的正常页面..')
            elif wait_div!=None and wait_div.attrs['style'] !='display: none;' :
                print('已输入验证码.. 正在等待'+str(soup.find('span', {'id':'wait_span'}).get_text())+'秒..')
            elif interval_div!=None and interval_div.attrs['style'] !='display: none;' :
                print('已进入限制状态.. 还需等待' + str(driver.find_element_by_css_selector('#down_interval_tag').text) + '分钟..')
                time.sleep(60)
            else :
                print('??是进入了错误还是可以下载了！？')
                button = driver.find_element_by_css_selector('#downbtn > a:nth-child(2)')
                # driver.execute_script("$(arguments[0]).click()", button)
                print('开始下载啦！！')
                break
            time.sleep(1)
            clear_page(work_window, driver)

    except Exception as e :
        print("异常的原因 %s" %e)
        nowTime = time.strftime('%Y%m%d.%H.%M.%S')
        t = driver.get_screenshot_as_file('%s.jpg' %nowTime)
        print( '截图结果%s' %t)
        print(driver.page_source)

    # 开始睡眠...
    print('正在下载..开始睡眠...')
    time.sleep(60*10)
    return True
    # 检查是否需要等待10分钟了..

    # inputDownWait > input
    # 保存页面源代码 (encoding 很重要)
    page_source = driver.page_source
    '''
    with open("page_source.html", 'w', encoding='utf-8') as file:
        file.write(page_source)
    '''
    # 退出模拟浏览器
    # driver.close()
    # driver.quit()
    # 返回页面源代码
    #
    return page_source

# 关掉弹出页面
def clear_page(work_window, driver) :
    cnt = 0
    # 获得当前所有打开窗口的句柄，这里一共就两个句柄。
    all_handles = driver.window_handles
    print('清理垃圾开始！当前的句柄数 : ' + str(len(all_handles)))
    for handle in all_handles:
        if handle != work_window:  # 工作句柄了
            driver.switch_to.window(handle)
            #print("找到垃圾窗口！")
            driver.close()
    print('调回工作窗口!')
    driver.switch_to.window(work_window)


def record(msg="",wechat=False) :
    # 合成信息
    time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    return_msg = "{}  {}".format(time_str, msg)


    # 发送到各个输出端
    print(return_msg)


if __name__ == '__main__':

    # from selenium import webdriver
    #
    # driver = webdriver.Firefox()
    # driver.get('http://www.baidu.com')
    # exit(1)

    while True :
        url = 'http://page2.dfpan.com/fs/cwfd3d1w9b286/'

        print("start run..")
        # 获取页面
        page = ""
        while True :
            try :
                page = getPageSource(url)
                break
            except Exception as e :
                print(e)
                exit(1)
                time.sleep(60)
        print("???")

        # 解析页面
        soup = BeautifulSoup(page, "html.parser")

    pass

