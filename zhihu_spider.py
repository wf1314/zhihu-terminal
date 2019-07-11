import re
import asyncio
from zhihu_client import ZhihuClient
from utils import print_colour


class ZhihuSpider(object):

    def __init__(self, client: ZhihuClient):
        self.client = client
        self.logger = self.client.logger

    async def get_me_info(self) -> dict:
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
        print_colour(output)
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
        for d in result['data']:
            target = d['target']
            author = target['author']
            question = target.get('question')
            article_info = {
                'author': {
                    'name': author['name'],
                    'headline': author.get('headline'),
                    'head': author['avatar_url'],
                    'gender': author.get('gender'),
                    'url': author.get('url'),
                },
                'excerpt': target['excerpt_new'],
                'content': target['content'],
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
        print_colour(output)
        return output


if __name__ == '__main__':
    from setting import USER, PASSWORD
    async def test():
        client = ZhihuClient(user=USER, password=PASSWORD)
        await client.login(load_cookies=True)
        spider = ZhihuSpider(client)
        await spider.get_recommend_article()

    ioloop = asyncio.get_event_loop()
    ioloop.run_until_complete(test())