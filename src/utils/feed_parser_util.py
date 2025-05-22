from datetime import datetime
import feedparser


class FeedParser:
    def __init__(self):
        self.parser = feedparser

    def parse_rss(self, url):
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
