"""
保存有知乎登录cookie的ClientSession
"""
import aiohttp
import asyncio
import base64
import execjs
import hmac
import hashlib
import json
import re
import os
import sys
import time
# import threading
from typing import Union
from PIL import Image
from urllib.parse import urlencode
from utils import print_colour
from log import get_logger
from setting import COOKIE_FILE


class ZhihuClient(aiohttp.ClientSession):
    """扩展ClientSession"""

    def __init__(self, user='', password='', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.password = password
        headers = {
            'Host': 'www.zhihu.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586',
            'Connection': 'Keep-Alive',
            'Referer': 'https://www.zhihu.com/',
            'accept-encoding': 'gzip, deflate',
        }
        self.headers = headers
        self.logger = get_logger()
        self.cookie_file = COOKIE_FILE or '/tmp/cookies.pick'

    def get(self, url,  **kwargs):
        """Perform HTTP GET request."""
        return super().get(url, ssl=False,  **kwargs)

    def post(self, url, data=None, **kwargs):
        """Perform HTTP POST request."""
        return super().post(url, ssl=False, data=data, **kwargs)

    def put(self, url, data=None, **kwargs):
        """Perform HTTP PUT request."""
        return super().put(url, ssl=False, data=data, **kwargs)

    async def login(self, load_cookies: bool=False) -> None:
        """
        登录
        :param load_cookies: 是否加载cookie
        :return:
        """
        if load_cookies:
            self.cookie_jar.load(self.cookie_file)
            self.logger.debug(f'加载cookies从:{self.cookie_file}')
            is_succ = await self.check_login()
            if is_succ:
                print_colour('登录成功!', colour='green')
                return
            else:
                print_colour('通过缓存登录失败尝试重新登录', 'red')
                self.cookie_jar.clear()
                os.remove(self.cookie_file)

        login_data = {
            'client_id': 'c3cef7c66a1843f8b3a9e6a1e3160e20',
            'grant_type': 'password',
            'source': 'com.zhihu.web',
            'username': self.user,
            'password': self.password,
            'lang': 'en',  # en 4位验证码, cn 中文验证码
            'ref_source': 'other_https://www.zhihu.com/signin?next=%2F',
            'utm_source': ''
        }
        xsrf = await self._get_xsrf()
        captcha = await self._get_captcha()
        timestamp = int(time.time() * 1000)
        login_data.update({
            'captcha': captcha,
            'timestamp': timestamp,
            'signature': self._get_signature(timestamp, login_data)
        })
        headers = {
            'accept-encoding': 'gzip, deflate, br',
            'Host': 'www.zhihu.com',
            'Referer': 'https://www.zhihu.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586',
            'content-type': 'application/x-www-form-urlencoded',
            'x-zse-83': '3_2.0',
            'x-xsrftoken': xsrf
        }
        data = self._encrypt(login_data)
        url = 'https://www.zhihu.com/api/v3/oauth/sign_in'
        async with self.post(url, data=data, headers=headers) as r:
            resp = await r.text()
            if 'error' in resp:
                print_colour(json.loads(resp)['error'], 'red')
                self.logger.debug(f"登录失败:{json.loads(resp)['error']}")
                sys.exit()
            self.logger.debug(resp)
            is_succ = await self.check_login()
            if is_succ:
                print_colour('登录成功!', colour='green')
            else:
                print_colour('登录失败!', colour='red')
                sys.exit()

    async def _get_captcha(self) -> str:
        """
        请求验证码的 API 接口，无论是否需要验证码都需要请求一次
        如果需要验证码会返回图片的 base64 编码
        :return: 验证码的 POST 参数
        """

        url = 'https://www.zhihu.com/api/v3/oauth/captcha?lang=en'
        async with self.get(url) as r:
            resp = await r.text()
            show_captcha = re.search(r'true', resp)
        if show_captcha:
            async with self.put(url) as r:
                resp = await r.text()
            json_data = json.loads(resp)
            img_base64 = json_data['img_base64'].replace(r'\n', '')
            with open(f'./captcha.jpg', 'wb') as f:
                f.write(base64.b64decode(img_base64))
            img = Image.open(f'./captcha.jpg')
            # if lang == 'cn':
            #     import matplotlib.pyplot as plt
            #     plt.imshow(img)
            #     print('点击所有倒立的汉字，在命令行中按回车提交')
            #     points = plt.ginput(7)
            #     capt = json.dumps({'img_size': [200, 44],
            #                        'input_points': [[i[0] / 2, i[1] / 2] for i in points]})
            # else:
            # img_thread = threading.Thread(target=img.show, daemon=True)
            # img_thread.start()
            # TODO 验证码自动识别实现
            loop = asyncio.get_running_loop()
            loop.run_in_executor(None, img.show)
            capt = input('请输入图片里的验证码：')
            # 这里必须先把参数 POST 验证码接口
            await self.post(url, data={'input_text': capt})
            return capt
        return ''

    async def check_login(self) -> bool:
        """
        检查登录状态，访问登录页面出现跳转则是已登录，
        如登录成功保存当前 Cookies
        :return: bool
        """
        url = 'https://www.zhihu.com/'
        async with self.get(url, allow_redirects=False) as r:
            if r.status == 200:
                self.cookie_jar.save(self.cookie_file)
                self.logger.debug(f'保存cookies到->{self.cookie_file}')
                return True
            else:
                self.logger.debug(await r.text())
                self.logger.debug(r.headers)
                self.logger.debug(r.status)
            return False

    async def _get_xsrf(self) -> str:
        """
        从登录页面获取 xsrf
        :return: str
        """
        async with self.get('https://www.zhihu.com/', allow_redirects=False) as r:
            self.logger.debug('尝试获取xsrf token')
            if r.cookies.get('_xsrf'):
                self.logger.debug(f'获取成功{r.cookies.get("_xsrf").value}')
                return r.cookies.get('_xsrf').value
        raise AssertionError('获取 xsrf 失败')

    def _get_signature(self, timestamp: Union[int, str], login_data: dict) -> str:
        """
        通过 Hmac 算法计算返回签名
        实际是几个固定字符串加时间戳
        :param timestamp: 时间戳
        :return: 签名
        """
        ha = hmac.new(b'd1b964811afb40118a12068ff74a12f4', digestmod=hashlib.sha1)
        grant_type = login_data['grant_type']
        client_id = login_data['client_id']
        source = login_data['source']
        ha.update(bytes((grant_type + client_id + source + str(timestamp)), 'utf-8'))
        return ha.hexdigest()

    # @staticmethod
    # def _encrypt(form_data: dict) -> str:
    #     with open(f'./static/encrypt_old.js') as f:
    #         js = execjs.compile(f.read())
    #         return js.call('Q', urlencode(form_data))

    @staticmethod
    def _encrypt(form_data: dict):
        with open('./static/encrypt.js') as f:
            js = execjs.compile(f.read())
            return js.call('b', urlencode(form_data))


if __name__ == '__main__':
    from setting import USER, PASSWORD

    async def test():
        client = ZhihuClient(user=USER, password=PASSWORD)
        await client.login(load_cookies=False)
        await client.close()

    asyncio.run(test())
