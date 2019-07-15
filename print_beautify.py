from utils import print_colour


def print_recommend_article(output):
    for d in output:
        print_colour('-' * 150, 'black')
        print_colour(f'id:{d["id"]}')
        print_colour(d['title'], 'purple', end='')
        print_colour(f"({d['author']['name']})", 'purple')
        print_colour(d['excerpt'], colour='blue')
        print_colour(f"*赞同数{d['voteup_count']} 感谢数{d.get('thanks_count', 0)} "
                     f"评论数{d['comment_count']} 浏览数{d['visited_count']}*", 'purple')