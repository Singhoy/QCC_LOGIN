# python3.7
import asyncio
import re
from random import randint
from tkinter import Tk

from pyppeteer import launch

__author__ = """Singhoy Choi"""
__Link__ = """https://github.com/Singhoy/QCC_LOGIN"""
CACHE = r".\pycache"


def screen_size():
    tk = Tk()
    width = tk.winfo_screenwidth()
    height = tk.winfo_screenheight()
    tk.quit()
    return width, height


async def new_browser():
    print("new_browser")
    return await launch(
        {'headless': False, "userDataDir": CACHE, 'dumpio': True, 'devtools': True,
         'slowMo': 3, 'logLevel': 'WARNING',
         'args': ['--no-sandbox', '--start-maximized', '--disable-infobars']
         }
    )


async def close_other(browser, page):
    # 关闭其他无关页面
    for _ in await browser.pages():
        if _ != page:
            await _.close()


async def login(user_name, pass_word):
    """
    自动登录企查查
    :param user_name: 用户名
    :param pass_word: 密码
    :return: 登录后的cookies --> str, 或者错误代码 --> int
    """
    _browser = await new_browser()
    _page = await _browser.newPage()
    await _page.setUserAgent(
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36")
    width, height = screen_size()
    await _page.setViewport({'width': width, 'height': height})
    await _page.setJavaScriptEnabled(True)
    await _page.evaluate("""
        () =>{
            Object.defineProperties(navigator,{
                webdriver:{
                get: () => false
                }
            })
        }
    """)
    try:
        await _page.goto("https://www.qichacha.com", timeout=0)
        await close_other(_browser, _page)
        await _page.click(".navi-btn", {"delay": 10})
        await asyncio.sleep(1)
        await _page.click("#normalLogin", {"delay": 10})
        await asyncio.sleep(1)
        await _page.type("#nameNormal", user_name, {"delay": 10})
        await _page.type("#pwdNormal", pass_word, {"delay": 10})
        await wait_slide(_page)
        w = width * 0.8
        await slide_block(_page, w)
        t = await _page.content()
        r_t = re.findall("验证通过", t)
        if r_t:
            print("点击登录")
            await _page.click('#user_login_normal > button', {"delay": 100})
            cookies = await make_cookies(_page)
        else:
            cookies = 400
        await asyncio.sleep(5)
    except Exception as e:
        print(e)
        cookies = 400
    finally:
        await _browser.close()
    return cookies


async def slide_block(page, width):
    # 自动拖动滑块，超过9次还没通过则验证失败
    regex = re.compile('验证通过')
    tmp = 0
    while tmp < 9:
        slider = await page.Jx("//div[@class='nc_scale']/span")
        print(slider)
        await slider[0].hover()
        print("move")
        await page.mouse.down()
        await page.mouse.move(width, 0, {"steps": randint(80, 120)})
        await page.mouse.up()
        await asyncio.sleep(3)
        t = await page.content()
        r_t = regex.findall(t)
        if r_t:
            print(r_t)
            break
        try:
            print("点击刷新")
            await page.click(".nc-lang-cnt > a")
        except Exception as e:
            if "No node found for selector: .nc-lang-cnt > a" == e:
                print(e)
                break
        await asyncio.sleep(1)
        tmp += 1


async def make_cookies(page):
    # 提取cookies
    cookie_list = await page.cookies()
    cookies = "".join(f"{_.get('name')}={_.get('value')}; " for _ in cookie_list)
    return cookies.strip()


async def wait_slide(page):
    # 等待滑块刷新出来
    regex = re.compile(r"请按住滑块，拖动到最右边")
    tmp = 0
    while tmp < 9:
        try:
            await page.waitForXPath("//div[@class='nc_scale']/span")
            break
        except Exception as e:
            print(e)
            p = await page.content()
            a = regex.findall(p)
            if not a:
                try:
                    await page.click(".nc-lang-cnt > a")
                except Exception as e:
                    if "No node found for selector: .nc-lang-cnt > a" == e:
                        print(e)
                        break
        tmp += 1


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    user = input("输入用户名：")
    pwd = input("输入密码：")
    cookie = loop.run_until_complete(login(user, pwd))
    print(cookie)
