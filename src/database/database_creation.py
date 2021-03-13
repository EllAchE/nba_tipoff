import glob
import json
import unicodedata

import pandas as pd
import re

from nba_api.stats.endpoints import leaguegamefinder
from nba_api.stats.static import teams

import ENVIRONMENT
from src.database.database_access import getUniversalPlayerName
from src.utils import getSoupFromUrl, removeAllNonLettersAndLowercase, sleepChecker


def concatCsv(save_path: str):
    fNames = [i for i in glob.glob('CSV/*.csv')]
    concattedCsv = pd.concat([pd.read_csv(f) for f in fNames])
    concattedCsv.to_csv(save_path, index=False, encoding='utf-8-sig')

def resetAndInitializePredictionSummaryDict(histogramBinDivisions, path):
    intervalList = list()
    i = 0
    lstLen = len(histogramBinDivisions)

    while i < lstLen - 1:
        subDsd = {
            "totalMatchups": 0,
            "tipoffWinsByHigher": 0,
            "tipoffLossesByHigher": 0,
            "tipWinnerScores": 0,
            "winPercentage": 0,
            "expectedTipWinsFromAlgo": 0,
            "higherOddsScoresFirst": 0,
            "winningBets": 0,
            "losingBets": 0,
        }
        intervalList.append({
            "start": histogramBinDivisions[i],
            "end": histogramBinDivisions[i + 1],
            "predictionSummaries": subDsd
        })
        i += 1
    dsd = {
        "winningBets": 0,
        "losingBets": 0,
        "totalBets": 0,
        "correctTipoffPredictions": 0,
        "incorrectTipoffPredictions": 0,
        "tipWinnerScores": 0,
        "seasons": None,
        "winPercentage": 0,
        "correctTipoffPredictionPercentage": 0,
        "expectedTipWinsFromAlgo": 0,
        "predictionAverage": 0,
        "histogramDivisions": intervalList,
    }

    with open(path, 'w') as json_file:
        json.dump(dsd, json_file, indent=4)

    return dsd

def createPlayerEloDictionary(path=ENVIRONMENT.PLAYER_ELO_DICT_PATH):
    with open(ENVIRONMENT.PLAYER_TEAM_PAIRS_PATH) as playerTeamPairsJson:
        ptp = json.load(playerTeamPairsJson)

        playerCodes = set()
        playerSkillDict = {}

        for season in ptp.keys():
            for player in ptp[season].keys():
                playerCodes.add(player)

        for code in playerCodes:
            playerSkillDict[code] = {'elo': ENVIRONMENT.BASE_ELO, 'appearances': 0, 'wins': 0, 'losses': 0, 'predicted wins': 0, 'predicted losses': 0}

    with open(path, 'w') as psd:
        json.dump(playerSkillDict, psd, indent=4)

def createPlayerGlickoDictionary(path=ENVIRONMENT.PLAYER_GLICKO_DICT_PATH):
    with open(ENVIRONMENT.PLAYER_TEAM_PAIRS_PATH) as playerTeamPairsJson:
        ptp = json.load(playerTeamPairsJson)

        playerCodes = set()
        playerSkillDict = {}

        for season in ptp.keys():
            for player in ptp[season].keys():
                playerCodes.add(player)

        for code in playerCodes:
            playerSkillDict[code] = {'mu': ENVIRONMENT.BASE_GLICKO_MU, 'sigma': ENVIRONMENT.BASE_GLICKO_SIGMA, 'phi': ENVIRONMENT.BASE_GLICKO_PHI, 'appearances': 0, 'wins': 0, 'losses': 0, 'predicted wins': 0, 'predicted losses': 0}

    with open(path, 'w') as psd:
        json.dump(playerSkillDict, psd, indent=4)

def createPlayerTrueSkillDictionary(path=ENVIRONMENT.PLAYER_TRUESKILL_DICT_PATH):
    with open(ENVIRONMENT.PLAYER_TEAM_PAIRS_PATH) as playerTeamPairsJson:
        ptp = json.load(playerTeamPairsJson)

        playerCodes = set()
        playerSkillDict = {}

        for season in ptp.keys():
            for player in ptp[season].keys():
                playerCodes.add(player)

        for code in playerCodes:
            playerSkillDict[code] = {'mu': ENVIRONMENT.BASE_TS_MU, 'sigma': ENVIRONMENT.BASE_TS_SIGMA, 'appearances': 0, 'wins': 0, 'losses': 0, 'predicted wins': 0, 'predicted losses': 0}

    with open(path, 'w') as psd:
        json.dump(playerSkillDict, psd, indent=4)

def saveActivePlayersTeams(start_season: int):
    # https://www.basketball-reference.com/leagues/NBA_2021_per_game.html
    seasonsList = list()
    while start_season < 2022:
        seasonsList.append(str(start_season))
        start_season += 1

    for season in seasonsList:
        singleSeasonPlayerTeamPairs(season)
    print('saved seasons Data')

