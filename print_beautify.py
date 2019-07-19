import os
import html2text
from utils import print_colour


def print_log():
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
    print_colour(logo, 'ultramarine')


def print_recommend_article(output: list):
    """
    打印推荐文章简述
    :param output:
    :return:
    """
    for d in output:
        print_colour('=' * 60, 'white')
        print_colour(f'article_id:{d["id"]}', 'purple')
        print_colour(f'question_id:{d["question"]["id"]}', 'purple')
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
    question_id = output['question']['id']
    content = html2text.html2text(content)
    print_colour(content)
    print_colour('-----------------------------------------------------', 'purple')
    print_colour(f'|article_id:{output["id"]}', 'purple')
    print_colour(f'|question_id:{question_id}', 'purple')
    print_colour(f'|title:{title}', 'purple')
    print_colour('-----------------------------------------------------', 'purple')


def print_comments(output: list):
    """
    打印评论
    :param output:
    :return:
    """
    for d in output:
        author = d.get('author').get('name')
        reply_to_author = d.get('reply_to_author').get('name')
        content = d.get('content')
        vote_count = d.get('vote_count')
        comment_id = d.get('id')
        child_comments = d.get('child_comments')
        print_colour(f'comment_id:{comment_id}', 'purple')
        if d.get('featured'):
            print_colour('热评🔥', end='')
        if reply_to_author:
            print_colour(f'{author}->{reply_to_author}', end='')
        else:
            print_colour(f'{author}', end='')
        print_colour(f'(赞:{vote_count}):{content}')
        if child_comments:
            for clild in child_comments:
                author = clild.get('author').get('name')
                reply_to_author = clild.get('reply_to_author').get('name')
                content = clild.get('content')
                vote_count = clild.get('vote_count')
                comment_id = clild.get('id')
                print_colour(f'         comment_id:{comment_id}', 'purple')
                if d.get('featured'):
                    print_colour('         热评🔥', end='')
                if reply_to_author:
                    print_colour(f'         {author}->{reply_to_author}', end='')
                else:
                    print_colour(f'         {author}', end='')
                print_colour(f'         (赞:{vote_count}):{content}')
                print_colour('         *********************************************************', 'blue')
        print_colour('==========================================================', 'blue')


def print_vote_thank(output: dict, typ: str):
    """
    打印赞同感谢  up', 'down', 'neutral'
    :param output:
    :return:
    """
    if output.get('error'):
        print_colour(output.get('error'), 'red')
    elif typ == 'thank':
        print_colour(f'感谢成功!感谢总数{output["thanks_count"]}')
    elif typ == 'unthank':
        print_colour(f'取消感谢!感谢总数{output["thanks_count"]}')
    elif typ == 'up':
        print_colour(f'赞同成功!赞同总数{output["voteup_count"]}')
    elif typ == 'down':
        print_colour(f'反对成功!赞同总数{output["voteup_count"]}')
    else:
        print_colour(f'保持中立!赞同总数{output["voteup_count"]}')


def print_vote_comments(output: dict, typ: str):
    """
    打印赞同感谢  up', 'down', 'neutral'
    :param output:
    :return:
    """
    if output.get('error'):
        print_colour(output.get('error'), 'red')
    elif typ == 'up':
        print_colour(f'点赞评论成功!被赞总数{output["vote_count"]}')
    elif typ == 'neutral':
        print_colour(f'保持中立!被赞总数{output["vote_count"]}')