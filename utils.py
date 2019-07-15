from typing import Any

"""
前景色	背景色	颜色
30	40	黑色
31	41	红色
32	42	绿色
33	43	黃色
34	44	蓝色(有问题)
35	45	紫红色
36	46	青蓝色
37	47	白色

显示方式	意义
0	终端默认设置
1	高亮显示
4	使用下划线
5	闪烁
7	反白显示
8	不可见
"""
colour_map = {
    'black': '30',
    'red': '31',
    'green': '32',
    'yellow': '33',
    'blue': '34',
    'purple': '35',
    'ultramarine': '36',
    'white': '37',
}


def print_colour(s: Any, colour: str='green', way: int=0, **kwargs):
    """打印颜色"""
    print(f'\033[{way};{colour_map[colour]};m{s}', **kwargs)


class SpiderBaseclass(object):

    def __init__(self, client):
        self.client = client
        self.logger = self.client.logger

