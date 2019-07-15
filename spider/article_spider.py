"""
知乎api
"""
import re
import asyncio
from zhihu_client import ZhihuClient
from utils import SpiderBaseclass


class ArticleSpider(SpiderBaseclass):

    async def get_recommend_article(self) -> dict:
        """
        获取推荐文章
        :return:
        """
        url = 'https://www.zhihu.com'
        for _ in range(2):
            async with self.client.get(url) as r:
                resp = await r.text()
                session_token = re.findall(r'session_token=(.*?)\&', resp)
            if session_token:
                session_token = session_token[0]
                break
        else:
            raise AssertionError('获取session_token失败')
        url = 'https://www.zhihu.com/api/v3/feed/topstory/recommend?'
        data = {
            'session_token': session_token,
            'desktop': 'true',
            'page_number': '1',
            'limit': '6',
            'action': 'down',
            'after_id': '5',
        }
        async with self.client.get(url, params=data) as r:
            result = await r.json()
        return result

    async def endorse_answer(self, uid, typ: str= 'up') -> dict:
        """
        赞同回答
        :param id:
        :param typ: up赞同, down踩, neutral中立
        :return:
        """
        # 724073802
        url = f'https://www.zhihu.com/api/v4/answers/{uid}/voters'
        data = {
            'type': typ
        }
        r = await self.client.post(url, json=data)
        result = await r.json()
        self.logger.debug(result)
        return result

    async def thank_answer(self, uid: str, delete: bool=False) -> dict:
        """
        感谢回答
        :param id:
        :param delete:
        :return:
        """
        url = f'https://www.zhihu.com/api/v4/answers/{uid}/thankers'
        if delete:
            r = await self.client.delete(url)
        else:
            r = await self.client.post(url)
        result = await r.json()
        self.logger.debug(result)
        return result


if __name__ == '__main__':
    from setting import USER, PASSWORD

    async def test():
        client = ZhihuClient(user=USER, password=PASSWORD)
        await client.login(load_cookies=True)
        spider = ArticleSpider(client)
        await spider.get_recommend_article()
        await client.close()

    asyncio.run(test())
