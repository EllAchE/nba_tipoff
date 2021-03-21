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

def _createPlayerDictionary(path, playerDetailsFunction):
    with open(ENVIRONMENT.PLAYER_TEAM_PAIRS_PATH) as playerTeamPairsJson:
        ptp = json.load(playerTeamPairsJson)

        playerCodes = set()
        playerSkillDict = {}

        for season in ptp.keys():
            for player in ptp[season].keys():
                playerCodes.add(player)

        playerSkillDictPopulated = playerDetailsFunction(playerCodes, playerSkillDict)

    with open(path, 'w') as psd:
        json.dump(playerSkillDictPopulated, psd, indent=4)

def createPlayerEloDictionary():
    _createPlayerDictionary(ENVIRONMENT.PLAYER_ELO_DICT_PATH, _eloPlayerDetailsFunction)

def createPlayerGlickoDictionary():
    _createPlayerDictionary(ENVIRONMENT.PLAYER_GLICKO_DICT_PATH, _glickoPlayerDetailsFunction)

def createPlayerTrueSkillDictionary():
    _createPlayerDictionary(ENVIRONMENT.PLAYER_TRUESKILL_DICT_PATH, _trueSkillPlayerDetailsFunction)

def _eloPlayerDetailsFunction(playerCodes, playerSkillDict):
    for code in playerCodes:
        playerSkillDict[code] = {'elo': ENVIRONMENT.BASE_ELO, 'appearances': 0, 'wins': 0, 'losses': 0, 'predicted wins': 0, 'predicted losses': 0}
    return playerSkillDict

def _glickoPlayerDetailsFunction(playerCodes, playerSkillDict):
    for code in playerCodes:
        playerSkillDict[code] = {'mu': ENVIRONMENT.BASE_GLICKO_MU, 'sigma': ENVIRONMENT.BASE_GLICKO_SIGMA, 'phi': ENVIRONMENT.BASE_GLICKO_PHI, 'appearances': 0, 'wins': 0, 'losses': 0, 'predicted wins': 0, 'predicted losses': 0}
    return playerSkillDict

def _trueSkillPlayerDetailsFunction(playerCodes, playerSkillDict):
    for code in playerCodes:
        playerSkillDict[code] = {'mu': ENVIRONMENT.BASE_TS_MU, 'sigma': ENVIRONMENT.BASE_TS_SIGMA, 'appearances': 0, 'wins': 0, 'losses': 0, 'predicted wins': 0, 'predicted losses': 0}
    return playerSkillDict

def saveActivePlayersTeams(start_season: int):
    # https://www.basketball-reference.com/leagues/NBA_2021_per_game.html
    seasonsList = list()
    while start_season < 2022:
        seasonsList.append(str(start_season))
        start_season += 1

    for season in seasonsList:
        _singleSeasonPlayerTeamPairs(season)
    print('saved seasons Data')

def _singleSeasonPlayerTeamPairs(season):
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
        playerUniversalName = getUniversalPlayerName(playerNameTag.contents[0].contents[0])

        tag = str(tag)
        playerCode = re.search(r'(?<=\"/players/./)(.*?)(?=\")', tag).group(0)
        playerTeam = re.search(r'(?<=<a href="/teams/)(.*?)(?=/)', tag).group(0)
        if playerCode in noTradeSet:
            seasons[season][playerUniversalName]['currentTeam'] = seasons[season][playerCode]['currentTeam'] = playerTeam
            seasons[season][playerUniversalName]['possibleTeams'] += [playerTeam]
            seasons[season][playerCode]['possibleTeams'] += [playerTeam]
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
        seasons[season][playerUniversalName] = seasons[season][playerCode] = {'possibleTeams': [playerTeam]}
        seasons[season][playerUniversalName]['currentTeam'] = seasons[season][playerCode]['currentTeam'] = playerTeam

    with open(ENVIRONMENT.PLAYER_TEAM_PAIRS_PATH, 'w') as json_file:
        json.dump(seasons, json_file, indent=4)

# backlogtodo find a faster way to replace messed up player names
# backlogtodo edit the methods inside here to use append (i.e. don't overwrite each time, just start from the end)
def createPlayerNameRelationship(startSeason: int=1998):
    activePlayers = []
    addedPlayerSet = set()

    while startSeason < 2022:
        activePlayers, addedPlayerSet = singlePlayerNameRelationshipRequest(activePlayers, startSeason, addedPlayerSet)
        startSeason += 1

    activePlayers = _misformattedNameAdjustment(activePlayers)

    with open(ENVIRONMENT.PLAYER_NAME_RELATIONSHIPS_PATH, 'w') as json_file:
        json.dump(activePlayers, json_file, indent=4)
    print('saved player DB Data')

