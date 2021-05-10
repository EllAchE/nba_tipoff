import glob
import json

import pandas as pd

import ENVIRONMENT

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

    details = {
        "home": oddsDict['home'],
        "away": oddsDict['away'],
        "bestHomeOdds": homeOdds,
        "bestAwayOdds": awayOdds
    }
    print('ran for', oddsDict['fetchedDatetime'],  oddsDict['home'], 'vs.', oddsDict['away'])
    return oddsDict['exchange'], details
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
        json.dump(pickledOdds, fff)
    print('saved pickled odds')

def retrievePickledOdds():
    fNames = [i for i in glob.glob('{}/**'.format(ENVIRONMENT.ODDS_DATA_FOLDER))]
    allOddsDict = {}
    dateSet = set()

    for fName in fNames:
        date, time = splitFileName(fName)
        if date not in dateSet:
            allOddsDict[date] = {}
            dateSet.add(date)

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

        exchangeSet = set()
        for objDict in unpickledObjDictList:
            exchange, details = parseDetailsFromOddsObj(objDict)
            exclusionList = ['betfair', 'unibet', 'bovada', 'barstool']
            if exchange is None or exchange in exclusionList:
                continue
            if exchange not in exchangeSet:
                exchangeSet.add(exchange)
                allOddsDict[date][time][exchange] = {}
            try:
                quarter = objDict['quarter']
            except:
                quarter = 'QUARTER_1'
            allOddsDict[date][time][exchange][quarter] = details

    return allOddsDict

# def addAdditionalQuarterScoreResultsToSeasonCsv():
#     # with open(ENVIRONMENT.FIRST_POINT_DATA_RAW_2021) as gamePbpF:
#     #     gamePbpDict = json.load(gamePbpF)
#     seasonCsvDf = pd.read_csv(ENVIRONMENT.SEASON_CSV_UNFORMATTED_PATH.format(2021))
#
#     seasonCsvDf['First Scorer Q2'] = seasonCsvDf['First Scorer Q3'] = seasonCsvDf['First Scorer Q4'] = None
#
#     for game in gamePbpDict:



def generateBaseBacktestCsv():
    # with open(ENVIRONMENT.FIRST_POINT_DATA_RAW_2021) as gamePbpF:
    #     gamePbpDict = json.load(gamePbpF)
    odds = retrievePickledOdds()
    seasonCsvDf = pd.read_csv(ENVIRONMENT.SEASON_CSV_UNFORMATTED_PATH.format(2021))

