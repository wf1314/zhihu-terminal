import os
import asyncio
from zhihu_client import ZhihuClient
from zhihu_spider import ZhihuSpider
from setting import USER
from setting import PASSWORD
from utils import print_colour


def start():
    print('************************************')
    print('')


def welcome():
    pass


async def login(user, password):
    client = ZhihuClient(user, password)
    load_cookies = False
    if os.path.exists(client.cookie_file):
        load_cookies = True
    if not load_cookies:
        assert USER and PASSWORD, '未配置账号密码'
    await client.login(load_cookies=load_cookies)
    return client


async def _run():
    try:
        client = await login(USER, PASSWORD)
        spider = ZhihuSpider(client)
        await spider.get_me_info()
        await spider.get_recommend_article()
    except:
        pass
    finally:
        await client.close()

def main():
    ioloop = asyncio.get_event_loop()
    ioloop.run_until_complete(_run())


if __name__ == '__main__':
    main()