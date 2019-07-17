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
        url = f'https://www.zhihu.com/api/v4/{typ}s/{uid}/root_comments'
        params = {
            'order': 'normal',
            'limit': '20',
            'offset': '0',
            'status': 'open',
        }

        r = await self.client.get(url, params=params, proxy='http://10.10.9.56:8888', verify_ssl=False)
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
            r = await self.client.delete(url)
        else:
            r = await self.client.post(url)
        result = await r.json()
        self.logger.debug(result)
        return result