
import os, re
from bs4 import BeautifulSoup
import requests

from selenium import webdriver
# 引入配置对象DesiredCapabilities
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from my_tools.my_files import MyFiles

proxies = {
  'http': 'http://127.0.0.1:60562',
  'https': 'https://127.0.0.1:60562',
}


def get_exist_files(exist_path):
    return MyFiles(exist_path).fin_files()

# 设置模拟浏览器参数
def webdriver_Chrome():
    driver = None
    try:
        # 开启配置项chrome_options
        chrome_options = webdriver.ChromeOptions()
        # 禁用加载图片
        # prefs = {"profile.managed_default_content_settings.images": 2}
        prefs = {
            'profile.default_content_setting_values': {
                'images': 2,  # 不加载图片
                'javascript': 2,  # 不加载JS
            }
        }
        chrome_options.add_experimental_option("prefs", prefs)
        # 无头模式
        chrome_options.add_argument('--headless')
        # 其他的参考：https://blog.csdn.net/zwq912318834/article/details/78933910

        # 创建浏览器
        driver = webdriver.Chrome(chrome_options=chrome_options, executable_path = os.path.join('Scripts', 'chromedriver.exe'))
        # 根据桌面分辨率来定，主要是为了抓到验证码的截屏
        # browser.set_window_size(configure.windowHeight, configure.windowWidth)

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

    except Exception as e:
        print('异常原因%s' % e)
        pass
    return driver

def filter_exist(dfpan_list):
    driver = webdriver_Chrome()
    if not driver:  print('创建浏览器异常！')

    # 过滤掉已经下载好的文件的dfpan地址列表
    for idx, dfpan_url in enumerate(dfpan_list):
        driver.get(dfpan_url)
        # print(driver.title)
        res_name = driver.title
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

        if res_name in exist_files:
            dfpan_list.pop(idx)



if __name__ == '__main__':
    # 获取已下载好的文件
    exist_path = os.path.join('exist/')
    exist_files = get_exist_files(exist_path)
    # 保存(追加)dfpan地址列表
    save_path = os.path.join('output', 'need_dfpan.txt')
    output_file = open(save_path, 'w', encoding='utf8')

    beg_page = 1
    end_page = 2
    # 遍历整个blog所有的页面
    for page in range(beg_page, end_page):
        # 填好url
        url = 'http://mkskinlover.tumblr.com/'
        real_url = url+'page/'+str(page)


        # 请求url
        response = requests.get(real_url, proxies=proxies)

        # 找到response中所有的dfpan地址列表
        # dfpan_list = ['http://page2.dfpan.com/fs/3k2i3n1g7c6v339/', 'http://page2.dfpan.com/fs/bkeidncgcc4vdf9/']
        dfpan_list = []
        elem_dfpan = response.findAll("", {})
        print('page %d, dfpan_list len : %d'%(page, len(dfpan_list)) )

        # 过滤掉已存在的文件
        filter_exist(dfpan_list)

        # 保存需要的dfpan
        print('page %d, filterd dfpan_list len : %d' % (page, len(dfpan_list)))
        output_file.write('\n'.join(dfpan_list))

    output_file.close()