def _misformattedNameAdjustment(activePlayers):
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
        elif playerDict['fullName'] == 'Brad Wanamaker':
            playerDict['alternateNames'] += ["Bradley Wanamaker"]
        elif playerDict['fullName'] == 'Juan Toscano-Anderson':
            playerDict['alternateNames'] += ['Juan Anderson']
        elif playerDict['fullName'] == "Isaac Austin":
            playerDict['alternateNames'] += ["Ike Austin"]
        elif playerDict['universalName'] == "omerask":
            playerDict['alternateNames'] += ['OMer Asik']
        elif playerDict['fullName'] == "Danny Schayes":
            playerDict['alternateNames'] += ["Dan Schayes"]
        elif playerDict['fullName'] == "Mike Sweetney":
            playerDict['alternateNames'] += ["Michael Sweetney"]
        elif playerDict['fullName'] == "Larry Nance Jnr":
            playerDict['alternateNames'] += ["Larry Nance"]
            playerDict['alternateNames'] += ["Larry Nance Jr."]
        elif playerDict['fullName'] == "Larry Nance Jr.":
            playerDict['alternateNames'] += ["Larry Nance"]
            playerDict['alternateNames'] += ["Larry Nance Jnr"]
    return activePlayers

def singlePlayerNameRelationshipRequest(activePlayers, startSeason, addedPlayerSet):
    url = 'https://www.basketball-reference.com/leagues/NBA_{}_per_game.html'.format(str(startSeason))
    soup, statusCode = getSoupFromUrl(url, returnStatus=True)
    print("GET request for", startSeason, "players list returned status", statusCode)

    allPlayerTags = soup.find_all('tr', class_="full_table")
    for tag in allPlayerTags:
        tagStr = str(tag)
        playerNameTag = tag.select('td[data-stat="player"]')[0]
        playerFullName = playerNameTag.contents[0].contents[0]
        playerCode = re.search(r'(?<=\"/players/./)(.*?)(?=\")', tagStr).group(0)
        if playerCode in addedPlayerSet:
            continue
        else:
            addedPlayerSet.add(playerCode)

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
        })
    return activePlayers, addedPlayerSet


# backlogtodo implement binary search
# https://docs.python.org/3/library/bisect.html
def sortPlayerNameRelationships():
    with open(ENVIRONMENT.PLAYER_NAME_RELATIONSHIPS_PATH) as pNameRelationships:
        pNameList = json.load(pNameRelationships)

    def sortByUniversalName(x):
        return x['universalName']

    pNameList.sort(key=sortByUniversalName)

    with open(ENVIRONMENT.PLAYER_NAME_RELATIONSHIPS_PATH) as writeFile:
        json.dump(pNameList, writeFile)

    print("Sorted player name relationships")

def getAllGameData():
    shortCodes = ENVIRONMENT.CURRENT_TEAMS.sort()
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

    for teamDf in teamGameList:
        teamName = teamDf.iloc[0]["TEAM_ABBREVIATION"]
        teamDf.to_csv(ENVIRONMENT.GAME_SUMMARY_UNFORMATTED_PATH.format(teamName))
        print("saved data for", teamName)

    print("extracted game data for all teams", nbaTeams)

    return teamIds

def addExtraUrlToPlayerLinks():
    for season in [2008, 2009]:
        df = pd.read_csv(ENVIRONMENT.SEASON_CSV_UNFORMATTED_PATH.format(season))
        for i in range(0, len(df['Game Code']) - 1):
            temp = df['Tip Winner Link'].iloc[i]
            if "/players/" not in temp:
                df.at[i, 'Tip Winner Link'] = "/players/" + temp[0] + "/" + temp
                temp2 = df['Tip Loser Link'].iloc[i]
                df.at[i, 'Tip Loser Link'] = "/players/" + temp2[0] + "/" + temp2

        df.to_csv(ENVIRONMENT.SEASON_CSV_UNFORMATTED_PATH.format(season), index=False)

def addSeasonLongData():
    # off eff
    # def eff
    # FT percent
    # 2pt per
    # 3pt per
    # TO Rate
    # Naive Q1 rating
    pass

def addIncrementalData():
    # gamesPlayed -x
    # Tipper Lifetime Appearances
    # Elo - x
    # Glicko - x
    # Trueskill - x
    # current naive Q1 rating
    # Tip Wins
    # Tip Losses
    # Mid season naive Q1 rating
    pass


def addGamesPlayed(df):
    teamSet = set()
    teamDict = {}
    df["Home Games Played"] = df["Away Games Played"] = 0
    for i in range(0, len(df.index) - 1):
        row = df.iloc[i]
        home = row['Home']
        away = row['Away']
        if home not in teamSet:
            teamSet.add(home)
            teamDict[home] = 0
        if away not in teamSet:
            teamSet.add(away)
            teamDict[away] = 0

        teamDict[home] += 1
        teamDict[away] += 1
        df.at[i, "Home Games Played"] = teamDict[home]
        df.at[i, "Away Games Played"] = teamDict[away]

def addResult():
    pass

def addAdditionalMlColumnsSingleSeason(season):
    df = pd.read_csv(ENVIRONMENT.SEASON_CSV_UNFORMATTED_PATH.format(season))
    for i in range(0, len(df.index) - 1):
        row = df.iloc[i]

#
# def removeExtraIndex():
#     for season in ENVIRONMENT.ALL_SEASONS_LIST:
#         df = pd.read_csv(ENVIRONMENT.SEASON_CSV_UNFORMATTED_PATH.format(season), index_col=0)
#         df.to_csv(ENVIRONMENT.SEASON_CSV_UNFORMATTED_PATH.format(season), index=False)
#         # df2 = pd.read_csv(ENVIRONMENT.SEASON_CSV_UNFORMATTED_PATH.format(season), index_col=0)
#         # df2.to_csv(ENVIRONMENT.SEASON_CSV_UNFORMATTED_PATH.format(season), index=False)

