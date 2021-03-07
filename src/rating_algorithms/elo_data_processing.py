import json
import ENVIRONMENT
import pandas as pd

from src.database.database_creation import resetPredictionSummaries, createPlayerEloDictionary
from src.historical_data.historical_data_retrieval import getPlayerTeamInSeasonFromBballRefLink
from src.rating_algorithms.algorithms import eloMatchWithRawNums, eloWinProb

from src.rating_algorithms.common_data_processing import preMatchPredictions
# todo refactor equations here to be generic

def runEloForSeason(season: str, seasonCsv: str, playerSkillDictPath: str, winningBetThreshold: float=0.6, startFromBeginning=False):
    df = pd.read_csv(seasonCsv)
    # df = df[df['Home Tipper'].notnull()] # filters invalid rows
    # todo consider adding elo rating per game to files as well
    # df['Home Elo'] = None
    # df['Away Elo'] = None

    winningBets, losingBets = 0

    print('running for season doc', seasonCsv, '\n', '\n')
    colLen = len(df['Game Code'])

    with open(playerSkillDictPath) as jsonFile:
        psd = json.load(jsonFile)

    if startFromBeginning:
        i = 0
    else:
        i = colLen - 1
        lastGameCode = psd['lastGameCode']
        while df.iloc[i]['Game Code'] != lastGameCode:
            i -= 1
        i += 1

    with open(ENVIRONMENT.ELO_PREDICTION_SUMMARIES_PATH) as jsonFile:
        dsd = json.load(jsonFile)

    while i < colLen:
        if df['Home Tipper'].iloc[i] != df['Home Tipper'].iloc[i]:
            i += 1
            continue
        hTip = df['Home Tipper'].iloc[i]
        tWinner = df['Tipoff Winner'].iloc[i]
        aTip = df['Away Tipper'].iloc[i]
        tWinLink = df['Tipoff Winner Link'].iloc[i]
        tLoseLink = df['Tipoff Loser Link'].iloc[i]
        if tWinner == hTip:
            hTipCode = tWinLink[11:]
            aTipCode = tLoseLink[11:]
        elif tWinner == aTip:
            hTipCode = tLoseLink[11:]
            aTipCode = tWinLink[11:]
        else:
            raise ValueError('no match for winner')

        eloBeforeMatchPredictions(season, psd, dsd, hTipCode, aTipCode, tWinLink, df['First Scoring Team'].iloc[i], winningBetThreshold)
        homeElo, awayElo, = eloUpdateDataSingleTipoff(psd, tWinLink, tLoseLink, hTipCode, df['Full Hyperlink'].iloc[i])
        df['Home Mu'].iloc[i] = homeElo
        df['Away Mu'].iloc[i] = awayElo

        i += 1

    psd['lastGameCode'] = df.iloc[-1]['Game Code']

    with open(playerSkillDictPath, 'w') as write_file:
        json.dump(psd, write_file, indent=4)

    with open(ENVIRONMENT.ELO_PREDICTION_SUMMARIES_PATH, 'w') as write_file:
        json.dump(dsd, write_file, indent=4)

    # df.to_csv(str(seasonCsv)[:-4] + '-elo-test.csv')

    return winningBets, losingBets

def eloBeforeMatchPredictions(season, psd, dsd, homePlayerCode, awayPlayerCode, tipWinnerCode, scoringTeam, winningBetThreshold=0.6):
    homeOdds = eloWinProb(homePlayerCode, awayPlayerCode, psd=psd)
    homePlayerTeam = getPlayerTeamInSeasonFromBballRefLink(homePlayerCode, season, longCode=False)['currentTeam']
    awayPlayerTeam = getPlayerTeamInSeasonFromBballRefLink(awayPlayerCode, season, longCode=False)['currentTeam']

    if psd[homePlayerCode]['appearances'] > ENVIRONMENT.MIN_ELO_APPEARANCES and psd[awayPlayerCode]['appearances'] > ENVIRONMENT.MIN_ELO_APPEARANCES:
        preMatchPredictions(awayPlayerCode, awayPlayerTeam, dsd, homeOdds, homePlayerCode, homePlayerTeam, scoringTeam,
                            tipWinnerCode, winningBetThreshold)
    else:
        print('no bet, not enough Data on participants')

