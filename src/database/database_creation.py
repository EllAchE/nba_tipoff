import glob
import json
import unicodedata
import pandas as pd
import re

from nba_api.stats.endpoints import leaguegamefinder, TeamEstimatedMetrics, teamestimatedmetrics, LeagueDashTeamPtShot, \
    TeamDashboardByGameSplits
from nba_api.stats.static import teams

import ENVIRONMENT
from src.database.database_access import getUniversalPlayerName, getUniversalTeamShortCode
from src.rating_algorithms.algorithms import glickoTipWinProb, eloTipWinProb, trueSkillTipWinProb, \
    trueSkillTipWinFromMuAndSigma, eloWinProbFromRawElo, glickoWinProbFromMuPhiSigma
from src.utils import getSoupFromUrl, removeAllNonLettersAndLowercase, sleepChecker, customNbaSeasonFormatting


def concatCsv(savePath: str, readFolder: str):
    fNames = [i for i in glob.glob('{}/*.csv'.format(readFolder))]
    concattedCsv = pd.concat([pd.read_csv(f) for f in fNames])
    concattedCsv.to_csv(savePath, index=False, encoding='utf-8-sig')

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
        elif playerDict['fullName'] == "Aleksej Polusevski":
            playerDict['alternateNames'] += ['Pokuševski, Aleksej']
        elif playerDict['fullName'] == "Larry Nance Jnr":
            playerDict['alternateNames'] += ["Larry Nance"]
            playerDict['alternateNames'] += ["Larry Nance Jr."]
        elif playerDict['fullName'] == "Larry Nance Jr.":
            playerDict['alternateNames'] += ["Larry Nance"]
            playerDict['alternateNames'] += ["Larry Nance Jnr"]
        elif playerDict['fullName'] == "Svi Mykhailiuk":
            playerDict['alternateNames'] += ['Sviatoslav Mykhailiuk']
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
    shortCodes = ENVIRONMENT.CURRENT_TEAMS
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
        teamDf.to_csv(ENVIRONMENT.GAME_SUMMARY_UNFORMATTED_PATH.format(teamName), index=False)
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

def saveNbaApiDataframeAsJson(data, path):
    result = data.to_json(orient="index")
    parsed = json.loads(result)
    newDict = {}
    for key in parsed.keys():
        obj = parsed[key]
        name = obj["TEAM_NAME"]
        newDict[getUniversalTeamShortCode(name)] = parsed[key]
    with open(path, 'w') as wFile:
        json.dump(newDict, wFile, indent=4)

def getShotBreakdownForTeams(season): # season must be in 2014-15 format
    # shot pt https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/endpoints/leaguedashteamptshot.md
    # percentages https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/endpoints/teamyearbyyearstats.md
    data = LeagueDashTeamPtShot(season=season).get_data_frames()[0]
    path = ENVIRONMENT.SHOT_BREAKDOWN_TEAMS_UNFORMATTED.format(season)
    saveNbaApiDataframeAsJson(data, path)

def getPlusMinusForTeams(season):
    seasonStr = customNbaSeasonFormatting(season)
    teamPlusMinusDict = {}
    with open(ENVIRONMENT.TEAM_NAMES_PATH) as teamsFiles:
        teamData = json.load(teamsFiles)
    for team in teamData:
        data = TeamDashboardByGameSplits(team_id=team["teamId"], season=seasonStr).get_data_frames()[2]
        print('running for team', team['abbreviation'])
        sleepChecker(1, 10, 1)
        teamPlusMinusDict[team['abbreviation']] = {}
        teamPlusMinusDict[team['abbreviation']]['quarter1'] = data['PLUS_MINUS'][0]
        teamPlusMinusDict[team['abbreviation']]['quarter2'] = data['PLUS_MINUS'][1]
        teamPlusMinusDict[team['abbreviation']]['quarter3'] = data['PLUS_MINUS'][2]
        teamPlusMinusDict[team['abbreviation']]['quarter4'] = data['PLUS_MINUS'][3]

    with open(ENVIRONMENT.PLUS_MINUS_TEAMS_UNFORMATTED.format(season), 'w') as saveFile:
        json.dump(teamPlusMinusDict, saveFile)
    print('saved plus minus data')


def getAdvancedMetricsForTeams(season):
    # all https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/endpoints/teamdashboardbyteamperformance.md
    # data split out by things like all star break etc. https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/endpoints/teamdashboardbygeneralsplits.md
    # advanced i.e. TOV PCT https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/endpoints/teamestimatedmetrics.md
    data = TeamEstimatedMetrics(season=season).get_data_frames()[0]
    path = ENVIRONMENT.ADVANCED_TEAMS_METRICS_UNFORMATTED.format(season)
    saveNbaApiDataframeAsJson(data, path)

