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


def print_vote_thank(output: dict, typ: str):
    """
    打印赞同感谢  up', 'down', 'neutral'
    :param output:
    :return:
    """
    if output.get('error'):
        print_colour(output.get('error'), 'red')
    elif typ == 'thank':
        print_colour('点击感谢成功!重复点击将取消感谢')
    elif typ == 'up':
        print_colour('赞同成功!')
    elif typ == 'down':
        print_colour('反对成功!')
    else:
        print_colour('保持中立!')