def runEloForAllSeasons(seasons, winning_bet_threshold=ENVIRONMENT.TIPOFF_ODDS_THRESHOLD):
    seasonKey = ''
    for season in seasons:
        runEloForSeason(season, ENVIRONMENT.SEASON_CSV_UNFORMATTED_PATH.format(season),
                       ENVIRONMENT.PLAYER_ELO_DICT_PATH, winning_bet_threshold, startFromBeginning=True)
        seasonKey += str(season) + '-'

    with open(ENVIRONMENT.TS_PREDICTION_SUMMARIES_PATH) as predSum:
        dsd = json.load(predSum)

    dsd['seasons'] = seasonKey + 'with-odds-' + str(winning_bet_threshold)

    with open(ENVIRONMENT.TS_PREDICTION_SUMMARIES_PATH, 'w') as predSum:
        json.dump(dsd, predSum, indent=4)

def eloUpdateDataSingleTipoff(psd, winnerCode, loserCode, homePlayerCode, game_code=None):
    if game_code:
        print(game_code)
    winnerCode = winnerCode[11:]
    loserCode = loserCode[11:]

    winnerOgElo = psd[winnerCode]["elo"]
    loserOgElo = psd[loserCode]["elo"]
    winnerElo, loserElo = eloMatchWithRawNums(psd[winnerCode]["elo"], psd[loserCode]['elo'])
    winnerWinCount = psd[winnerCode]["wins"] + 1
    winnerAppearances = psd[winnerCode]["appearances"] + 1
    loserLosses = psd[loserCode]["losses"] + 1
    loserAppearances = psd[loserCode]["appearances"] + 1

    psd[winnerCode]["wins"] = winnerWinCount
    psd[winnerCode]["appearances"] = winnerAppearances
    psd[loserCode]["losses"] = loserLosses
    psd[loserCode]["appearances"] = loserAppearances
    psd[winnerCode]["elo"] = winnerElo
    psd[loserCode]["elo"] = loserElo

    print('Winner:', winnerCode, 'elo increased', winnerElo - winnerOgElo, 'to', winnerElo, '. W:', winnerWinCount, 'L', winnerAppearances - winnerWinCount)
    print('Loser:', loserCode, 'elo decreased', loserElo - loserOgElo, 'to', loserElo, '. W:', loserAppearances - loserLosses, 'L', loserLosses)

    if homePlayerCode == winnerCode:
        homeElo = winnerOgElo
        awayElo = loserOgElo
    elif homePlayerCode == loserCode:
        homeElo = loserOgElo
        awayElo = winnerOgElo

    return homeElo, awayElo

def calculateEloDictionaryFromZero():
    resetPredictionSummaries(ENVIRONMENT.TS_PREDICTION_SUMMARIES_PATH) # reset sums
    createPlayerEloDictionary() # clears the stored values,
    runEloForAllSeasons(ENVIRONMENT.SEASONS_LIST, winning_bet_threshold=ENVIRONMENT.TIPOFF_ODDS_THRESHOLD)
    print("\n", "elo dictionary updated for seasons", ENVIRONMENT.SEASONS_LIST, "\n")

def updateEloDictionaryFromLastGame():
    runEloForSeason(ENVIRONMENT.CURRENT_SEASON, ENVIRONMENT.CURRENT_SEASON_CSV, ENVIRONMENT.PLAYER_ELO_DICT_PATH, winningBetThreshold=0.6, startFromBeginning=False)
    print("\n", "elo dictionary updated from last game", "\n")
