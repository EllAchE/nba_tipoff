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
import json

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


def get_single_season_game_headers(season):
    normal_months = ["october", "november", "december", "january", "february", "march", "april", "may", "june"]
    months_2020 = ["october-2019", "november", "december", "january", "february", "march", "july", "august",
                   "september", "october-2020"]
    months_2021 = ["december", "january", "february", "march"]  # may be a shortened season

    season_games = list()
    if season == 2020:
        months = months_2020
    elif season == 2021:
        months = months_2021
    else:
        months = normal_months
    for month in months:
        season_games.append(get_single_month_game_headers(season, month))

    return season_games


def get_single_month_game_headers(season, month):
    url = 'https://www.basketball-reference.com/leagues/NBA_{}_games-{}.html'.format(season, month)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    table_game_strs = soup.find_all('th', class_="left")
    table_away_strs = soup.select('td[data-stat="visitor_team_name"]')
    table_home_strs = soup.select('td[data-stat="home_team_name"]')

    month_games = list()
    list_len = len(table_game_strs)
    i = 0
    while i < list_len - 1:
        i += 1
        game_str = str(table_game_strs[i])
        away_str_full = str(table_away_strs[i].a.contents[0])
        home_str_full = str(table_home_strs[i].a.contents[0])

        s_index = game_str.index('csk="') + 5
        away_str_short = str(table_away_strs[i])[s_index:s_index+3]
        home_str_short = str(table_home_strs[i])[s_index:s_index+3]

        month_games.append([game_str[s_index:s_index+12], home_str_full, away_str_full, home_str_short, away_str_short])

    return month_games


def get_game_headers(start_season=2014, start_date=None):
    normal_months = ["october", "november", "december", "january", "february", "march", "april", "may", "june"]
    months_2020 = ["october-2019", "november", "december", "january", "february", "march", "july", "august", "september", "october-2020"]
    months_2021 = ["december", "january", "february", "march"] # may be a shortened season

    seasons_list = list()
    while start_season < 2022:
        seasons_list.append(start_season)
        start_season += 1

    sleep_counter = 0
    game_list = list()

    for season in seasons_list:
        if season == 2020:
            months = months_2020
        elif season == 2021:
            months = months_2021
        else:
            months = normal_months
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

                # game_str = re.match(r'\csk='"\d\d\d\d\d\d\d\d\d\D\D\D\b", str(line)) #todo use regex
                single_list = [game_str[s_index:s_index+12], home_str_full, away_str_full, home_str_short, away_str_short]
                game_list.append(single_list)
    return game_list


def sleep_checker(sleep_counter, iterations=3, base_time=2):
    sleep_counter += 1
    if sleep_counter % (iterations + 1) == 0:
        print("sleeping for", str(base_time), "+ random seconds")
        time.sleep(base_time + random.random() * 3)
        sleep_counter = 0
    return sleep_counter


# def get_team_season_pair(tag):
#     string = re.search(r'(?<=\"/teams/)(.*?)(?=\.)', str(tag.contents)).group(0)
#     team, season = string.split('/')
#     return [team, season]


def get_player_team_in_season(player_link, season):
    # assumes good data
    player_link = player_link[11:]
    with open('player_team_pairs.json') as team_pairs:
        seasons = json.load(team_pairs)

        try:
            return seasons[str(season)][player_link]
        except:
            return player_link



    # # https://www.basketball-reference.com/players/g/georgpa01.html
    # url = 'https://www.basketball-reference.com/{}'.format(player_link)
    # page = requests.get(url)
    # soup = BeautifulSoup(page.content, 'html.parser')
    # all_team_matches_in_table = soup.select('td[data-stat="team_id"]')
    # possible_teams = set()
    #
    # for line in all_team_matches_in_table:
    #     if re.search(r'a-stat="team_id"><a href="/teams/', str(line)) is not None:
    #         index = str(line).index('a-stat="team_id"><a href="/teams/') + 33
    #         if str(line)[(index + 4):(index + 8)] == str(season):
    #             possible_teams.add(str(line)[index:(index + 3)])
    #
    # return possible_teams

    # sleep_counter = 0
    # team_season_pairs = list()
    # print(all_team_matches_in_table)
    # for tag in all_team_matches_in_table[:-1]:
    #     sleep_counter = sleep_checker(sleep_counter, iterations=5)
    #     team_season_pairs.append(get_team_season_pair(tag))
    #
    # for pair in team_season_pairs:
    #     if pair[1] == str(season):
    #         return pair[0]
    # return None


