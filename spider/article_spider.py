"""
知乎api
"""
import re
import asyncio
from zhihu_client import ZhihuClient
from utils import SpiderBaseclass


class ArticleSpider(SpiderBaseclass):

    async def get_self_info(self) -> dict:
        """
        获取我的信息
        :param session:
        :return:
        """
        url = 'https://www.zhihu.com/api/v4/me?include=ad_type;available_message_types,' \
              'default_notifications_count,follow_notifications_count,vote_thank_notifications_count,' \
              'messages_count;draft_count;following_question_count;account_status,is_bind_phone,' \
              'is_force_renamed,email,renamed_fullname;ad_type'

        async with self.client.get(url) as resp:
            result = await resp.json()
            self.logger.debug(result)
        return result

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

    async def get_comments(self, uid: str) -> dict:
        """
        获取评论
        :param id:
        :return:
        """
        '414461974'
        url = f'https://www.zhihu.com/api/v4/answers/{uid}/root_comments'
        params = {
            'order': 'normal',
            'limit': '20',
            'status': 'open',
            'offset': '0',
        }
        r = await self.client.get(url, params=params)
        result = await r.json()
        # self.logger.debug(result)
        return result

    async def endorse_comment(self, uid: str, delete: bool = False) -> dict:
        """
        赞同评论
        :param uid:
        :return:
        """
        url = f'https://www.zhihu.com/api/v4/comments/{uid}/actions/like'
        if delete:
            r = await self.client.delete(url)
        else:
            r = await self.client.post(url)
        result = await r.json()
        self.logger.debug(result)
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
        spider = ZhihuSpider(client)
        # await spider.get_recommend_article()
        # await spider.endorse_answer('')
        # await spider.thank_answer('')
        await spider.get_comments('324013933')
        await client.close()

    asyncio.run(test())
