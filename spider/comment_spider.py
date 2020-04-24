from utils import SpiderBaseclass


class CommentSpider(SpiderBaseclass):
    """评论爬取"""

    async def get_comments(self, uid: str, typ: str='answer') -> dict:
        """
        获取评论
        :param uid:
        :param typ:
        :return:
        """
        # uid = '720626601'
        url = f'https://www.zhihu.com/api/v4/{typ}s/{uid}/root_comments'
        params = {
            'order': 'normal',
            'limit': '20',
            'offset': '0',
            'status': 'open',
        }

        r = await self.client.get(url, params=params, headers = self.client.headers)
        self.logger.debug(await r.text())
        result = await r.json()
        self.logger.debug(result)
        return result

    async def get_comments_by_url(self, url) -> dict:
        """
        获取评论
        :param uid:
        :param typ:
        :return:
        """
        r = await self.client.get(url, headers = self.client.headers)
        self.logger.debug(await r.text())
        result = await r.json()
        self.logger.debug(result)
        return result

    async def endorse_comment(self, uid: str, delete: bool = False) -> dict:
        """
        赞同评论
        :param uid:
        :param delete:
        :return:
        """
        url = f'https://www.zhihu.com/api/v4/comments/{uid}/actions/like'
        if delete:
            r = await self.client.delete(url, headers = self.client.headers)
        else:
            r = await self.client.post(url, headers = self.client.headers)
        result = await r.json()
        self.logger.debug(result)
        return result


if __name__ == '__main__':
    import asyncio
    from setting import USER, PASSWORD
    from zhihu_client import ZhihuClient

    async def test():
        client = ZhihuClient(user=USER, password=PASSWORD)
        await client.login(load_cookies=True)
        spider = CommentSpider(client)
        await spider.get_comments('123')
        await client.close()

    asyncio.run(test())