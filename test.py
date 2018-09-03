

import re


# content = str('ss<span id="file_show_filename">sdf </span>33')
with open('temp.html', 'r', encoding='utf8') as f:
    t = f.read()
    # t = '<!-- <span class="file_size_span">文件大小:123.37 MB</span> -->\n<h2 class="file_title" style="margin-bottom:0px;">&nbsp;文件下载&nbsp;&nbsp;<span id="file_show_filename">ÿõ£ª£¦¾½áòá</span> - 123.37 MB </h2>'
    # print(t)
    searchObj = re.match(r'.*<span id="file_show_filename">(.*?)</span>.*',t, re.DOTALL)
    res_name = searchObj.group(1)
    print(res_name)