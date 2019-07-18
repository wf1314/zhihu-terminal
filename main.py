import os
import sys
import asyncio
from zhihu_client import ZhihuClient
from data_extractor import DataExtractor

from print_beautify import print_recommend_article
from print_beautify import print_article_content
from print_beautify import print_comments
from print_beautify import print_vote_thank
from print_beautify import print_log

from utils import print_colour
from utils import get_com_func

from setting import USER
from setting import PASSWORD


def help_main():
    output = "\n" \
           "**********************************************************\n" \
           "**  remd:                    查看推荐内容\n" \
           "**  aten:                    查看动态内容\n" \
           "**  q:                       退出系统\n" \
           "**********************************************************\n"
    return output


def help_recommend():
    output = "\n" \
           "**********************************************************\n" \
           "**  f:                       刷新推荐内容\n" \
           "**  r:                       再次显示(重新显示回答)\n" \
           "**  read:article_id          查看回答具体内容\n" \
           "**  question:question_id     查看回答具体内容\n" \
           "**  back:                    返回上层\n" \
           "**  q:                       退出系统\n" \
           "**********************************************************\n"
    return output


def help_article():
    output = "\n" \
            "**********************************************************\n" \
            "**  question                查看回答具体内容\n" \
            "**  back                    返回上层\n" \
            "**  q                       退出系统\n" \
            "**  up                      赞同\n" \
            "**  down                    反对\n" \
            "**  neutral                 中立,可以取消对回答的赞同或反对\n" \
            "**  thank                   感谢\n" \
            "**  unthank                 取消感谢\n"\
            "**  comment                 评论相关(查看评论, 回复评论等)\n"\
            "**********************************************************\n"
    return output


def help_comments():
    pass


def check_setting():
    pass


async def login(user, password):
    """
    登录
    :param user:
    :param password:
    :return:
    """
    client = ZhihuClient(user, password)
    load_cookies = False
    if os.path.exists(client.cookie_file):
        # 如果cookie缓存存在优先读取缓存
        load_cookies = True
    await client.login(load_cookies=load_cookies)
    return client


def exit(cmd: str):
    if cmd in('q', 'quit', 'exit'):
        sys.exit()


async def deal_comments(spider):
    """
    处理评论命令
    :param spider:
    :return:
    """
    while True:
        print_colour('', 'yellow')
        remd_cmd = input(help_comments()).lower()
        remd_cmd = remd_cmd.split(':')
        # TODO 处理评论命令
        import pdb;pdb.set_trace()


async def deal_article(spider, article):
    """
    处理文章内容命令
    :param spider:
    :param recommend_articles:
    :param ids:
    :return:
    """
    while True:
        print_colour('', 'yellow')
        remd_cmd = input(help_article()).lower()
        if not remd_cmd:
            print_colour('输入有误!', 'red')
            continue
        exit(remd_cmd)
        if remd_cmd == 'back':
            break

        elif remd_cmd in ('up', 'down', 'neutral', 'thank', 'unthank'):

            uid = article.get('id')
            func = get_com_func(remd_cmd)
            result = await getattr(spider, func)(uid)
            print_vote_thank(result, remd_cmd)
            continue
        elif remd_cmd == 'comment':
            typ = article['type']
            uid = article.get('id')
            result = await spider.get_comments(uid, typ)
            print_comments(result)  # TODO 输出评论信息
            import pdb;
            pdb.set_trace()
            await deal_comments(spider)
        elif remd_cmd == 'question':
            # todo 查看问题下的其他回答
            continue
        else:
            print_colour('输入有误!', 'red')
            continue


async def deal_remd(spider):
    """
    处理推荐文章命令
    :param spider:
    :return:
    """
    is_print = True
    while True:
        if is_print:
            recommend_articles = await spider.get_recommend_article()
            ids = [d.get('id') for d in recommend_articles]
            print_recommend_article(recommend_articles)
            is_print = False
        print_colour('', 'yellow')
        remd_cmd = input(help_recommend()).lower()
        remd_cmd = remd_cmd.split(':')
        if not remd_cmd:
            print_colour('输入有误!', 'red')
            continue
        exit(remd_cmd[0])
        if remd_cmd[0] == 'f':
            is_print = True
            continue
        elif remd_cmd[0] == 'r':
            print_recommend_article(recommend_articles)
            continue
        elif remd_cmd[0] == 'read':
            if len(remd_cmd) != 2:
                print_colour('输入有误!', 'red')
                continue
            if remd_cmd[1] not in ids:
                print_colour('输入id有误!', 'red')
                continue
            output = [d for d in recommend_articles if d['id'] == remd_cmd[1]][0]
            print_article_content(output)
            await deal_article(spider, output)
            continue
        elif remd_cmd[0] == 'question':
            # todo 查看问题下的其他回答
            continue
        elif remd_cmd[0] == 'back':
            break
        else:
            print_colour('输入有误!', 'red')
            continue


async def run(client):
    spider = DataExtractor(client)
    output = await spider.get_self_info()
    print_colour(f'hello {output["name"]} 欢迎使用terminal-zhihu!', 'ultramarine')
    flag = True
    while flag:
        print_colour('', 'yellow')
        cmd = input(help_main()).lower()
        exit(cmd)
        if cmd == 'remd':
            await deal_remd(spider)
        elif cmd == 'aten':
            pass


async def main():
    try:
        check_setting()
        client = await login(USER, PASSWORD)
        print_log()
        await run(client)
    # except Exception as e:
    #     print_colour(e, 'red')
    finally:
        print_colour('欢迎再次使用')
        await asyncio.sleep(0)
        await client.close()


if __name__ == '__main__':
    asyncio.run(main())
