import json
import re

import requests
from bs4 import BeautifulSoup


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

    # def get_team_season_pair(tag):
    #     string = re.search(r'(?<=\"/teams/)(.*?)(?=\.)', str(tag.contents)).group(0)
    #     team, season = string.split('/')
    #     return [team, season]

    #
    # home_wins_possession = False
    # if possession_gaining_team == home_team:
    #     home_wins_possession = True
    # elif possession_gaining_team != away_team:
    #     raise ValueError("player didn't match either team", possession_gaining_player)

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