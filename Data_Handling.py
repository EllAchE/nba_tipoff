import glob
import json
import re
import pandas as pd

import requests
from bs4 import BeautifulSoup


def concat_csv(save_path):
    f_names = [i for i in glob.glob('CSV/*.csv')]
    concatted_csv = pd.concat([pd.read_csv(f) for f in f_names])
    concatted_csv.to_csv(save_path, index=False, encoding='utf-8-sig')


def save_active_players_teams(start_season):
    # https://www.basketball-reference.com/leagues/NBA_2021_per_game.html
    seasons_list = list()
    seasons = {}

    while start_season < 2023:
        seasons_list.append(str(start_season))
        start_season += 1

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

    with open('Data/player_team_pairs.json', 'w') as json_file:
        json.dump(seasons, json_file)

    print('saved seasons Data')


def create_player_skill_dictionary():
    with open('Data/player_team_pairs.json') as player_team_pairs_json:
        ptp = json.load(player_team_pairs_json)

        player_codes = set()
        player_skill_dict = {}

        for season in ptp.keys():
            for player in ptp[season].keys():
                player_codes.add(player)

        for code in player_codes:
            player_skill_dict[code] = {'mu': 25, 'sigma': 25/3, 'appearances': 0, 'wins': 0, 'losses': 0, 'predicted wins': 0, 'predicted losses': 0}

    with open('Data/player_skill_dictionary.json', 'w') as psd:
        json.dump(player_skill_dict, psd)
        print()


def reset_prediction_summaries(j='prediction_summaries.json'):
    with open(j) as json_file:
        d = json.load(json_file)

    d['winningBets'] = 0
    d['losingBets'] = 0
    d['correctTipoffPredictions'] = 0
    d['incorrectTipoffPredictions'] = 0

    with open(j, 'w') as json_w_file:
        json.dump(d, json_w_file)

    print('reset prediction summaries')