def get_tipoff_winner_and_first_score(game_link, season, home_team, away_team):
    # https://www.basketball-reference.com/boxscores/pbp/201901220OKC.html
    url = 'https://www.basketball-reference.com/boxscores/pbp/{}.html'.format(game_link)
    page = requests.get(url)
    print("GET request for game", game_link, "returned status", page.status_code)

    soup = BeautifulSoup(page.content, 'html.parser')
    possession_win_line = soup.select('td[colspan="5"]')[0].contents
    first_score_line_options = soup.find_all('td', class_='bbr-play-score', limit=2)[:2]  # todo fix this to choose right side
    if re.search(r'makes', str(first_score_line_options[0])) is not None:
        first_score_line = first_score_line_options[0].contents
    else:
        first_score_line = first_score_line_options[1].contents

    first_scoring_player = first_score_line[0].contents[0]
    # link_index = str(first_score_line[0]).index('"')
    first_scoring_player_link = re.search(r'(?<=")(.*?)(?=")', str(first_score_line[0])).group(0)
    try:
        possession_gaining_player_link = re.search(r'(?<=")(.*?)(?=")', str(possession_win_line[5])).group(0)

        home_tipper = possession_win_line[1].contents[0]
        # home_tipper_link = re.search(r'(?<=")(.*?)(?=")', str(possession_win_line[1])).group(0)
        away_tipper = possession_win_line[3].contents[0]
        # away_tipper_link = re.search(r'(?<=")(.*?)(?=")', str(possession_win_line[3])).group(0)

        possible_teams = get_player_team_in_season(possession_gaining_player_link, season)
        if home_team in possible_teams:
            possession_gaining_team = home_team
        else:
            possession_gaining_team = away_team # todo no error checks here

        possible_teams = get_player_team_in_season(first_scoring_player_link, season)
        if home_team in possible_teams:
            first_scoring_team = home_team
        else:
            first_scoring_team = away_team
        #
        # home_wins_possession = False
        # if possession_gaining_team == home_team:
        #     home_wins_possession = True
        # elif possession_gaining_team != away_team:
        #     raise ValueError("player didn't match either team", possession_gaining_player)

        return [home_tipper, away_tipper, first_scoring_player, possession_gaining_team, first_scoring_team]
    except:
        return [None, None, None, None, None]


def save_active_players_teams(start_season):
    # https://www.basketball-reference.com/leagues/NBA_2021_per_game.html
    seasons_list = list()
    while start_season < 2022:
        seasons_list.append(str(start_season))
        start_season += 1

    seasons = {}

    for season in seasons_list:
        season = str(season)
        seasons[season] = {}
        url = 'https://www.basketball-reference.com/leagues/NBA_{}_per_game.html'.format(season)

        page = requests.get(url)
        print("GET request for season", season, "players list returned status", page.status_code)
        soup = BeautifulSoup(page.content, 'html.parser')

        no_trade_player_tags = soup.find_all('tr', class_="full_table")
        trade_player_tags = soup.find_all('tr', class_="italic_text partial_table")
        no_trade_set = set()

        for tag in trade_player_tags:
            tag = str(tag)
            player_code = re.search(r'(?<=\"/players/./)(.*?)(?=\")', tag).group(0)
            player_team = re.search(r'(?<=<a href="/teams/)(.*?)(?=/)', tag).group(0)
            if player_code in no_trade_set:
                seasons[season][player_code] += [player_team]
            else:
                seasons[season][player_code] = [player_team]
            no_trade_set.add(player_code)
        for tag in no_trade_player_tags:
            tag = str(tag)
            player_code = re.search(r'(?<=\"/players/./)(.*?)(?=\")', tag).group(0)
            if player_code in no_trade_set:
                continue # skip the trade_players who break the regex
            player_team = re.search(r'(?<=<a href="/teams/)(.*?)(?=/)', tag).group(0)
            seasons[season][player_code] = [player_team]
    with open('player_team_pairs.json', 'w') as json_file:
        json.dump(seasons, json_file)

    print('saved seasons data')
