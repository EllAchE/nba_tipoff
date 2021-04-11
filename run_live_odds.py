from src.live_data.display_bets import getAllOddsAndDisplayByEv, getUniqueOddsAndDisplayByEv
from src.odds_and_statistics.odds_calculator import checkForArbitrageInRetrievedOdds

getAllOddsAndDisplayByEv(bovada=True, betfair=True, fanduelToday=True, mgm=True, draftkings=True)#, pointsbet=True, unibet=True, barstool=True, includeOptimalPlayerSpread=True)
checkForArbitrageInRetrievedOdds()
