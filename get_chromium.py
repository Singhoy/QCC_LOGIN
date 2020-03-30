# 获取chromium下载地址
import pyppeteer.chromium_downloader

print(f"chromedriver默认存储路径：{pyppeteer.chromium_downloader.chromiumExecutable.get('win64')}")
print(f"win64平台下载链接为：{pyppeteer.chromium_downloader.downloadURLs.get('win64')}")
print("如上面链接下载的无法启动，请手动寻找与本机chrome相匹配的chromedriver版本，http://chromedriver.storage.googleapis.com/index.html")