def addSeasonLongData(df, season):
    # off eff - x
    # def eff - x
    # FT percent - x
    # 2pt per - x
    # 3pt per - x
    # TO Rate - x
    # Naive Q1 rating - x
    seasonNbaComFormat = str(season) + '-' + str((season + 1) % 100)
    with open(ENVIRONMENT.ADVANCED_TEAMS_METRICS_UNFORMATTED.format(seasonNbaComFormat)) as rFile:
        advancedMetrics = json.load(rFile)
    with open(ENVIRONMENT.SHOT_BREAKDOWN_TEAMS_UNFORMATTED.format(seasonNbaComFormat)) as rFile:
        shotBreakdown = json.load(rFile)

    advancedMetricsKeyList = ['W_PCT', 'E_OFF_RATING', 'E_DEF_RATING', 'E_OREB_PCT', 'E_DREB_PCT', 'E_REB_PCT', 'E_TM_TOV_PCT', 'W_PCT_RANK', 'E_OFF_RATING_RANK',
                              'E_DEF_RATING_RANK', 'E_OREB_PCT_RANK', 'E_REB_PCT_RANK', 'E_TM_TOV_PCT']
    shotBreakdownKeyList = ['FG_PCT', 'FG2_PCT', 'FG3_PCT', 'FG2A_FREQUENCY', 'FG3A_FREQUENCY']
    for item in advancedMetricsKeyList:
        df["HOME_" + str(item)] = None
        df["AWAY_" + str(item)] = None
    for i in range(0, len(df.index)):
        row = df.iloc[i]
        home = getUniversalTeamShortCode(row['Home Short'])
        away = getUniversalTeamShortCode(row['Away Short'])

        for item in advancedMetricsKeyList:
            homeKey = "HOME_" + item
            awayKey = "AWAY_" + item
            df.at[i, homeKey] = advancedMetrics[home][item]
            df.at[i, awayKey] = advancedMetrics[away][item]
        for item in shotBreakdownKeyList:
            homeKey = "HOME_" + item
            awayKey = "AWAY_" + item
            df.at[i, homeKey] = shotBreakdown[home][item]
            df.at[i, awayKey] = shotBreakdown[away][item]
    return df

def addGamesPlayedAndNaiveAdjustment(df): # Games Played, naive adjustment
    teamSet = set()
    teamDict = {}
    df["Home Games Played"] = df["Away Games Played"] = df["Cur_H_N_Adj"] = df["Cur_A_N_Adj"] = df["Home Scores"] \
        = df["Mid_H_N_Adj"] = df["Mid_A_N_Adj"] = df["Full_H_N_Adj"] = df["Full_A_N_Adj"] = None
    for i in range(0, len(df.index)):
        row = df.iloc[i]
        home = getUniversalTeamShortCode(row['Home Short'])
        away = getUniversalTeamShortCode(row['Away Short'])
        homeScores = True if row['First Scoring Team'] == getUniversalTeamShortCode(row['Home']) else False
        df.at[i, "Home Scores"] = homeScores
        if home not in teamSet:
            teamSet.add(home)
            teamDict[home] = {}
            teamDict[home]["gp"] = 0
            teamDict[home]['expectedScores'] = teamDict[home]['actualScores'] = 0
            teamDict[home]['midSeasonAdjFactor'] = None
        if away not in teamSet:
            teamSet.add(away)
            teamDict[away] = {}
            teamDict[away]["gp"] = 0
            teamDict[away]['expectedScores'] = teamDict[away]['actualScores'] = 0
            teamDict[away]['midSeasonAdjFactor'] = None

        teamDict[home]['gp'] += 1
        teamDict[away]['gp'] += 1
        df.at[i, "Home Games Played"] = teamDict[home]['gp']
        df.at[i, "Away Games Played"] = teamDict[away]['gp']

        teamDict[home]['expectedScores'] += ENVIRONMENT.TIP_WINNER_SCORE_ODDS if row['Tip Winning Team'] == home else (1-ENVIRONMENT.TIP_WINNER_SCORE_ODDS)
        teamDict[away]['expectedScores'] += ENVIRONMENT.TIP_WINNER_SCORE_ODDS if row['Tip Winning Team'] == away else (1-ENVIRONMENT.TIP_WINNER_SCORE_ODDS)
        teamDict[home]['actualScores'] += True if row['First Scoring Team'] == home else False
        teamDict[away]['actualScores'] += True if row['First Scoring Team'] == away else False
        df.at[i, "Cur_H_N_Adj"] = teamDict[home]['actualScores'] / teamDict[home]['expectedScores']
        df.at[i, "Cur_A_N_Adj"] = teamDict[away]['actualScores'] / teamDict[away]['expectedScores']

        if teamDict[home]['gp'] == 40:
            teamDict[home]['midSeasonAdjFactor'] = teamDict[home]['actualScores'] / teamDict[home]['expectedScores']
        if teamDict[away]['gp'] == 40:
            teamDict[away]['midSeasonAdjFactor'] = teamDict[away]['actualScores'] / teamDict[away]['expectedScores']

    for i in range(0, len(df.index) - 1):
        df.at[i, "Mid_H_N_Adj"] = teamDict[getUniversalTeamShortCode(df.iloc[i]["Home"])]['midSeasonAdjFactor']
        df.at[i, "Mid_A_N_Adj"] = teamDict[getUniversalTeamShortCode(df.iloc[i]["Away"])]['midSeasonAdjFactor']
        df.at[i, "Full_H_N_Adj"] = teamDict[getUniversalTeamShortCode(df.iloc[i]["Home"])]['actualScores'] / teamDict[getUniversalTeamShortCode(df.iloc[i]["Home"])]['expectedScores']
        df.at[i, "Full_A_N_Adj"] = teamDict[getUniversalTeamShortCode(df.iloc[i]["Away"])]['actualScores'] / teamDict[getUniversalTeamShortCode(df.iloc[i]["Away"])]['expectedScores']
        # backlogtodo this is going to bias playoff teams downwards as they'll play other good teams (though not too significantly)
    return df

