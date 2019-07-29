import os
import sys
import asyncio
from zhihu_client import ZhihuClient
from data_extractor import DataExtractor

from print_beautify import print_recommend_article
from print_beautify import print_article_content
from print_beautify import print_comments
from print_beautify import print_question
from print_beautify import print_vote_thank
from print_beautify import print_vote_comments
from print_beautify import print_logo
from print_beautify import print_save

from utils import print_colour
from utils import get_com_func

from setting import USER
from setting import PASSWORD
from setting import SAVE_DIR


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
           "**  read:article_id          查看回答具体内容(进入下一级菜单)\n" \
           "**  question:question_id     查看问题下的其他回答(进入下一级菜单)\n" \
           "**  back:                    返回上层\n" \
           "**  q:                       退出系统\n" \
           "**********************************************************\n"
    return output


def help_article():
    output = "\n" \
            "**********************************************************\n" \
            "**  back                    返回上层\n" \
            "**  q                       退出系统\n" \
            "**  save                    保存到本地\n" \
            "**  enshrine                收藏回答\n" \
            "**  question                查看问题下的其他回答\n" \
            "**  up                      赞同\n" \
            "**  down                    反对\n" \
            "**  neutral                 中立,可以取消对回答的赞同或反对\n" \
            "**  thank                   感谢\n" \
            "**  unthank                 取消感谢\n"\
            "**  comment                 评论相关(查看评论, 回复评论等将进入下一级菜单)\n"\
            "**********************************************************\n"
    return output


def help_comments():
    output = "\n" \
            "**********************************************************\n" \
            "**  back                    返回上层\n" \
            "**  q                       退出系统\n" \
            "**  n                       显示下一页\n" \
            "**  p                       显示上一页\n" \
            "**  com:comment_id          回复评论,点赞等功能(进入下级菜单)\n" \
            "**********************************************************\n"
    return output


def help_comments2():
    output = "\n" \
            "**********************************************************\n" \
            "**  back                    返回上层\n" \
            "**  q                       退出系统\n" \
            "**  up                      点赞\n" \
            "**  neutral                 中立,可以取消对点赞\n" \
            "**  reply:content           回复评论\n" \
            "**********************************************************\n"
    return output


def help_question():
    output = "\n" \
            "**********************************************************\n" \
            "**  back                    返回上层\n" \
            "**  q                       退出系统\n" \
            "**  question                查看问题详情\n" \
            "**  read:article_id         查看回答具体内容(进入下一级菜单)\n" \
            "**  n                       显示下一页\n" \
            "**  p                       显示上一页\n" \
            "**  r                       再次显示(重新显示回答)\n" \
            "**********************************************************\n"
    return output


def exit(cmd: str):
    if cmd in('q', 'quit', 'exit'):
        sys.exit()


def clear():
    os.system("clear")


async def deal_comments_by_id(spider, uid):
    """
    对应id评论相关
    :param spider:
    :return:
    """
    while True:
        print_colour('', 'yellow')
        com2_cmd = input(help_comments2()).lower()
        com2_cmd = com2_cmd.split(':')
        if not com2_cmd[0]:
            print_colour('输入有误!', 'red')
            continue
        exit(com2_cmd[0])
        if com2_cmd[0] == 'back':
            break
        elif com2_cmd[0] == 'up':
            result = await spider.endorse_comment(uid, False)
            print_vote_comments(result, 'up')
        elif com2_cmd[0] == 'neutral':
            result = await spider.endorse_comment(uid, True)
            print_colour(result)
            print_vote_comments(result, 'neutral')
        elif com2_cmd[0] == 'reply' and len(com2_cmd) == 2:
            # todo 回复评论
            data = {
                'content': com2_cmd[1],
                'replyToId': uid,
            }
            print_colour('功能还在开发中...', 'red')
            continue
        else:
            print_colour('输入有误!', 'red')
            continue
    pass


