from datetime import datetime
import feedparser
from src.utils.error_util import ErrorUtil


class FeedParser:
    def __init__(self):
        self.parser = feedparser

    def parse_rss(self, url):
        try:
            feed = self.parser.parse(url)
            news = []
            for entry in feed.entries:
                news_caractersitics = dict()
                news_caractersitics["Title"] = entry.title
                news_caractersitics["Direct URL"] = entry.link
                news_caractersitics["TIMESTAMP"] = datetime.now().timestamp()
                # Casting date into time stamp
                dt = datetime.strptime(entry.published, "%Y-%m-%dT%H:%M:%SZ")
                news_caractersitics["Published"] = dt.timestamp()

                news.append(news_caractersitics)
            return news
        except Exception as e:
            return ErrorUtil.handle_error(e, "Error in parse RSS")
