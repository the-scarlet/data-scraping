import requests
from bs4 import BeautifulSoup

# # Fetch Google Alerts page (after logging in manually)
# url = "https://www.google.com/alerts"
# response = requests.get(url)
# soup = BeautifulSoup(response.text, "html.parser")

# # Extract RSS link
# rss_link = soup.select_one("div.alert_buttons a[href^='/alerts/feeds/']")["href"]
# print("RSS Feed:", rss_link)


class BS:
    def __init__(self):
        pass
