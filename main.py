import os
import asyncio
from zhihu_client import ZhihuClient
from data_extractor import DataExtractor
from setting import USER
from setting import PASSWORD
from utils import print_colour


def start():
    print('************************************')
    print('')


def welcome():
    pass


def check_setting():
    pass


async def login(user, password):
    """
    登录
    :param user:
    :param password:
    :return:
    """
    client = ZhihuClient(user, password)
    load_cookies = False
    if os.path.exists(client.cookie_file):
        # 如果cookie缓存存在优先读取缓存
        load_cookies = True
    await client.login(load_cookies=load_cookies)
    return client


async def _run():
    client = await login(USER, PASSWORD)
    try:
        check_setting()
        spider = DataExtractor(client)
        await spider.get_self_info()
        await spider.get_recommend_article()
    except Exception as e:
        print_colour(e, colour='red')
    finally:
        await asyncio.sleep(0)
        await client.close()


def main():
    ioloop = asyncio.get_event_loop()
    ioloop.run_until_complete(_run())


if __name__ == '__main__':
    main()