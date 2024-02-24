import requests
import argparse
import datetime
from requests_html import HTMLSession
import re
import os
import django
import string

NYT_LEADERBOARD_URL = "https://www.nytimes.com/puzzles/leaderboards"
NYT_LOGIN_URL = "https://myaccount.nytimes.com/auth/enter-email"
NYT_COOKIE = '0^CBYSLwjO6IetBhDZzIutBhoSMS05CzAn46QNq5sU-Kd-ctUvILXPpBwqAgACOOvNidYEGkAlbuMWXlcYsJcGK0pVSj41Y3C5n13IvJzH7mNKUZdkNKsKLnaLyUGqDcQnkF4EL9v8ahf3BAmRvofRTNVKXaIP'
NYT_LEADERBOARD_REGEX = r'"name":\s*"([^"]+)".*?"solveTime":(?:(null)|"([^"]+)")'

parser = argparse.ArgumentParser(description="Crossword Mini Time Scraper")
parser.add_argument('-o', '--output', default='mini_data.csv')

PLAYER_ALIAS = {"Wombat": {"Wombat", "David", "Dave"},
                "Max": {"Max"},
                "Beardality": {"Beardality, Beardo"}}


class WebScrapping:
    def __init__(self):
        print("Initializing")
        os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                              "nytcrossword.settings")  # this has to be called before any django operations
        django.setup()

    def start(self):
        print("Running")
        self._loadWebPage(NYT_LEADERBOARD_URL)
        self._parseDate()
        self._parseLeaderboard()
        self._getScores()
        self._updateDB()

    def _loadWebPage(self, url):
        print("Loading page")
        session = HTMLSession()
        self.r = session.get(url, cookies={'NYT-S': NYT_COOKIE})
        self.r.html.render(reload=False)

    def _parseDate(self):
        print("Parsing info")
        dateString = self.r.html.search('"displayDate":"{}"')[0]
        self.date = datetime.datetime.strptime(dateString, "%A, %B %d, %Y")

        print(self.date)

    def _parseLeaderboard(self):
        print("Parsing leaderboard")
        self.playerData = self.r.html.search('"scoreList":[{}]')[0]
        print(self.playerData)

    def _getScores(self):
        print("Getting scores")
        matches = re.findall(NYT_LEADERBOARD_REGEX, self.playerData)
        printable = set(string.printable)

        self.player_info = {}

        for match in matches:
            name = match[0]
            name = ''.join(filter(lambda x: x in printable,
                                  name)).strip()  # remove funny characters and leading/trailing whitespace

            for original_name, alias_list in PLAYER_ALIAS.items():  # handle aliases
                if name in alias_list:
                    name = original_name
                    break

            if (match[1] == "null"):  # null score won't have quotes around them, so the regex gets a little funny
                solveTime = match[1]
            else:
                solveTime = match[2]
                self.player_info[name] = datetime.datetime.strptime(solveTime,
                                                                    "%M:%S")  # only add if solveTime exists

            print(f"Name: {name}, Solve Time: {solveTime}")

    def _updateDB(self):
        from leaderboard.models import Player
        from leaderboard.models import Score

        # add players and scores to django db if needed
        for player_name, score in self.player_info.items():
            newPlayer, newPlayerCreated = Player.objects.get_or_create(name=player_name)
            Score.objects.get_or_create(date=self.date, time=score, name=Player(id=newPlayer.id))


args = parser.parse_args()
wb = WebScrapping()
wb.start()