# def missing stuff(): # this happens in the predictions runner
    # gamesPlayed - x
    # Tipper Lifetime Appearances - x
    # Elo - x
    # Glicko - x
    # Trueskill - x
    # current naive Q1 rating - x
    # Tip Wins - x
    # Tip Losses - x
    # Mid season naive Q1 rating - x
def addAdditionalMlColumnsSingleSeason(season):
    df = pd.read_csv(ENVIRONMENT.SEASON_CSV_UNFORMATTED_PATH.format(season))

    df = addGamesPlayedAndNaiveAdjustment(df)
    df = addSeasonLongData(df, season)
    df = columnSummaryValuesAddedToMl(df)
    numberBack = (season % 100) + 1
    seasonTitle = str(season) + "-" + str(numberBack)

    df.to_csv(ENVIRONMENT.SEASON_CSV_ML_COLS_UNFORMATTED_PATH.format(seasonTitle), index=False)
    print('ml columns added to dataset for season', season)

def columnSummaryValuesAddedToMl(df):
    df['Elo Difference'] = df['Home Elo'] - df['Away Elo']
    df['TrueSkill Difference'] = df['Home TS Mu'] - df['Away TS Mu']
    df['Glicko Difference'] = df['Home Glicko Mu'] - df['Away Glicko Mu']
    df['Combined_Cur_N_Adj'] = df['Combined_Mid_N_Adj'] = df['Combined_Full_N_Adj'] = None

    for i in range(0, len(df.index)):
        df.at[i, "Elo Tip Win Prob"] = eloWinProbFromRawElo(df['Home Elo'].iloc[i], df['Away Elo'].iloc[i])
        df.at[i, "Glicko Tip Win Prob"] = glickoWinProbFromMuPhiSigma(df['Home Glicko Mu'].iloc[i], df['Home Glicko Phi'].iloc[i], df['Home Glicko Sigma'].iloc[i], df['Away Glicko Mu'].iloc[i], df['Away Glicko Phi'].iloc[i], df['Away Glicko Sigma'].iloc[i])
        df.at[i, "TrueSkill Tip Win Prob"] = trueSkillTipWinFromMuAndSigma(df['Home TS Mu'].iloc[i], df['Home TS Sigma'].iloc[i], df['Away TS Mu'].iloc[i], df['Away TS Sigma'].iloc[i])
        df.at[i, 'Combined_Cur_N_Adj'] = df['Cur_H_N_Adj'].iloc[i] / df['Cur_A_N_Adj'].iloc[i] if df['Cur_A_N_Adj'].iloc[i] != 0 and df['Cur_A_N_Adj'].iloc[i] is not None else 0
        df.at[i, 'Combined_Mid_N_Adj'] = df['Mid_H_N_Adj'].iloc[i] / df['Mid_A_N_Adj'].iloc[i] if df['Mid_A_N_Adj'].iloc[i] != 0 and df['Mid_A_N_Adj'].iloc[i] is not None else 0
        df.at[i, 'Combined_Full_N_Adj'] = df['Full_H_N_Adj'].iloc[i] / df['Full_A_N_Adj'].iloc[i] if df['Full_A_N_Adj'].iloc[i] != 0 and df['Full_A_N_Adj'].iloc[i] is not None else 0

    return df

# def removeExtraIndex():
#     for season in ENVIRONMENT.ALL_SEASONS_LIST:
#         df = pd.read_csv(ENVIRONMENT.SEASON_CSV_UNFORMATTED_PATH.format(season), index_col=0)
#         df.to_csv(ENVIRONMENT.SEASON_CSV_UNFORMATTED_PATH.format(season), index=False)
#         # df2 = pd.read_csv(ENVIRONMENT.SEASON_CSV_UNFORMATTED_PATH.format(season), index_col=0)
#         # df2.to_csv(ENVIRONMENT.SEASON_CSV_UNFORMATTED_PATH.format(season), index=False)

