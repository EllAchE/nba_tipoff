import glob
import json

import pandas as pd

import ENVIRONMENT
from src.database.database_access import getUniversalTeamShortCode
from src.odds.odds_calculator import returnGreaterOdds, decimalToAmerican, americanToDecimal
from src.utils import getDashDateAndHomeCodeFromGameCode


def decodePickle(fileName):
    with open(fileName) as pickleFile:
        oddsList = json.load(pickleFile)
    return oddsList

def parseDetailsFromOddsObj(oddsDict):
    homeOdds = None
    try:
        homeOdds = oddsDict['bestHomeOdds']
        awayOdds = oddsDict['bestAwayOdds']
    except:
        pass

    if homeOdds is None:
        print('errored on', oddsDict['fetchedDatetime'],  oddsDict['home'], 'vs.', oddsDict['away'])
        return None, None

    home = getUniversalTeamShortCode(oddsDict['home'])
    away = getUniversalTeamShortCode(oddsDict['away'])
    details = {
        "home": home,
        "away": away,
        "bestHomeOdds": homeOdds,
        "bestAwayOdds": awayOdds,
        "exchange": oddsDict['exchange']
    }
    print('ran for', oddsDict['fetchedDatetime'],  home, 'vs.', away)
    return details
    # alternate names: homeTeamFirstQuarterOdds, awayTeamSecondQuarterOdds

def splitFileName(fileName):
    res1 = fileName.split('/')
    res = res1[-1].split('_')
    date = res[0]
    time = res[1].split('.')[0]
    return date, time

def savePickledOdds(path):
    pickledOdds = retrievePickledOdds()
    with open(path, 'w') as fff:
        json.dump(pickledOdds, fff, indent=4)
    print('saved pickled odds')

def retrievePickledOdds():
    fNames = [i for i in glob.glob('{}/**'.format(ENVIRONMENT.ODDS_DATA_FOLDER))]
    allOddsDict = {}

    for fName in fNames:
        date, time = splitFileName(fName)
        if date not in allOddsDict.keys():
            allOddsDict[date] = {}

        unpickledObjDictList = decodePickle(fName)
        for objDict in unpickledObjDictList:
            try:
                isMultiQuarter = objDict['isFullGame']
            except:
                isMultiQuarter = False
            if isMultiQuarter and objDict['quarter'] == 'QUARTER_1':
                unpickledObjDictList.append(objDict['secondQuarterGameObj'])
                unpickledObjDictList.append(objDict['thirdQuarterGameObj'])
                unpickledObjDictList.append(objDict['fourthQuarterGameObj'])
        allOddsDict[date][time] = {}

        teamSet = set()
        for objDict in unpickledObjDictList:
            dtl = parseDetailsFromOddsObj(objDict)
            exclusionList = ['betfair', 'unibet', 'bovada', 'barstool', 'pointsBet']

            if dtl['exchange'] is None or dtl['exchange'] in exclusionList:
                continue

            if dtl['home'] not in teamSet:
                teamSet.add(dtl['home'])
                allOddsDict[date][time][dtl['home']] = {}
                allOddsDict[date][time][dtl['home']]['QUARTER_1'] = {}
                allOddsDict[date][time][dtl['home']]['QUARTER_2'] = {}
                allOddsDict[date][time][dtl['home']]['QUARTER_3'] = {}
                allOddsDict[date][time][dtl['home']]['QUARTER_4'] = {}
            if dtl['away'] not in teamSet:
                teamSet.add(dtl['away'])
                allOddsDict[date][time][dtl['away']] = {}
                allOddsDict[date][time][dtl['away']]['QUARTER_1'] = {}
                allOddsDict[date][time][dtl['away']]['QUARTER_2'] = {}
                allOddsDict[date][time][dtl['away']]['QUARTER_3'] = {}
                allOddsDict[date][time][dtl['away']]['QUARTER_4'] = {}

            try:
                quarter = objDict['quarter']
            except:
                quarter = 'QUARTER_1'

            allOddsDict[date][time][dtl['home']][quarter][dtl['exchange']] = dtl['bestHomeOdds']
            allOddsDict[date][time][dtl['away']][quarter][dtl['exchange']] = dtl['bestAwayOdds']

    for dateKey in allOddsDict.keys(): # remove emptys
        delList = []
        for timeKey in allOddsDict[dateKey].keys():
            if len(allOddsDict[dateKey][timeKey].keys()) == 0:
                delList.append(timeKey)
        for key in delList:
            del allOddsDict[dateKey][key]

    for dateKey in allOddsDict.keys(): # remove more emptys
        for timeKey in allOddsDict[dateKey].keys():
            for teamKey in allOddsDict[dateKey][timeKey].keys():
                dellist = []
                for quarterKey in allOddsDict[dateKey][timeKey][teamKey].keys():
                    if len(allOddsDict[dateKey][timeKey][teamKey][quarterKey].keys()) == 0:
                        dellist.append(quarterKey)
                for delKey in dellist:
                    del allOddsDict[dateKey][timeKey][teamKey][delKey]

    return allOddsDict

