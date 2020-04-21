"""
处理从知乎获取到的数据,去除不需要的数据
"""
import json
from pyquery import PyQuery as pq
from spider.article_spider import ArticleSpider
from spider.comment_spider import CommentSpider
from spider.user_spider import UserSpider


class DataExtractor(ArticleSpider, CommentSpider, UserSpider):
    """数据提取"""

    async def get_self_info(self) -> dict:
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
                'excerpt': target.get('excerpt_new') or target.get('excerpt'),
                'content': target['content'],
                'voteup_count': target.get('voteup_count'),  # 赞同数
                'visited_count': target.get('visited_count'),
                'thanks_count': target.get('thanks_count', 0),
                'comment_count': target['comment_count'],
                'id': str(target['id']),
                'type': target['type'],
                'created_time': d['created_time'],
                'updated_time': d['updated_time'],
            }
            # 如果type是zvideo，那么voteup_count对应的属性名是vote_count,这里把属性名修改过来
            if target['type'] == 'zvideo':
                article_info['voteup_count'] = target.get('vote_count')
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
                    'id': str(question['id']),
                    'type': 'normal',
                }
            else:
                question = {
                    'title': target['title'],
                    'url': target.get('url'),
                    'type': 'market',
                    'id': '',
                    'author': target['author']
                }
            article_info['question'] = question
            output.append(article_info)
        self.logger.debug(output)
        return output

    def extract_comments(self, result: dict) -> tuple:
        """
        提取评论
        :param result:
        :return:
        """
        output = []
        for d in result['data']:
            author = d['author']['member']
            for clild in d['child_comments']:
                clild['author'] = clild['author']['member']
                if clild['reply_to_author'].get('member'):
                    clild['reply_to_author'] = clild['reply_to_author']['member']
            reply_to_author = d.get('reply_to_author', {}).get('member', {})
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
                'id': str(d['id']),
                'vote_count': d['vote_count'],
                'voting': d['voting'],
                'type': d['type'],
                'featured': d.get('featured'),  # 是否是热评
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
        return output, paging

    async def get_comments(self, uid: str, typ: str ='answer') -> tuple:
        """
        获取评论
        :param typ:
        :param uid:
        :return:
        """
        result = await super().get_comments(uid, typ)
        output, paging = self.extract_comments(result)
        return output, paging

    async def get_comments_by_url(self, url: str) -> tuple:
        """
        获取评论
        :return:
        """
        result = await super().get_comments_by_url(url)
        output, paging = self.extract_comments(result)
        return output, paging

    async def get_question_details(self, question_id: str, uid: str) -> dict:
        """
        获取评论
        :return:
        """
        result = await super().get_question_article_first(question_id, uid)
        doc = pq(result)
        data = doc('#js-initialData').text()
        result = json.loads(data)
        questions = list(result['initialState']['entities']['questions'].values())[0]
        # answers = list(result['initialState']['entities']['answers'].values())[0]
        output = {
                'id': questions['id'],
                'type': questions['type'],
                'title': questions['title'],
                'creTime': questions.get('creTime') or questions.get('created'),
                'excerpt': questions['excerpt'],
                'detail': questions['detail'],
                'author': questions['author'],
                'answerCount': questions['answerCount'],
                'visitCount': questions['visitCount'],
                'comment_count': questions['commentCount'],
                'followerCount': questions['followerCount'],
        }
        return output
    # TODO
    # async def get_first_answer_by_qustion(self, question_id: str, uid: str) -> dict:
    #     """
    #     获取第一个回答,这个回答很可能在后续的查询中查询不到
    #     :return:
    #     """
    #     result = await super().get_question_article_first(question_id, uid)
    #     doc = pq(result)
    #     data = doc('#js-initialData').text()
    #     result = json.loads(data)
    #     # questions = list(result['initialState']['entities']['questions'].values())[0]
    #     answers = list(result['initialState']['entities']['answers'].values())[0]
    #     output = {
    #             'author': {
    #                 ''
    #             }
    #     }
    #     return output

    def extract_article_by_question(self, result):
        """
        提取文章信息
        :param result:
        :return:
        """
        output = []
        for d in result['data']:  # 提取用到的数据
            target = d
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
                'excerpt': target.get('excerpt_new') or target.get('excerpt'),
                'content': target['content'],
                'voteup_count': target['voteup_count'],  # 赞同数
                'visited_count': target.get('visited_count', 0),
                'thanks_count': target.get('thanks_count', 0),
                'comment_count': target['comment_count'],
                'id': str(target['id']),
                'type': target['type'],
                'created_time': d['created_time'],
                'updated_time': d['updated_time'],
            }
            if question:
                question = {
                    'title': question['title'],
                    'url': question['url'],
                    'id': str(question['id']),
                    'type': 'normal',
                }
            else:
                question = {
                    'title': target['title'],
                    'url': target['url'],
                    'type': 'market',
                    'id': '',
                }
            article_info['question'] = question
            output.append(article_info)
        return output

    async def get_article_by_question(self, question_id, offset: int = 0, limit: int = 3) -> tuple:
        """

        :param question_id:
        :param offset:
        :param limit:
        :return:
        """
        result = await super().get_article_by_question(question_id, offset, limit)
        output = self.extract_article_by_question(result)
        paging = result['paging']
        self.logger.debug(output)
        return output, paging

    async def get_article_by_question_url(self, url):
        """

        :param url:
        :return:
        """
        result = await super().get_article_by_question_url(url)
        output = self.extract_article_by_question(result)
        paging = result['paging']
        self.logger.debug(output)
        return output, paging
