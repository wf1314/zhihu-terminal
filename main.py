import asyncio
from zhihu_client import ZhihuClient
from zhihu_spider import ZhihuSpider
from setting import USER
from setting import PASSWORD


def start():
    print('************************************')
    print('')


def welcome():
    pass


async def login(user, password):
    client = ZhihuClient(user, password)
    await client.login()
    return client


async def _run():
    client = await login(USER, PASSWORD)
    spider = ZhihuSpider(client)
    await spider.get_me_info()
    await spider.get_recommend_article()


def main():
    ioloop = asyncio.get_event_loop()
    ioloop.run_until_complete(_run())


if __name__ == '__main__':

    main()