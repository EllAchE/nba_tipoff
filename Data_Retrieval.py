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

# URL for game https://www.basketball-reference.com/boxscores/pbp/201901220OKC.html
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

    # normal_months = ["october", "november", "december", "january", "february", "march", "april", "may", "june"]
    # months_2020 = ["october-2019", "november", "december", "january", "february", "march", "july", "august", "september", "october-2020"]
    # months_2021 = ["december", "january", "february", "march"] # may be a shortened season
    months = ["december"]

    seasons_list = list()
    while start_season < 2022:
        seasons_list.append(str(start_season))
        start_season += 1

    sleep_counter = 0
    game_list = list()
    seasons_list = ["2019"]
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
            table_game_strs = soup.find_all('th', class_="left")
            table_away_strs = soup.select('td[data-stat="visitor_team_name"]')
            table_home_strs = soup.select('td[data-stat="home_team_name"]')
            list_len = len(table_game_strs)
            i = 0

            while i < list_len - 1:
                i += 1
                game_str = str(table_game_strs[i])
                away_str_full = str(table_away_strs[i].a.contents[0])
                home_str_full = str(table_home_strs[i].a.contents[0])

                s_index = game_str.index('csk="') + 5
                # away_index = str(table_away_strs[i]).index('csk="') + 5
                # home_index = str(table_home_strs[i]).index('csk="') + 5
                away_str_short = str(table_away_strs[i])[s_index:s_index+3]
                home_str_short = str(table_home_strs[i])[s_index:s_index+3]

                # game_str = re.match(r'\csk='"\d\d\d\d\d\d\d\d\d\D\D\D\b", str(line)) #todo make this work with regex
                single_list = [game_str[s_index:s_index+12], home_str_full, away_str_full, home_str_short, away_str_short]
                game_list.append(single_list)
                # todo need to add home and away team pull here
    return game_list


def sleep_checker(sleep_counter, base_time=2):
    sleep_counter += 1
    if sleep_counter % 4 == 0:
        print("sleeping for 2 + random seconds")
        time.sleep(base_time + random.random() * 3)
        sleep_counter = 0
    return sleep_counter


def get_team_season_pairs(tag):
    string = re.search(r'(?<=\"/teams/)(.*?)(?=\.)', str(tag.contents)).group(0)
    team, season = string.split('/')
    return [team, season]


def get_player_team_in_season(player_link, season):
    # https://www.basketball-reference.com/players/g/georgpa01.html
    url = 'https://www.basketball-reference.com/{}'.format(player_link)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    all_team_matches_in_table = soup.select('td[data-stat="team_id"]')

    team_season_pairs = list()
    for tag in all_team_matches_in_table:
        team_season_pairs.append(get_team_season_pairs(tag))

    print()
    # team_short = all_team_matches_in_table.map all_team_matches_in_table.contents.a.contents # Map this
    # example of player with midseason trade James Harden
    pass


def get_tipoff_winner_and_first_score(game_link, season, home_team, away_team):
    # https://www.basketball-reference.com/boxscores/pbp/201901220OKC.html
    url = 'https://www.basketball-reference.com/boxscores/pbp/{}.html'.format(game_link)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    possession_win_line = soup.select('td[colspan="5"]')[0].contents
    first_score_line = soup.find_all('td', class_='bbr-play-score', limit=2)[1].contents  # second one

    first_scoring_player = first_score_line[0].contents[0]
    # link_index = str(first_score_line[0]).index('"')
    first_scoring_player_link = re.search(r'(?<=")(.*?)(?=")', str(first_score_line[0])).group(0)
    possession_gaining_player = possession_win_line[5].contents[0]
    possession_gaining_player_link = re.search(r'(?<=")(.*?)(?=")', str(possession_win_line[5])).group(0)

    home_tipper = possession_win_line[1].contents[0]
    # home_tipper_link = re.search(r'(?<=")(.*?)(?=")', str(possession_win_line[1])).group(0)
    away_tipper = possession_win_line[3].contents[0]
    # away_tipper_link = re.search(r'(?<=")(.*?)(?=")', str(possession_win_line[3])).group(0)

    possession_gaining_team = get_player_team_in_season(possession_gaining_player_link, season)
    first_scoring_team = get_player_team_in_season(first_scoring_player_link, season)
    home_wins = False
    if possession_gaining_team == home_team:
        home_wins = True
    elif possession_gaining_player != away_team:
        raise ValueError("player didn't match either team")

    return home_tipper, away_tipper, first_scoring_player, possession_gaining_team, first_scoring_team, home_wins

# get_tipoff_winner_and_first_score('201901220OKC', 2020, 'DAL', 'OKC')
# get_games_played_links()
get_player_team_in_season('/players/g/georgpa01.html', 2018)
