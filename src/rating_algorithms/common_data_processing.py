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