async def deal_comments(spider, result, paging):
    """
    处理评论命令
    :param spider:
    :return:
    """
    # all_coments = []
    while True:
        comment_ids = []
        for d in result:
            comment_ids.append(d['id'])
            for clild in d.get('child_comments'):
                comment_ids.append(clild['id'])
        comment_ids = list(set(comment_ids))
        print_colour('', 'yellow')
        comm_cmd = input(help_comments()).lower()
        comm_cmd = comm_cmd.split(':')
        if not comm_cmd:
            print_colour('输入有误!', 'red')
            continue
        exit(comm_cmd[0])
        if comm_cmd[0] == 'back':
            break
        elif comm_cmd[0] == 'n':
            if paging.get('is_end'):
                print_colour('已是最后一页!', 'red')
                continue
            url = paging['next'].replace('https://www.zhihu.com/', 'https://www.zhihu.com/api/v4/')
            result, paging = await spider.get_comments_by_url(url)
            print_comments(result)
            continue
        elif comm_cmd[0] == 'p':
            if paging.get('is_start'):
                print_colour('已是第一页!', 'red')
                continue
            url = paging['previous'].replace('https://www.zhihu.com/', 'https://www.zhihu.com/api/v4/')
            result, paging = await spider.get_comments_by_url(url)
            print_comments(result)
            continue
        elif comm_cmd[0] == 'com':
            if len(comm_cmd) != 2:
                print_colour('输入有误!', 'red')
                continue
            if comm_cmd[1] not in comment_ids:
                print_colour('输入id有误!', 'red')
                continue
            await deal_comments_by_id(spider, comm_cmd[1])
            continue
        else:
            print_colour('输入有误!', 'red')
            continue


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
        arl_cmd = input(help_article()).lower()
        if not arl_cmd:
            print_colour('输入有误!', 'red')
            continue
        exit(arl_cmd)
        if arl_cmd == 'back':
            break

        elif arl_cmd in ('up', 'down', 'neutral', 'thank', 'unthank'):

            uid = article.get('id')
            func = get_com_func(arl_cmd)
            result = await getattr(spider, func)(uid)
            print_vote_thank(result, arl_cmd)
            continue
        elif arl_cmd == 'comment':
            typ = article['type']
            uid = article.get('id')
            result, paging = await spider.get_comments(uid, typ)
            print_comments(result)
            await deal_comments(spider, result, paging)
            continue
        elif arl_cmd == 'save':
            print_save(article)
            continue
        elif arl_cmd == 'enshrine':
            # todo 收藏回答
            print_colour('功能还在开发中...', 'red')
            continue
        elif arl_cmd == 'question':
            await deal_question(spider, article.get('question').get('id'), article.get('id'))
            continue
        else:
            print_colour('输入有误!', 'red')
            continue


async def deal_question(spider, question_id, uid):
    """
    处理问题命令
    :param spider:
    :param uid:
    :param id_map:
    :return:
    """
    is_print = True
    while True:
        if is_print:
            question_articles, paging = await spider.get_article_by_question(question_id)
            ids = [d.get('id') for d in question_articles]
            print_recommend_article(question_articles)
            is_print = False
        print_colour('', 'yellow')
        ques_cmd = input(help_question()).lower()
        ques_cmd = ques_cmd.split(':')
        if not ques_cmd:
            print_colour('输入有误!', 'red')
            continue
        exit(ques_cmd[0])
        if ques_cmd[0] == 'read':
            if len(ques_cmd) != 2:
                print_colour('输入有误!', 'red')
                continue
            if ques_cmd[1] not in ids:
                print_colour('输入id有误!', 'red')
                continue
            output = [d for d in question_articles if d['id'] == ques_cmd[1]][0]
            print_article_content(output)
            await deal_article(spider, output)
            continue
        elif ques_cmd[0] == 'question':
            question_detail = await spider.get_question_details(question_id, uid)
            print_question(question_detail)
        elif ques_cmd[0] == 'n':
            if paging.get('is_end'):
                print_colour('已是最后一页!', 'red')
                continue
            url = paging['next']
            question_articles, paging = await spider.get_article_by_question_url(url)
            print_recommend_article(question_articles)
            continue
        elif ques_cmd[0] == 'p':
            if paging.get('is_start'):
                print_colour('已是第一页!', 'red')
                continue
            url = paging['previous']
            question_articles, paging = await spider.get_article_by_question_url(url)
            print_recommend_article(question_articles)
        elif ques_cmd[0] == 'r':
            print_recommend_article(question_articles)
            continue
        elif ques_cmd[0] == 'back':
            break
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
            question_ids = [d.get('question').get('id') for d in recommend_articles]
            if len(remd_cmd) != 2:
                print_colour('输入有误!', 'red')
                continue
            if remd_cmd[1] not in question_ids:
                print_colour('输入id有误!', 'red')
                continue
            assert len(ids) == len(question_ids)
            id_map = dict(zip(question_ids, ids))
            uid = id_map[remd_cmd[1]]
            await deal_question(spider, remd_cmd[1], uid)
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
        if not cmd:
            print_colour('输入有误!', 'red')
            continue
        exit(cmd)
        if cmd == 'remd':
            await deal_remd(spider)
        elif cmd == 'aten':
            # todo 获取关注动态
            print_colour('功能还在开发中...', 'red')
            continue
        else:
            print_colour('输入有误!', 'red')
            continue


def check_setting():
    save_dir = SAVE_DIR or '/tmp/zhihu_save'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)


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


async def main():
    try:
        check_setting()
        client = await login(USER, PASSWORD)
        print_logo()
        await run(client)
    # except Exception as e:
    #     print_colour(e, 'red')
    finally:
        print_colour('欢迎再次使用')
        await asyncio.sleep(0)
        await client.close()


if __name__ == '__main__':
    # asyncio.run(main())
    asyncio.get_event_loop().run_until_complete(main())
