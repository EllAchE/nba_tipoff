import glob
import json
import re
import pandas as pd

import ENVIRONMENT
from ..functions.utils import getSoupFromUrl


def concatCsv(save_path: str):
    fNames = [i for i in glob.glob('CSV/*.csv')]
    concattedCsv = pd.concat([pd.read_csv(f) for f in fNames])
    concattedCsv.to_csv(save_path, index=False, encoding='utf-8-sig')


def saveActivePlayersTeams(start_season):
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

        soup, statusCode = getSoupFromUrl(url, returnStatus=True)
        print("GET request for season", season, "players list returned status", statusCode)


        noTradePlayerTags = soup.find_all('tr', class_="full_table")
        tradePlayerTags = soup.find_all('tr', class_="italic_text partial_table")
        noTradeSet = set() # todo unsolved edge case: a player is traded then plays against their original team, having both on their record for the season

        for tag in tradePlayerTags:
            tag = str(tag)
            player_code = re.search(r'(?<=\"/players/./)(.*?)(?=\")', tag).group(0)
            player_team = re.search(r'(?<=<a href="/teams/)(.*?)(?=/)', tag).group(0)
            if player_code in noTradeSet:
                seasons[season][player_code] += [player_team]
            else:
                seasons[season][player_code] = [player_team]
            noTradeSet.add(player_code)
        for tag in noTradePlayerTags:
            tag = str(tag)
            player_code = re.search(r'(?<=\"/players/./)(.*?)(?=\")', tag).group(0)
            if player_code in noTradeSet:
                continue # skip the trade_players who break the regex
            player_team = re.search(r'(?<=<a href="/teams/)(.*?)(?=/)', tag).group(0)
            seasons[season][player_code] = [player_team]

    with open('../Data/JSON/player_team_pairs.json', 'w') as json_file:
        json.dump(seasons, json_file)

    print('saved seasons Data')


def createPlayerSkillDictionary():
    with open(ENVIRONMENT.PLAYER_SKILL_DICT_PATH) as playerTeamPairsJson:
        ptp = json.load(playerTeamPairsJson)

        player_codes = set()
        player_skill_dict = {}

        for season in ptp.keys():
            for player in ptp[season].keys():
                player_codes.add(player)

        for code in player_codes:
            player_skill_dict[code] = {'mu': 25, 'sigma': 25/3, 'appearances': 0, 'wins': 0, 'losses': 0, 'predicted wins': 0, 'predicted losses': 0}

    with open(ENVIRONMENT.PLAYER_SKILL_DICT_PATH, 'w') as psd:
        json.dump(player_skill_dict, psd)
        print()


def resetPredictionSummaries(j=ENVIRONMENT.PREDICTION_SUMMARIES_PATH):
    with open(j) as json_file:
        d = json.load(json_file)

    d['winningBets'] = 0
    d['losingBets'] = 0
    d['correctTipoffPredictions'] = 0
    d['incorrectTipoffPredictions'] = 0

    with open(j, 'w') as json_w_file:
        json.dump(d, json_w_file)

    print('reset prediction summaries')
