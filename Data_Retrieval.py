'''
Retrieves raw data from pages as csv

Steps to NBA check:

Base requirements:
-	Find the starters for each team/who does the tipoff:
-	Player W/L %

Additional variables
-	Ref
-	Is starter out
-	Home/away
-	Who they tip it to
-	Matchup
-	Height
-	Offensive effectiveness
-	Back-to-back games/overtime etc.
-	Age decline
-	Recent history weighting

Format is https://www.basketball-reference.com/boxscores/pbp/201901220OKC.html
Home team 3 letter symbol is used after a 0, i.e. YYYYMMDD0###.html
https://fansided.com/stats/jump-ball-statistics-1998-present/
Guy who compiled the tip off stats https://twitter.com/FattMemrite
https://sportsbook.draftkings.com/leagues/basketball/103?category=game-props&subcategory=first-team-to-score
'''

# Request URL https://www.basketball-reference.com/boxscores/pbp/201901220OKC.html
# Where YYYYMMDD0### (# = home team code)

# game schedule in order for seasons https://www.basketball-reference.com/leagues/NBA_2019_games.html
# Creating json/dictonary would probably be best

# Games played https://www.basketball-reference.com/leagues/NBA_2019_games-october.html
# Year is ending year (i.e. 2018-2019 is 2019)
# All relevant are October-June except 2019-2020 and 2020-21 (first bc covid, second is in progress)

from bs4 import BeautifulSoup
import requests
import time
import random
import re

# todo get scraper retrieving proper data from arbitrary file
# todo get list of all nba games played, regular season & playoff
# todo get means of generating request urls to hit
# todo get means of storing data
# todo get means of aggregating data


def get_games_played_links(start_season=2014, start_date=None):

    #normal_months = ["october", "november", "december", "january", "february", "march", "april", "may", "june"]
    #months_2020 = ["october-2019", "november", "december", "january", "february", "march", "july", "august", "september", "october-2020"]
    #months_2021 = ["december", "january", "february", "march"] # may be a shortened season
    start_season = 2021
    months = ["december"]

    # regex -> csk="dddddddddaaa"

    seasons_list = list()
    df_list = list()
    while start_season < 2022:
        seasons_list.append(str(start_season))
        start_season += 1

    sleep_counter = 0
    for season in seasons_list:
        # if season == 2020:
        #     months = months_2020
        # elif season == 2021:
        #     months = months_2021
        # else:
        #     months = normal_months
        for month in months:
            url = 'https://www.basketball-reference.com/leagues/NBA_{}_games-{}.html'.format(season, month)
            page = requests.get(url)
            print("GET request for season", season, "month", month, "returned status", page.status_code)
            soup = BeautifulSoup(page.content, 'html.parser')
            sleep_counter = sleep_checker(sleep_counter)
            table = soup.find_all('th', class_="left")
            game_list = list()
            for line in table:
                game_str = str(line)
                s_index = game_str.index('csk="') + 5
                # game_str = re.match(r'\csk='"\d\d\d\d\d\d\d\d\d\D\D\D\b", str(line)) #todo make this work with regex
                game_list.append(game_str[s_index:s_index+12])
                print(game_str[s_index:s_index+12])

            # for game_link in soup.select_all('div'):
            #     print(game_link)

    pass


def sleep_checker(sleep_counter):
    sleep_counter += 1
    if sleep_counter % 4 == 0:
        print("sleeping for 2 + random seconds")
        time.sleep(2 + random.random() * 3)
        sleep_counter = 0
    return sleep_counter

get_games_played_links()

def generate_request_urls(games_data):

    pass
