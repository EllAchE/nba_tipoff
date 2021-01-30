import json
import math

from bs4 import BeautifulSoup
import requests
import time
import random
import re


# todo offensive/defensive efficiency
# http://www.espn.com/nba/hollinger/teamstats/_/year/2003

# todo historical betting lines
# https://widgets.digitalsportstech.com/api/gp?sb=bovada&tz=-5&gameId=in,135430

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
        games_list = get_single_month_game_headers(season, month)
        for game in games_list:
            season_games.append(game)

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

        game_short = game_str[s_index:s_index+12]
        game_long = 'https://www.basketball-reference.com/boxscores/pbp/' + game_short + '.html'

        month_games.append([game_short, game_long, home_str_full, away_str_full, home_str_short, away_str_short])

    return month_games


def sleep_checker(sleep_counter, iterations=3, base_time=2, random_multiplier=3):
    sleep_counter += 1
    if sleep_counter % iterations == 0:
        print("sleeping for", str(base_time), "+ random seconds")
        time.sleep(base_time + random.random() * random_multiplier)
        sleep_counter = 0
    return sleep_counter


def get_player_team_in_season(player_link, season, long_code=True):
    if long_code:
        player_link = player_link[11:]
    with open('player_team_pairs.json') as team_pairs:
        seasons = json.load(team_pairs)
        try:
            return seasons[str(season)][player_link]
        except:
            return player_link


def in_progress_unbroken(game_link, season, home_team, away_team):
    # https://www.basketball-reference.com/boxscores/pbp/201901220OKC.html
    url = 'https://www.basketball-reference.com/boxscores/pbp/{}.html'.format(game_link)
    page = requests.get(url)
    print("GET request for game", game_link, "returned status", page.status_code)

    soup = BeautifulSoup(page.content, 'html.parser')
    table = soup.select('table[id="pbp"]')[0]
    current_line = table.find('tr')
    first_line = current_line
    break_case = False
    possible_scores = ['0-0', '1-0', '2-0', '3-0', '0-1', '0-2', '0-3']

    while not break_case:
        next_td_elem = current_line.td
        while next_td_elem is not None and next_td_elem.contents not in possible_scores:
            next_td_elem = next_td_elem.next_sibling
        if next_td_elem.contents in possible_scores:
            break_case = True
        else:
            current_line = current_line.next_sibling

    first_line_with_score = None

    # todo edge case is Violation by Team

    possession_win_line = soup.select('td[colspan="5"]')[0].contents
    if str(possession_win_line[0]) == "Start of 1st quarter":
        possession_win_line = soup.select('td[colspan="5"]')[1].contents
    first_score_line_options = soup.find_all('td', class_='bbr-play-score', limit=2)[:2]  # todo fix this to choose right side
    if re.search(r'makes', str(first_score_line_options[0])) is not None:
        first_score_line = first_score_line_options[0].contents
    else:
        first_score_line = first_score_line_options[1].contents

    first_scoring_player = first_score_line[0].contents[0]
    first_scoring_player_link = re.search(r'(?<=")(.*?)(?=")', str(first_score_line[0])).group(0)
    try:
        possession_gaining_player_link = re.search(r'(?<=")(.*?)(?=")', str(possession_win_line[5])).group(0)
        possession_gaining_player = str(possession_win_line[5].contents[0])

        tipper1 = possession_win_line[1].contents[0]
        tipper1_link = re.search(r'(?<=")(.*?)(?=")', str(possession_win_line[1])).group(0)
        tipper2 = possession_win_line[3].contents[0]
        tipper2_link = re.search(r'(?<=")(.*?)(?=")', str(possession_win_line[3])).group(0)

        if home_team in get_player_team_in_season(tipper1_link, season):
            home_tipper = tipper1
            away_tipper = tipper2
            home_tipper_link = tipper1_link
            away_tipper_link = tipper2_link
        else:
            home_tipper = tipper2
            away_tipper = tipper1
            home_tipper_link = tipper2_link
            away_tipper_link = tipper1_link

        if home_team in get_player_team_in_season(possession_gaining_player_link, season):
            possession_gaining_team = home_team
            possession_losing_team = away_team
            tipoff_winner = home_tipper
            tipoff_loser = away_tipper
            tipoff_winner_link = home_tipper_link
            tipoff_loser_link = away_tipper_link
        else:
            possession_gaining_team = away_team
            possession_losing_team = home_team
            tipoff_winner = away_tipper
            tipoff_loser = home_tipper
            tipoff_winner_link = away_tipper_link
            tipoff_loser_link = home_tipper_link

        if home_team in get_player_team_in_season(first_scoring_player_link, season):
            first_scoring_team = home_team
            scored_upon_team = away_team
        else:
            first_scoring_team = away_team
            scored_upon_team = home_team

        if possession_gaining_team == first_scoring_team:
            tip_win_score = 1
        else:
            tip_win_score = 0

        return [home_tipper, away_tipper, first_scoring_player, possession_gaining_team, possession_losing_team,
                possession_gaining_player, possession_gaining_player_link, first_scoring_team, scored_upon_team,
                tipoff_winner, tipoff_winner_link, tipoff_loser, tipoff_loser_link, tip_win_score]
    except:
        return [None, None, None, None, None, None, None, None, None, None, None, None]


def get_current_starters(team_code): #todo need a scraper for one of these
    # https://www.rotowire.com/basketball/nba-lineups.php
    # https://www.nba.com/players/todays-lineups
    # stats api here - https://stats.nba.com/js/data/leaders/00_active_starters_20210128.json
    # https://rotogrinders.com/lineups/nba
    # https://dailynbalineups.com/
    pass


