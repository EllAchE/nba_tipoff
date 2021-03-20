from src.live_data.display_bets import getAllOddsAndDisplayByEv, getUniqueOddsAndDisplayByEv

getAllOddsAndDisplayByEv(fanduelTomorrow=True)
getAllOddsAndDisplayByEv(bovada=True)
getAllOddsAndDisplayByEv(betfair=True)
getAllOddsAndDisplayByEv(fanduelToday=True, mgm=True, draftkings=True, pointsbet=True, unibet=True, barstool=True, includeOptimalPlayerSpread=True)
# getAllOddsAndDisplayByEv(getFanduelToday=True, getMgm=True) #, getPointsBet=True, getUnibet=True, getBarstool=True)
# getAllOddsAndDisplayByEv(getDk=True)
# getAllOddsAndDisplayByEv(getBovada=True)
