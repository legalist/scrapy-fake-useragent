import json
import logging
import random

from fake_useragent import UserAgent

logger = logging.getLogger(__name__)


class RandomUserAgentMiddleware(object):
    def __init__(self, crawler):
        super(RandomUserAgentMiddleware, self).__init__()

        fallback = crawler.settings.get('FAKEUSERAGENT_FALLBACK', None)
        self.ua = UserAgent(fallback=fallback)
        self.per_proxy = crawler.settings.get('RANDOM_UA_PER_PROXY', False)
        self.ua_type = crawler.settings.get('RANDOM_UA_TYPE', 'random')
        self.proxy2ua = {}

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        def get_ua():
            """Gets random UA based on the type setting (random, firefox)"""
            result = ""
            try:
                result = getattr(self.ua, self.ua_type)
            except Exception as err:
                logger.warning(err)

            if not result:
                data = json.load(open("../user_agents.json"))
                browsers = data.get("browsers")
                random_key = random.choice(list(browsers.keys()))
                result = random.choice(browsers.get(random_key, ""))
            return result

        if self.per_proxy:
            proxy = request.meta.get('proxy')
            if proxy not in self.proxy2ua:
                self.proxy2ua[proxy] = get_ua()
                logger.debug('Assign User-Agent %s to Proxy %s' % (self.proxy2ua[proxy], proxy))
            request.headers.setdefault('User-Agent', self.proxy2ua[proxy])
        else:
            request.headers.setdefault('User-Agent', get_ua())