# def addAdditionalQuarterScoreResultsToSeasonCsv():
#     # with open(ENVIRONMENT.FIRST_POINT_DATA_RAW_2021) as gamePbpF:
#     #     gamePbpDict = json.load(gamePbpF)
#     seasonCsvDf = pd.read_csv(ENVIRONMENT.SEASON_CSV_UNFORMATTED_PATH.format(2021))
#
#     seasonCsvDf['First Scorer Q2'] = seasonCsvDf['First Scorer Q3'] = seasonCsvDf['First Scorer Q4'] = None
#
#     for game in gamePbpDict:


def generateBaseBacktestCsv(savePath):
    # with open(ENVIRONMENT.FIRST_POINT_DATA_RAW_2021) as gamePbpF:
    #     gamePbpDict = json.load(gamePbpF)
    odds = retrievePickledOdds()
    seasonCsvDf = pd.read_csv(ENVIRONMENT.SEASON_CSV_UNFORMATTED_PATH.format(2021))
    seasonCsvDf['fanduelHomeOdds'] = seasonCsvDf['draftkingsHomeOdds'] = seasonCsvDf['mgmHomeOdds'] = None
    seasonCsvDf['fanduelAwayOdds'] = seasonCsvDf['draftkingsAwayOdds'] = None
    seasonCsvDf['mgmAwayOdds'] = seasonCsvDf['bestHomeOdds'] = seasonCsvDf['bestAwayOdds'] = None
    for i in seasonCsvDf.index:
        date, teamCode = getDashDateAndHomeCodeFromGameCode(seasonCsvDf.iloc[i]['Game Code'])
        row = seasonCsvDf.iloc[i]
        home = row['Home Short']
        away = row['Away Short']
        try:
            dateDict = odds[date]
            dayOdds = extractFirstInstanceOfOddsFromSingleDayDict(dateDict)
            for teamKey in dayOdds.keys():
                for exchangeBetKey in dayOdds[teamKey]['QUARTER_1'].keys(): # todo hack for quarter 1 for now
                    if getUniversalTeamShortCode(teamKey) == getUniversalTeamShortCode(home):
                        strAdd = exchangeBetKey + 'HomeOdds'
                        seasonCsvDf.at[i, strAdd] = dayOdds[teamKey]['QUARTER_1'][exchangeBetKey]
                    elif getUniversalTeamShortCode(teamKey) == getUniversalTeamShortCode(away):
                        strAdd = exchangeBetKey + 'AwayOdds'
                        seasonCsvDf.at[i, strAdd] = dayOdds[teamKey]['QUARTER_1'][exchangeBetKey]

        except:
            print('possibly no odds for game', teamCode, date)
    for i in seasonCsvDf.index:
        try:
            homeOddsList = list()
            awayOddsList = list()
            row = seasonCsvDf.iloc[i]
            a = row['fanduelHomeOdds']
            b = row['draftkingsHomeOdds']
            c = row['mgmHomeOdds']
            d = row['fanduelAwayOdds']
            e = row['draftkingsAwayOdds']
            f = row['mgmAwayOdds']

            for odds in [a,b,c]:
                if odds is not None:
                    homeOddsList.append(odds)
            for odds in [d, e, f]:
                if odds is not None:
                    awayOddsList.append(odds)

            bestHomeOdds = bestAwayOdds = None
            if len(homeOddsList) > 0:
                bestHomeOdds = decimalToAmerican(max(map(americanToDecimal, homeOddsList)))
            if len(awayOddsList) > 0:
                bestAwayOdds = decimalToAmerican(max(map(americanToDecimal, awayOddsList)))
            seasonCsvDf.at[i, 'bestHomeOdds'] = bestHomeOdds
            seasonCsvDf.at[i, 'bestAwayOdds'] = bestAwayOdds
        except:
            print('possibly no odds for game', teamCode, date)

    saveDf = seasonCsvDf[['Game Code', 'Home Short', 'Away Short', 'Home Tipper', 'Away Tipper', 'Tip Winning Team', 'Tip Losing Team',
                          'First Scoring Team', 'Scored Upon Team', 'Tip Winner Scores', 'Home TS Mu', 'Away TS Mu', 'Home TS Sigma',
                          'Away TS Sigma', 'fanduelHomeOdds', 'draftkingsHomeOdds', 'mgmHomeOdds', 'bestHomeOdds',
                          'fanduelAwayOdds', 'draftkingsAwayOdds', 'mgmAwayOdds', 'bestAwayOdds']]

    saveDf.to_csv(savePath, index=False)

def extractFirstInstanceOfOddsFromSingleDayDict(dateDict):
    comboSet = set()
    teamSet = set()
    firstInstanceOddsDict = {}

    for time in dateDict.keys():
        for team in dateDict[time].keys():
            if team not in teamSet:
                teamSet.add(team)
                firstInstanceOddsDict[team] = {}

            for quarter in dateDict[time][team].keys():
                if quarter not in firstInstanceOddsDict[team].keys():
                    firstInstanceOddsDict[team][quarter] = {}

                for exchange in dateDict[time][team][quarter].keys():
                    if team + quarter + exchange in comboSet:
                        continue
                    else:
                        comboSet.add(team + quarter + exchange)
                        firstInstanceOddsDict[team][quarter][exchange] = dateDict[time][team][quarter][exchange]

    return firstInstanceOddsDict

