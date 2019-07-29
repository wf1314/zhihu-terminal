"""
知乎api
"""
import re
import asyncio
from zhihu_client import ZhihuClient
from utils import SpiderBaseclass


class ArticleSpider(SpiderBaseclass):
    """文章相关"""

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
        self.logger.debug(result)
        return result

    async def endorse_answer(self, uid: str, typ: str = 'up') -> dict:
        """
        赞同回答
        :param uid:
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

    async def thank_answer(self, uid: str, delete: bool = False) -> dict:
        """
        感谢回答
        :param uid:
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

    async def get_question_article_first(self, question_id: str, uid: str):
        """

        :param uid:
        :param question_id:
        :return:
        """
        url = f'https://www.zhihu.com/question/{question_id}/answer/{uid}'
        r = await self.client.get(url)
        resp = await r.text()
        self.logger.debug(resp)
        return resp

    async def get_article_by_question(self, question_id, offset: int = 0, limit: int = 3):
        """

        :param question_id:
        :param offset:
        :param limit:
        :return:
        """
        url = f'https://www.zhihu.com/api/v4/questions/{question_id}/answers'
        params = {
            'include': 'data[*].is_normal,admin_closed_comment,reward_info,'
                       'is_collapsed,annotation_action,annotation_detail,collapse_reason,'
                       'is_sticky,collapsed_by,suggest_edit,comment_count,can_comment,'
                       'content,editable_content,voteup_count,reshipment_settings,comment_permission,'
                       'created_time,updated_time,review_info,relevant_info,question,excerpt,'
                       'relationship.is_authorized,is_author,voting,is_thanked,is_nothelp,is_labeled,'
                       'is_recognized,paid_info,paid_info_content;data[*].mark_infos[*].url;data[*].'
                       'author.follower_count,badge[*].topics',
            'offset': offset,
            'limit': limit,
            'sort_by': 'default',
            'platform': 'desktop',
        }
        r = await self.client.get(url, params=params, proxy='http://10.10.9.218:8888', ssl=False)
        result = await r.json()
        self.logger.debug(result)
        return result

    async def get_article_by_question_url(self, url):
        """

        :param question_id:
        :param offset:
        :param limit:
        :return:
        """
        r = await self.client.get(url, proxy='http://10.10.9.218:8888', ssl=False)
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
