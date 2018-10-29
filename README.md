
## 说明
crawler文件夹 存放爬虫

## 目前爬取字段的想法
dict形式存储

- jsondb : [
    - {
        - title : ""   # 原始标题
        - yunfile_url     # 云盘链接 
        - （可选）other_url  # 其他网盘的链接
        - （可选）passwd    # 密码
        - real_url  # 云盘真实链接（将 yunfile_url 放到真实浏览器后得到的链接）
        - file_name # 云盘显示的文件名
        - file_size # 云盘显示的文件大小
    - }, {..}, {..}, ..
- ]