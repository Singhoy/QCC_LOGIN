# 获取chromium下载地址
import pyppeteer.chromium_downloader

print(f"可执行文件默认路径：{pyppeteer.chromium_downloader.chromiumExecutable.get('win64')}")
print(f"win64平台下载链接为：{pyppeteer.chromium_downloader.downloadURLs.get('win64')}")
