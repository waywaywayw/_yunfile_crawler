
import os, re
from bs4 import BeautifulSoup
import requests

from my_tools.my_files import MyFiles

proxies = {
  'http': 'http://127.0.0.1:60562',
  'https': 'https://127.0.0.1:60562',
}
headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
        , 'Connection': 'keep-alive'
        , 'Host': 'page2.dfpan.com'
        # ,'Accept': 'text / html, application / xhtml + xml, application / xml;    q = 0.9, image / webp, * / *;q = 0.8'
        # ,'Cookie': '__cfduid=dd47fd076c3e54cc53a5d1054db82d6121505225609; PHPSESSID=j31c7qsbkqi22p0019vide6ih0; AGREE_CONSENT=1; _popfired=20; _gat=1; _ga=GA1.2.1458835411.1504142140; _gid=GA1.2.1307652668.1505225547'
    }

def get_exist_files(exist_path):
    return MyFiles(exist_path).fin_files()

def work(resource_url, ):
    pass

def filter_exist(dfpan_list):
    # 过滤掉已经下载好的文件的dfpan地址列表
    for idx, dfpan in enumerate(dfpan_list):
        response = requests.get(dfpan, proxies=proxies, headers=headers)
        # <span id="file_show_filename">lf0905-.rar</span>
        content = response.content.decode("utf8")
        # debug, 保存内容
        with open('temp.html', 'wb') as f:
            f.write(response.content)
        # 找到该dfpan对应的文件名
        searchObj = re.match(r'.*<span id="file_show_filename">(.*?)</span>.*', content, re.DOTALL)
        res_name = searchObj.group(1)
        print(res_name)
        print(res_name.encode('utf8').decode('gb18030'))

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
    end_page = 100
    # 遍历整个blog所有的页面
    for page in range(beg_page, end_page):
        # 填好url

        # 请求url
        # requests.get()

        # 找到response中所有的dfpan地址列表
        dfpan_list = ['http://page2.dfpan.com/fs/3k2i3n1g7c6v339/', 'http://page2.dfpan.com/fs/bkeidncgcc4vdf9/']
        print('dfpan_list len :', len(dfpan_list))

        filter_exist(dfpan_list)

        # 保存需要的dfpan
        print('need dfpan_list len :', len(dfpan_list))
        output_file.write('\n'.join(dfpan_list))

    output_file.close()


