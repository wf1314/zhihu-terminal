from utils import SpiderBaseclass


class UserSpider(SpiderBaseclass):
    """用户信息爬取"""
    async def get_self_info(self) -> dict:
        """
        获取我的信息
        :return:
        """
        url = 'https://www.zhihu.com/api/v4/me?include=ad_type;available_message_types,' \
              'default_notifications_count,follow_notifications_count,vote_thank_notifications_count,' \
              'messages_count;draft_count;following_question_count;account_status,is_bind_phone,' \
              'is_force_renamed,email,renamed_fullname;ad_type'

        async with self.client.get(url, headers = self.client.headers) as resp:
            result = await resp.json()
            self.logger.debug(result)
        return result