def get_tipoff_winner_and_first_score(game_link, season, home_team, away_team):
    # https://www.basketball-reference.com/boxscores/pbp/201901220OKC.html
    url = 'https://www.basketball-reference.com/boxscores/pbp/{}.html'.format(game_link)
    page = requests.get(url)
    print("GET request for game", game_link, "returned status", page.status_code)

    soup = BeautifulSoup(page.content, 'html.parser')
    table = soup.select('table[id="pbp"]')
    possession_win_line = soup.select('td[colspan="5"]')[0].contents
    if str(possession_win_line[0]) == "Start of 1st quarter":
        possession_win_line = soup.select('td[colspan="5"]')[1].contents
    first_score_line_options = soup.find_all('td', class_='bbr-play-score', limit=2)[:2]
    if re.search(r'makes', str(first_score_line_options[0])) is not None:
        first_score_line = first_score_line_options[0].contents
    else:
        first_score_line = first_score_line_options[1].contents

    first_scoring_player = first_score_line[0].contents[0]
    first_scoring_player_link = re.search(r'(?<=")(.*?)(?=")', str(first_score_line[0])).group(0)
    try:
        possession_gaining_player_link = re.search(r'(?<=")(.*?)(?=")', str(possession_win_line[5])).group(0)
        possession_gaining_player = str(possession_win_line[5].contents[0])

        tipper1 = possession_win_line[1].contents[0]
        tipper1_link = re.search(r'(?<=")(.*?)(?=")', str(possession_win_line[1])).group(0)
        tipper2 = possession_win_line[3].contents[0]
        tipper2_link = re.search(r'(?<=")(.*?)(?=")', str(possession_win_line[3])).group(0)

        if home_team in get_player_team_in_season(tipper1_link, season):
            home_tipper = tipper1
            away_tipper = tipper2
            home_tipper_link = tipper1_link
            away_tipper_link = tipper2_link
        else:
            home_tipper = tipper2
            away_tipper = tipper1
            home_tipper_link = tipper2_link
            away_tipper_link = tipper1_link

        if home_team in get_player_team_in_season(possession_gaining_player_link, season):
            possession_gaining_team = home_team
            possession_losing_team = away_team
            tipoff_winner = home_tipper
            tipoff_loser = away_tipper
            tipoff_winner_link = home_tipper_link
            tipoff_loser_link = away_tipper_link
        else:
            possession_gaining_team = away_team
            possession_losing_team = home_team
            tipoff_winner = away_tipper
            tipoff_loser = home_tipper
            tipoff_winner_link = away_tipper_link
            tipoff_loser_link = home_tipper_link

        if home_team in get_player_team_in_season(first_scoring_player_link, season):
            first_scoring_team = home_team
            scored_upon_team = away_team
        else:
            first_scoring_team = away_team
            scored_upon_team = home_team

        if possession_gaining_team == first_scoring_team:
            tip_win_score = 1
        else:
            tip_win_score = 0

        return [home_tipper, away_tipper, first_scoring_player, possession_gaining_team, possession_losing_team,
                possession_gaining_player, possession_gaining_player_link, first_scoring_team, scored_upon_team,
                tipoff_winner, tipoff_winner_link, tipoff_loser, tipoff_loser_link, tip_win_score]
    except:
        return [None, None, None, None, None, None, None, None, None, None, None, None]



# def get_game_headers(start_season=2014, start_date=None):
#     normal_months = ["october", "november", "december", "january", "february", "march", "april", "may", "june"]
#     months_2020 = ["october-2019", "november", "december", "january", "february", "march", "july", "august", "september", "october-2020"]
#     months_2021 = ["december", "january", "february", "march"] # may be a shortened season
#
#     seasons_list = list()
#     while start_season < 2022:
#         seasons_list.append(start_season)
#         start_season += 1
#
#     sleep_counter = 0
#     game_list = list()
#
#     for season in seasons_list:
#         if season == 2020:
#             months = months_2020
#         elif season == 2021:
#             months = months_2021
#         else:
#             months = normal_months
#         for month in months:
#             url = 'https://www.basketball-reference.com/leagues/NBA_{}_games-{}.html'.format(season, month)
#             page = requests.get(url)
#             print("GET request for season", season, "month", month, "returned status", page.status_code)
#             soup = BeautifulSoup(page.content, 'html.parser')
#             sleep_counter = sleep_checker(sleep_counter)
#             table_game_strs = soup.find_all('th', class_="left")
#             table_away_strs = soup.select('td[data-stat="visitor_team_name"]')
#             table_home_strs = soup.select('td[data-stat="home_team_name"]')
#             list_len = len(table_game_strs)
#             i = 0
#
#             while i < list_len - 1:
#                 i += 1
#                 game_str = str(table_game_strs[i])
#                 away_str_full = str(table_away_strs[i].a.contents[0])
#                 home_str_full = str(table_home_strs[i].a.contents[0])
#
#                 s_index = game_str.index('csk="') + 5
#                 away_str_short = str(table_away_strs[i])[s_index:s_index+3]
#                 home_str_short = str(table_home_strs[i])[s_index:s_index+3]
#
#                 single_list = [game_str[s_index:s_index+12], home_str_full, away_str_full, home_str_short, away_str_short]
#                 game_list.append(single_list)
#     return game_list