def singleSeasonPlayerTeamPairs(season):
    with open(ENVIRONMENT.PLAYER_TEAM_PAIRS_PATH) as json_file:
        seasons = json.load(json_file)

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
            continue  # skip the trade_players who break the regex
        playerTeam = re.search(r'(?<=<a href="/teams/)(.*?)(?=/)', tag).group(0)
        seasons[season][playerUniversalName] = {'possibleTeams': [playerTeam]}
        seasons[season][playerUniversalName]['currentTeam'] = playerTeam
        seasons[season][playerCode] = {'possibleTeams': [playerTeam]}
        seasons[season][playerCode]['currentTeam'] = playerTeam

    with open(ENVIRONMENT.PLAYER_TEAM_PAIRS_PATH, 'w') as json_file:
        json.dump(seasons, json_file, indent=4)


# backlogtodo edit the methods inside here to use append
def updateCurrentSeasonPlayerData():
    createPlayerNameRelationship(ENVIRONMENT.CURRENT_SEASON)
    saveActivePlayersTeams(ENVIRONMENT.CURRENT_SEASON)

def createPlayerNameRelationship(startSeason: int=1998):
    activePlayers = []

    urlStub = 'https://www.basketball-reference.com/leagues/NBA_{}_per_game.html'
    while startSeason < 2022:
        startSeason, activePlayers = singlePlayerNameRelationshipRequest(activePlayers, startSeason, urlStub)

    for playerDict in activePlayers:
        if playerDict['fullName'] == "Maxi Kleber":
            playerDict['alternateNames'] += ["Maximilian Kleber"]
        elif playerDict['fullName'] == "Garrison Mathews":
            playerDict['alternateNames'] += ["Garison Matthew"]
        elif playerDict['fullName'] == "Danuel House":
            playerDict['alternateNames'] += ["Danuel House Jr."]
        elif playerDict['fullName'] == "P.J. Washington":
            playerDict['alternateNames'] += ["P.J. Washington Jr."]
        elif playerDict['fullName'] == "Lonnie Walker":
            playerDict['alternateNames'] += ["Lonnie Walker IV"]
        elif playerDict['fullName'] == "Dennis Smith Jr.":
            playerDict['alternateNames'] += ["Dennis Smith"]
        elif playerDict['fullName'] == 'Wendell Carter Jr.':
            playerDict['alternateNames'] += ['Wendell Carter']
        elif playerDict['fullName'] == 'Marvin Bagley III':
            playerDict['alternateNames'] += ["Marvin Bagley"]
        elif playerDict['fullName'] == 'Moritz Wagner':
            playerDict['alternateNames'] += ["Mo Wagner"]

    with open(ENVIRONMENT.PLAYER_NAME_RELATIONSHIPS_PATH, 'w') as json_file:
        json.dump(activePlayers, json_file, indent=4)

    print('saved player DB Data')

def singlePlayerNameRelationshipRequest(activePlayers, startSeason, urlStub):
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
        universalName = unicodedata.normalize('NFD', playerFullName.replace(".", "")).encode('ascii', 'ignore').decode(
            "utf-8")
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
    return startSeason, activePlayers


# backlogtodo implement binary search
def sortPlayerNameRelationships():
    with open(ENVIRONMENT.PLAYER_NAME_RELATIONSHIPS_PATH) as pNameRelationships:
        pNameList = json.load(pNameRelationships)
    # https://docs.python.org/3/library/bisect.html

    def sortByUniversalName(x):
        return x['universalName']

    pNameList.sort(key=sortByUniversalName)

    with open(ENVIRONMENT.PLAYER_NAME_RELATIONSHIPS_PATH) as writeFile:
        json.dump(pNameList, ENVIRONMENT.PLAYER_NAME_RELATIONSHIPS_PATH)

    print("Sorted player name relationships")

def getAllGameData():
    shortCodes = ENVIRONMENT.CURRENT_TEAMS
    shortCodes.sort()
    nbaTeams = teams.get_teams()
    teamDicts = [team for team in nbaTeams if team['abbreviation'] in shortCodes]

    def extractId(x):
        return x['id']

    teamIds = map(extractId, teamDicts)

    teamGameList = list()
    for id in teamIds:
        sleepChecker()
        gamefinder = leaguegamefinder.LeagueGameFinder(team_id_nullable=id)
        teamGameList.append(gamefinder.get_data_frames()[0])

    basePath = ENVIRONMENT.GAME_SUMMARY_UNFORMATTED_PATH
    for teamDf in teamGameList:
        teamName = teamDf.iloc[0]["TEAM_ABBREVIATION"]
        teamDf.to_csv(basePath.format(teamName))
        print("saved data for", teamName)

    print("extracted the game data")

    return teamIds