"""
处理从知乎获取到的数据,去除不需要的数据
"""
from spider.article_spider import ArticleSpider
from spider.comment_spider import CommentSpider
from spider.user_spider import UserSpider
from utils import print_colour


class DataExtractor(ArticleSpider, CommentSpider, UserSpider):

    async def get_self_info(self):
        """
        获取自己的信息
        :return:
        """
        result = await super().get_self_info()
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

    async def get_recommend_article(self) -> list:
        """
        获取推荐文章
        :return:
        """
        result = await super().get_recommend_article()
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
                'thanks_count': target.get('thanks_count', 0),
                'comment_count': target['comment_count'],
                'id': str(target['id']),
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
        :param uid:
        :return:
        """
        result = await super().get_comments(uid)
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
