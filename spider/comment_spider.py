from utils import SpiderBaseclass


class CommentSpider(SpiderBaseclass):

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