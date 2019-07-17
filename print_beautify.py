import html2text
from utils import print_colour


def print_recommend_article(output: list):
    """
    打印推荐文章简述
    :param output:
    :return:
    """
    for d in output:
        print_colour('=' * 60, 'white')
        print_colour(f'id:{d["id"]}')
        print_colour(d['question']['title'], 'purple', end='')
        print_colour(f"({d['author']['name']})", 'purple')
        print_colour(d['excerpt'])
        print_colour(f"*赞同数{d['voteup_count']} 感谢数{d.get('thanks_count', 0)} "
                     f"评论数{d['comment_count']} 浏览数{d['visited_count']}*", 'purple')


def print_article_content(output: dict):
    """
    打印文章内容
    :param output:
    :return:
    """
    content = output['content']
    title = output['question']['title']
    print_colour(f'id:{output["id"]}')
    print_colour(f'title:{title}', 'purple')
    content = html2text.html2text(content)
    print_colour(content)


def print_comments(output: list):
    """
    打印评论
    :param output:
    :return:
    """
    pass
