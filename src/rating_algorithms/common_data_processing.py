from src.database.database_access import getPlayerTeamInSeasonFromBballRefLink

def preMatchPredictions(awayPlayerCode, awayPlayerTeam, dsd, homeOdds, homePlayerCode, homePlayerTeam, scoringTeam,
                        tipWinnerCode, winningBetThreshold):
    if homeOdds > winningBetThreshold:
        if tipWinnerCode[11:] == homePlayerCode:
            dsd['correctTipoffPredictions'] += 1
            print('good prediction on home tip winner')
        else:
            dsd['incorrectTipoffPredictions'] += 1
            print('bad prediction on home tip winner')
        if homePlayerTeam == scoringTeam:
            dsd["winningBets"] += 1
            print('good prediction on home scorer')
        else:
            dsd["losingBets"] += 1
            print('bad prediction on home tip scorer')
        pass
    elif (1 - homeOdds) > winningBetThreshold:
        if tipWinnerCode[11:] == awayPlayerCode:
            dsd['correctTipoffPredictions'] += 1
            print('good prediction on away tip winner')
        else:
            dsd['incorrectTipoffPredictions'] += 1
            print('bad prediction on away tip winner')
        if awayPlayerTeam == scoringTeam:
            dsd["winningBets"] += 1
            print('good prediction on away scorer')
        else:
            dsd['losingBets'] += 1
            print('bad prediction on away scorer')
    else:
        print('no bet, odds were not good enough')

def beforeMatchPredictions(season, psd, dsd, homePlayerCode, awayPlayerCode, tipWinnerCode, scoringTeam, winningBetThreshold, predictionFunction):
    homeOdds = predictionFunction(homePlayerCode, awayPlayerCode, psd=psd)
    homePlayerTeam = getPlayerTeamInSeasonFromBballRefLink(homePlayerCode, season, longCode=False)['currentTeam']
    awayPlayerTeam = getPlayerTeamInSeasonFromBballRefLink(awayPlayerCode, season, longCode=False)['currentTeam']

    if psd[homePlayerCode]['appearances'] > winningBetThreshold and psd[awayPlayerCode]['appearances'] > winningBetThreshold:
        preMatchPredictions(awayPlayerCode, awayPlayerTeam, dsd, homeOdds, homePlayerCode, homePlayerTeam, scoringTeam,
                            tipWinnerCode, winningBetThreshold)
    else:
        print('no bet, not enough Data on participants')

def runAlgorithmForSeason():
    # def runEloForSeason(season: str, seasonCsv: str, playerSkillDictPath: str,
    #                     winningBetThreshold: float = ENVIRONMENT.ELO_TIPOFF_ODDS_THRESHOLD, startFromBeginning=False):
    #     df = pd.read_csv(seasonCsv)
    #     # df = df[df['Home Tipper'].notnull()] # filters invalid rows
    #     # df['Home Elo'] = None
    #     # df['Away Elo'] = None
    #
    #     winningBets, losingBets = 0, 0
    #
    #     print('running for season doc', seasonCsv, '\n', '\n')
    #     colLen = len(df['Game Code'])
    #
    #     with open(playerSkillDictPath) as jsonFile:
    #         psd = json.load(jsonFile)
    #
    #     if startFromBeginning:
    #         i = 0
    #     else:
    #         i = colLen - 1
    #         lastGameCode = psd['lastGameCode']
    #         while df.iloc[i]['Game Code'] != lastGameCode:
    #             i -= 1
    #         i += 1
    #
    #     with open(ENVIRONMENT.ELO_PREDICTION_SUMMARIES_PATH) as jsonFile:
    #         dsd = json.load(jsonFile)
    #
    #     while i < colLen:
    #         if df['Home Tipper'].iloc[i] != df['Home Tipper'].iloc[i]:
    #             i += 1
    #             continue
    #         hTip = df['Home Tipper'].iloc[i]
    #         tWinner = df['Tipoff Winner'].iloc[i]
    #         aTip = df['Away Tipper'].iloc[i]
    #         tWinLink = df['Tipoff Winner Link'].iloc[i]
    #         tLoseLink = df['Tipoff Loser Link'].iloc[i]
    #         if tWinner == hTip:
    #             hTipCode = tWinLink[11:]
    #             aTipCode = tLoseLink[11:]
    #         elif tWinner == aTip:
    #             hTipCode = tLoseLink[11:]
    #             aTipCode = tWinLink[11:]
    #         else:
    #             raise ValueError('no match for winner')
    #
    #         eloBeforeMatchPredictions(season, psd, dsd, hTipCode, aTipCode, tWinLink, df['First Scoring Team'].iloc[i],
    #                                   winningBetThreshold)
    #         eloUpdateDataSingleTipoff(psd, tWinLink, tLoseLink, hTipCode, df['Full Hyperlink'].iloc[i])
    #         # df['Home Elo'].iloc[i] = homeElo
    #         # df['Away Elo'].iloc[i] = awayElo
    #
    #         i += 1
    #
    #     psd['lastGameCode'] = df.iloc[-1]['Game Code']
    pass
