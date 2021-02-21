import glob
import json
import pandas as pd
import re

import ENVIRONMENT
from src.functions.utils import getSoupFromUrl

def concatCsv(save_path: str):
    fNames = [i for i in glob.glob('CSV/*.csv')]
    concattedCsv = pd.concat([pd.read_csv(f) for f in fNames])
    concattedCsv.to_csv(save_path, index=False, encoding='utf-8-sig')

def resetPredictionSummaries(j=ENVIRONMENT.PREDICTION_SUMMARIES_PATH):
    with open(j) as json_file:
        d = json.load(json_file)

    d['winningBets'] = 0
    d['losingBets'] = 0
    d['correctTipoffPredictions'] = 0
    d['incorrectTipoffPredictions'] = 0

    with open(j, 'w') as jsonWFile:
        json.dump(d, jsonWFile)

    print('reset prediction summaries')

def createPlayerSkillDictionary():
    with open(ENVIRONMENT.PLAYER_TEAM_PAIR_DICT_PATH) as playerTeamPairsJson:
        ptp = json.load(playerTeamPairsJson)

        playerCodes = set()
        playerSkillDict = {}

        for season in ptp.keys():
            for player in ptp[season].keys():
                playerCodes.add(player)

        for code in playerCodes:
            playerSkillDict[code] = {'mu': 25, 'sigma': 25/3, 'appearances': 0, 'wins': 0, 'losses': 0, 'predicted wins': 0, 'predicted losses': 0}

    with open(ENVIRONMENT.PLAYER_SKILL_DICT_PATH, 'w') as psd:
        json.dump(playerSkillDict, psd)
        print()

def saveActivePlayersTeams(start_season: int):
    # https://www.basketball-reference.com/leagues/NBA_2021_per_game.html
    seasonsList = list()
    seasons = {}

    while start_season < 2022:
        seasonsList.append(str(start_season))
        start_season += 1

    for season in seasonsList:
        season = str(season)
        seasons[season] = {}
        url = 'https://www.basketball-reference.com/leagues/NBA_{}_per_game.html'.format(season)

        soup, statusCode = getSoupFromUrl(url, returnStatus=True)
        print("GET request for season", season, "players list returned status", statusCode)

        noTradePlayerTags = soup.find_all('tr', class_="full_table")
        tradePlayerTags = soup.find_all('tr', class_="italic_text partial_table")
        noTradeSet = set()

        for tag in tradePlayerTags:
            playerNameTag = tag.select('td[data-stat="player"]')[0]
            playerFullName = playerNameTag.contents[0].contents[0]

            tag = str(tag)
            playerCode = re.search(r'(?<=\"/players/./)(.*?)(?=\")', tag).group(0)
            playerTeam = re.search(r'(?<=<a href="/teams/)(.*?)(?=/)', tag).group(0)
            if playerCode in noTradeSet:
                seasons[season][playerFullName] += [playerTeam]
            else:
                seasons[season][playerFullName] = [playerTeam]
            noTradeSet.add(playerCode)
        for tag in noTradePlayerTags:
            playerNameTag = tag.select('td[data-stat="player"]')[0]
            playerFullName = playerNameTag.contents[0].contents[0]

            tag = str(tag)
            playerCode = re.search(r'(?<=\"/players/./)(.*?)(?=\")', tag).group(0)
            if playerCode in noTradeSet:
                continue # skip the trade_players who break the regex
            playerTeam = re.search(r'(?<=<a href="/teams/)(.*?)(?=/)', tag).group(0)
            seasons[season][playerFullName] = [playerTeam]

    with open('Data/JSON/player_team_pairs.json', 'w') as json_file:
        json.dump(seasons, json_file)

    print('saved seasons Data')


def createActivePlayerNameRelationship():
    activePlayers = []

    url = 'https://www.basketball-reference.com/leagues/NBA_2021_per_game.html'
    soup, statusCode = getSoupFromUrl(url, returnStatus=True)
    print("GET request for 2021 players list returned status", statusCode)
    allPlayerTags = soup.find_all('tr', class_="full_table")

    for tag in allPlayerTags:
        tagStr = str(tag)
        playerNameTag = tag.select('td[data-stat="player"]')[0]
        playerFullName = playerNameTag.contents[0].contents[0]
        playerCode = re.search(r'(?<=\"/players/./)(.*?)(?=\")', tagStr).group(0)
        playerNameWithComma = re.search(r'(?<=csk=")(.*?)(?=")', str(playerNameTag)).group(0)
        playerNameLowerLettersOnly = playerFullName.replace(' ', '')
        playerNameLowerLettersOnly = playerNameLowerLettersOnly.replace('-', '')
        playerNameLowerLettersOnly = playerNameLowerLettersOnly.replace('.', '')
        playerNameLowerLettersOnly = playerNameLowerLettersOnly.lower()

        activePlayers.append({
            "bballRefCode": playerCode,
            "fullName": playerFullName,
            "nameWithComma": playerNameWithComma,
            "lowerLettersOnly": playerNameLowerLettersOnly
            # "playerNameTag": tagStr
        })

    with open('Data/JSON/player_name_relationships.json', 'w') as json_file:
        json.dump(activePlayers, json_file)

    print('saved player DB Data')