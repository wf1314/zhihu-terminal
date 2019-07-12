import re
import asyncio
from zhihu_client import ZhihuClient
from utils import print_colour


class ZhihuSpider(object):

    def __init__(self, client: ZhihuClient):
        self.client = client
        self.logger = self.client.logger

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
            print_colour(result)

        output = {
            'name': result['name'],
            'haealine': result['headline'],
            'head': result['avatar_url'],
            'gender': result['gender'],
            'vip_info': result['vip_info'],
            'url': result['url'],
        }
        self.logger.debug(output)
        return output

    async def get_recommend_article(self):
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

        output = []
        for d in result['data']:  # 提取用到的数据
            target = d['target']
            author = target['author']
            question = target.get('question')
            article_info = {
                'author': {  # 作者信息
                    'name': author['name'],
                    'headline': author.get('headline'),
                    'head': author['avatar_url'],
                    'gender': author.get('gender'),
                    'url': author.get('url'),
                },
                'excerpt': target['excerpt_new'],
                'content': target['content'],
                'voteup_count': target['voteup_count'],  # 赞同数
                'visited_count': target['visited_count'],
                'thanks_count': target['thanks_count'],
                'comment_count': target['comment_count'],
                'id': target['id'],
                'created_time': d['created_time'],
                'updated_time': d['updated_time'],
            }
            if question:
                question = {
                    'author': {
                        'name': question['author']['name'],
                        'headline': question['author'].get('headline'),
                        'head': question['author'].get('head'),
                        'gender': question['author'].get('gender'),
                        'url': question['author'].get('url'),
                    },
                    'title': question['title'],
                    'url': question['url'],
                    'type': 'normal',
                }
                article_info.update(question)
            else:
                question = {
                    'title': target['title'],
                    'url': target['url'],
                    'type': 'market',
                    'author': article_info['author']
                }
                article_info.update(question)
            output.append(article_info)
        self.logger.debug(output)
        return output

    async def get_comments(self, uid: str):
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
        output = []
        for d in result['data']:
            author = d['author']['member']
            reply_to_author = d.get('reply_to_author', {}).get('member')
            comment_info = {
                'author': {
                    'name': author.get('name'),
                    'headline': author.get('headline'),
                    'head': author.get('head'),
                    'gender': author.get('gender'),
                    'url': author.get('url'),
                },
                'content': d['content'],
                'created_time': d['created_time'],
                'child_comment_count': d['child_comment_count'],
                'id': d['id'],
                'vote_count': d['vote_count'],
                'voting': d['voting'],
                'type': d['type'],
                'reply_to_author': {
                    'name': reply_to_author.get('name'),
                    'headline': reply_to_author.get('headline'),
                    'head': reply_to_author.get('head'),
                    'gender': reply_to_author.get('gender'),
                    'url': reply_to_author.get('url'),
                },
                'child_comments': d['child_comments']
            }
            output.append(comment_info)
        self.logger.debug(output)
        paging = result['paging']
        return output

    async def endorse_comment(self, uid: str, delete: bool = False):
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
        self.logger.debug(await r.text())

    async def endorse_answer(self, uid, typ: str= 'up'):
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
        result = await r.text()
        self.logger.debug(result)

    async def thank_answer(self, uid: str, delete: bool=False):
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
        self.logger.debug(await r.text())


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

    ioloop = asyncio.get_event_loop()
    ioloop.run_until_complete(test())
