import glob
import json
import unicodedata

import pandas as pd
import re

from nba_api.stats.endpoints import leaguegamefinder
from nba_api.stats.static import teams

import ENVIRONMENT
from src.functions.database_access import getUniversalPlayerName, getBballRefPlayerName, getAllGamesForTeam, \
    getTeamDictionaryFromShortCode, convertBballRefTeamShortCodeToNBA
from src.functions.utils import getSoupFromUrl, removeAllNonLettersAndLowercase


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
            playerUniversalName = getUniversalPlayerName(playerFullName)

            tag = str(tag)
            playerCode = re.search(r'(?<=\"/players/./)(.*?)(?=\")', tag).group(0)
            playerTeam = re.search(r'(?<=<a href="/teams/)(.*?)(?=/)', tag).group(0)
            if playerCode in noTradeSet:
                seasons[season][playerUniversalName]['possibleTeams'] += [playerTeam]
                seasons[season][playerUniversalName]['currentTeam'] = playerTeam
                seasons[season][playerCode]['possibleTeams'] += [playerTeam]
                seasons[season][playerCode]['currentTeam'] = playerTeam
            else:
                seasons[season][playerUniversalName] = {"possibleTeams": [playerTeam]}
                seasons[season][playerCode] = {"possibleTeams": [playerTeam]}
            noTradeSet.add(playerCode)
        for tag in noTradePlayerTags:
            playerNameTag = tag.select('td[data-stat="player"]')[0]
            playerFullName = playerNameTag.contents[0].contents[0]
            playerUniversalName = getUniversalPlayerName(playerFullName)

            tag = str(tag)
            playerCode = re.search(r'(?<=\"/players/./)(.*?)(?=\")', tag).group(0)
            if playerCode in noTradeSet:
                continue # skip the trade_players who break the regex
            playerTeam = re.search(r'(?<=<a href="/teams/)(.*?)(?=/)', tag).group(0)
            seasons[season][playerUniversalName] = {'possibleTeams': [playerTeam]}
            seasons[season][playerUniversalName]['currentTeam'] = playerTeam
            seasons[season][playerCode] = {'possibleTeams': [playerTeam]}
            seasons[season][playerCode]['currentTeam'] = playerTeam

    with open('Data/JSON/player_team_pairs.json', 'w') as json_file:
        json.dump(seasons, json_file)

    print('saved seasons Data')


def createPlayerNameRelationship(startSeason: int=1998):
    activePlayers = []

    urlStub = 'https://www.basketball-reference.com/leagues/NBA_{}_per_game.html'
    while startSeason < 2022:
        url = urlStub.format(str(startSeason))
        soup, statusCode = getSoupFromUrl(url, returnStatus=True)
        print("GET request for", startSeason, "players list returned status", statusCode)
        allPlayerTags = soup.find_all('tr', class_="full_table")

        for tag in allPlayerTags:
            tagStr = str(tag)
            playerNameTag = tag.select('td[data-stat="player"]')[0]
            playerFullName = playerNameTag.contents[0].contents[0]
            playerCode = re.search(r'(?<=\"/players/./)(.*?)(?=\")', tagStr).group(0)
            playerNameWithComma = re.search(r'(?<=csk=")(.*?)(?=")', str(playerNameTag)).group(0)
            universalName = unicodedata.normalize('NFD', playerFullName.replace(".", "")).encode('ascii', 'ignore').decode("utf-8")
            universalName = removeAllNonLettersAndLowercase(universalName)

            activePlayers.append({
                "bballRefCode": playerCode,
                "fullName": playerFullName,
                "nameWithComma": playerNameWithComma,
                "universalName": universalName,
                "alternateNames": []
                # "playerNameTag": tagStr
            })
        startSeason += 1

    for playerDict in activePlayers:
        if playerDict['fullName'] == "Maxi Kleber":
            playerDict['alternateNames'] += ["Maximilian Kleber"]
        elif playerDict['fullName'] == "Garrison Mathews":
            playerDict['alternateNames'] += ["Garison Matthew"]
        elif playerDict['fullName'] == "Danuel House":
            playerDict['alternateNames'] += ["Danuel House Jr."]

    with open('Data/JSON/player_name_relationships.json', 'w') as json_file:
        json.dump(activePlayers, json_file)

    print('saved player DB Data')

def getAllGameData():
    shortCodes = ['NOP', 'IND', 'CHI', 'ORL', 'TOR', 'BKN', 'MIL', 'CLE', 'CHA', 'WAS', 'MIA', 'OKC', 'MIN', 'DET', 'PHX', 'NYK'
                'BOS', 'LAC', 'SAS', 'GSW', 'DAL', 'UTA', 'ATL', 'POR', 'PHI', 'HOU', 'MEM', 'DEN', 'LAL', 'SAC']
    nbaTeams = teams.get_teams()
    teamDicts = [team for team in nbaTeams if team['abbreviation'] in shortCodes]

    def extractId(x):
        return x['id']

    teamIds = map(extractId, teamDicts)

    teamGameList = list()
    for id in teamIds:
        gamefinder = leaguegamefinder.LeagueGameFinder(team_id_nullable=id)
        teamGameList.append(gamefinder.get_data_frames()[0])

    basePath = "Data/CSV/season_summary_data/{}_allgames.csv"
    for teamDf in teamGameList:
        teamName = teamDf.iloc[0]["TEAM_ABBREVIATION"]
        teamDf.to_csv(basePath.format(teamName))
        print("saved data for", teamName)

    print("extracted the game data")

    return teamIds