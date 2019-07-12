
import os
import asyncio
from zhihu_client import ZhihuClient
from data_extractor import DataExtractor
from setting import USER
from setting import PASSWORD
from utils import print_colour


def start():
    print('************************************')
    print('')


def welcome():
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


async def main():
    client = await login(USER, PASSWORD)
    check_setting()
    welcome()
    spider = DataExtractor(client)
    output = await spider.get_self_info()
    print_colour(f'hello {output["name"]} 欢迎使用terminal-zhihu!', 'blue')
    while True:
        try:
            await spider.output_recommend_article()
        except Exception as e:
            print_colour(e, colour='red')
        input('回车刷新')

if __name__ == '__main__':
    asyncio.run(main())