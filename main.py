import os
import asyncio
import html2text
from zhihu_client import ZhihuClient
from data_extractor import DataExtractor

from print_beautify import print_recommend_article

from utils import print_colour
from utils import get_com_func

from setting import USER
from setting import PASSWORD


def welcome():
    os.system("clear")
    logo = '''
                                                                                             ;$$;
                                                                                        #############
                                                                                   #############;#####o
                                                          ##                 o#########################
                                                          #####         $###############################
                                                          ##  ###$ ######!    ##########################
                               ##                        ###    $###          ################### ######
                               ###                      ###                   ##o#######################
                              ######                  ;###                    #### #####################
                              ##  ###             ######                       ######&&################
                              ##    ###      ######                            ## ############ #######
                             o##      ########                                  ## ##################
                             ##o                ###                             #### #######o#######
                             ##               ######                             ###########&#####
                             ##                ####                               #############!
                            ###                                                     #########
                   #####&   ##                                                      o####
                 ######     ##                                                   ####*
                      ##   !##                                               #####
                       ##  ##*                                            ####; ##
                        #####                                          #####o   #####
                         ####                                        ### ###   $###o
                          ###                                            ## ####! $###
                          ##                                            #####
                          ##                                            ##
                         ;##                                           ###                           ;
                         ##$                                           ##
                    #######                                            ##
                #####   &##                                            ##
              ###       ###                                           ###
             ###      ###                                             ##
             ##     ;##                                               ##
             ##    ###                                                ##
              ### ###                                                 ##
                ####                                                  ##
                 ###                                                  ##
                 ##;                                                  ##
                 ##$                                                 ##&
                  ##                                                 ##
                  ##;                                               ##
                   ##                                              ##;
                    ###                                          ###         ##$
                      ###                                      ###           ##
       ######################                              #####&&&&&&&&&&&&###
     ###        $#####$     ############&$o$&################################
     #                               $&########&o
    '''
    print_colour(logo, 'blue')


def main_help():
    output = "\n" \
           "**********************************************************\n" \
           "**\n" \
           "**  remd:    查看推荐内容\n" \
           "**  aten:    查看动态内容\n" \
           "**  q:       退出系统\n" \
           "**\n" \
           "**********************************************************\n"
    return output


def recommend_help():
    output = "\n" \
           "**********************************************************\n" \
           "**  id(文章id)\n" \
           "**  f:               刷新内容\n" \
           "**  help:            显示更多功能\n" \
           "**  back:            返回上层\n" \
           "**  q:               退出系统\n" \
           "**\n" \
           "**********************************************************\n"
    return output


def recommend_help_2():
    output = "\n" \
            "**********************************************************\n" \
            "**  id(文章id)\n" \
            "**  f:               刷新内容\n" \
            "**  r:               再次显示(重新显示回答)\n" \
            "**  back:            返回上层\n" \
            "**  q:               退出系统\n" \
            "**  up-id:           赞同\n" \
            "**  down-id:         反对\n" \
            "**  neutral-id:      中立,可以取消对回答的赞同或反对\n" \
            "**  thank-id:        感谢\n" \
            "**  unthank-id:      取消感谢\n"\
            "**  comment-id:      查看评论\n"\
            "**  check-id:        查看回答具体内容\n" \
            "**\n" \
            "**********************************************************\n"
    return output


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


async def run(client):
    global main_help
    global recommend_help
    global recommend_help_2
    spider = DataExtractor(client)
    output = await spider.get_self_info()
    print_colour(f'hello {output["name"]} 欢迎使用terminal-zhihu!', 'blue')
    main_help = main_help()
    recommend_help = recommend_help()
    recommend_help_2 = recommend_help_2()
    flag = True
    while flag:
        cmd = input(main_help)
        if cmd in ('q', 'quit', 'exit'):
            break
        elif cmd == 'remd':
            is_print = True
            is_input = True
            while True:
                if is_print:
                    recommend_articles = await spider.get_recommend_article()
                    ids = [d.get('id') for d in recommend_articles]
                    print_recommend_article(recommend_articles)
                    is_print = False
                if is_input:
                    remd_cmd = input(recommend_help)
                remd_cmd = remd_cmd.split('-')
                if not remd_cmd:
                    print_colour('输入有误!', 'red')
                    is_input = True
                    continue
                if remd_cmd[0] == 'f':
                    is_print = True
                    continue
                elif remd_cmd[0] == 'back':
                    break
                elif remd_cmd[0] in ('q', 'quit', 'exit'):
                    flag = False
                    break
                elif remd_cmd[0] == 'help':
                    remd_cmd = input(recommend_help_2)
                    is_input = False
                    continue
                elif remd_cmd[0] in ('up', 'down', 'neutral', 'thank', 'unthank', 'comment', 'check'):
                    if len(remd_cmd) != 2:
                        print_colour('输入有误!', 'red')
                        is_input = True
                        continue
                    if remd_cmd[1] not in ids:
                        print_colour('输入id有误!', 'red')
                        is_input = True
                        continue
                    if remd_cmd[0] == 'check':
                        content = [d['content'] for d in recommend_articles if d['id'] == remd_cmd[1]][0]
                        content = html2text.html2text(content)
                        print_colour(content)
                        continue
                    else:
                        func = get_com_func(remd_cmd[0])
                        result = await getattr(spider, func)(remd_cmd[1])
                        print_colour(result)
                        continue
                is_input = True

        elif cmd == 'aten':
            pass


async def main():
    try:
        check_setting()
        client = await login(USER, PASSWORD)
        welcome()
        await run(client)
    except Exception as e:
        print_colour(e, 'red')
    finally:
        await asyncio.sleep(0)
        await client.close()


if __name__ == '__main__':
    asyncio.run(main())