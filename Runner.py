# backlogtodo find out when the best time for placing bets on various sites is (i.e. when do odds move)
# backlogtodo next prop - who scores last nba, race to 5 points
# backlogtodo compare top rank vs. bottom rank losses
# backlogtodo reverse engineer odds from site odds and use that to find mismatches in correlation i.e. last team to score
# backlogtodo convert from printing desired bets to putting them into a json/csv
# backlogtodo unsolved edge case: a player is traded then plays against their original team, having both on their record for the season. This may be solved by just taking the last index of team list, unless
# backlogtodo a solution to the edge case above: use the nba api team fetching for cases when there is a match
# backlogtodo look into multithreading for the multiple algorithm analysis (run the three concurrently)
# backlogtodo add player start percentage to 1st shot summary
# backlogtodo replace values passed in the many args algos with ENV vars
# backlogtodo expand to NCAA which is offered on betmgm
# backlogtodo expand to other countries which are offered on betmgm
# backlogtodo write checker for updating all data that may need to be updated
# backlogtodo write checker for updating only game to game data (not rare breaking things like new players/player team pairs
# backlogtodo performance improvements, binary search of player db and smaller file size
# backlogtodo performance improvements, use in and index[itemIWant] for C native code performance improvements in numpy
# backlogtodo update print statements to show more and take up less space
# backlogtodo combine to update all relevant game dictionaries from last game after fetching new game details
# More books https://bookies.com/pennsylvania. Already checked these and living in CO there are a bunch of app only options, no idea what they ofer
# backlogtodo import decimal module or similar https://docs.python.org/3/library/decimal.html
# backlogtodo look for when there is a big gap between the exchanges (not necessarily arbitrage) and just determine which is worse at their job. Take one side, not both, of the bets.
# backlogtodo change this to update just the current season
# todo fix optimized player spreads across exchanges (i.e. look at first point on fd, bovada and dk; Need to consider first field goal as well)

import ENVIRONMENT
from src.database.database_creation import getAllGameData, createPlayerEloDictionary, \
    createPlayerGlickoDictionary, saveActivePlayersTeams, createPlayerNameRelationship
from src.historical_data.bball_reference_historical_data import updateCurrentSeasonRawGameData, oneSeasonFromScratch
from src.historical_data.nba_play_by_play_methods import getAllFirstPossessionStatisticsIncrementally, \
    splitAllSeasonsFirstShotDataToMultipleFiles, getSingleGameStarters, saveAllHistoricalStarters, \
    teamSummaryDataFromFirstPointData, getTipoffLineFromBballRefId
from src.live_data.display_bets import getAllOddsAndDisplayByEv, getUniqueOddsAndDisplayByEv
from src.live_data.live_odds_retrieval import getAllExpectedStarters, getDailyOdds, betfairOdds
from src.odds_and_statistics.prediction_enhancements import getFirstFieldGoalOrFirstPointStats, getCurrentSeasonUsageRate
from src.rating_algorithms.elo_data_processing import runEloForAllSeasons, calculateEloDictionaryFromZero
from src.rating_algorithms.glicko_data_processing import runGlickoForAllSeasons, calculateGlickoDictionaryFromZero
from src.rating_algorithms.trueskill_data_processing import calculateTrueSkillDictionaryFromZero, updateTrueSkillDictionaryFromLastGame

# for ml model add - team continuity factor & previous seasons stats

# getAllGameData()
# getAllFirstPossessionStatisticsIncrementally(2021)
# getFirstFieldGoalOrFirstPointStats(ENVIRONMENT.CURRENT_SEASON)  # Since Hornets became a team
# teamSummaryDataFromFirstPointData(ENVIRONMENT.CURRENT_SEASON)
getTipoffLineFromBballRefId('199711040NYK')
print()

# calculateEloDictionaryFromZero()
# createPlayerNameRelationship()
# saveActivePlayersTeams(1998)
# getAllGameData()
# updateCurrentSeasonRawGameData()
# updateTrueSkillDictionaryFromLastGame()
# oneSeasonFromScratch(2021)

# getAllExpectedStarters()

# calculateGlickoDictionaryFromZero()
# calculateTrueSkillDictionaryFromZero()
# calculateEloDictionaryFromZero()
# backlogtodo look at first 100 and last 100 games (or similar) of player performance vs. overall (on tip)

# calculateGlickoDictionaryFromZero()

# getAllOddsAndDisplayByEv(getFanduelToday=True, getDk=True, getBovada=True, getMgm=True, getPointsBet=True, getUnibet=True, getBarstool=True)
# getAllOddsAndDisplayByEv(getFanduelToday=True, includeOptimalPlayerSpread=True)#, getPointsBet=True, getUnibet=True, getBarstool=True)
# getAllOddsAndDisplayByEv(getFanduelTomorrow=True, getMgm=True)
# getAllOddsAndDisplayByEv(getMgm=True)
# getAllOddsAndDisplayByEv(getDk=True)#, getBovada=True)
# getAllOddsAndDisplayByEv(getBovada=True)# includeOptimalPlayerSpread=True)
# getAllOddsAndDisplayByEv(getUnibet=True)
# getUniqueOddsAndDisplayByEv(getBovada=True, getUnibet=True)
# getAllOddsAndDisplayByEv(getBovada=True, getUnibet=True)
#

#
getDailyOdds('MIA', 'MEM', '-115')
'''
Existing apis etc.

nba.com:
https://github.com/bttmly/nba-client-template/blob/master/nba.json
https://github.com/bttmly/nba

basketball reference:
https://github.com/vishaalagartha/basketball_reference_scraper/blob/master/API.md

nba play by play:
https://github.com/swar/nba_api/

https://www.olbg.com/blogs/basketball-betting-first-basketwinner-market-strategy
https://www.reddit.com/r/nba/comments/dhandf/oc_elo_system_to_determine_who_are_the_best_at/

Existing jumpball elo:
https://github.com/mattgalarneau/NBA-Jump-Balls/blob/master/Data/Bball_Ref_Player_List.py

Bet limits https://fanduelsportsbook.zendesk.com/hc/en-us/articles/360001688007-FanDuel-Sportsbook-House-Rules-New-Jersey
https://sportsbook.draftkings.com/help/general-betting-rules/sport-specific-limits
https://www.rebelbetting.com/surebetting

arbitrage offers:
https://www.betfair.com/sport/basketball/nba/houston-rockets-oklahoma-city-thunder/30266729
https://www.betburger.com/?sure_bets=1160
https://punter2pro.com/best-sports-arbing-software/
'''

# backlogtodo set up backtester with assumed odds lines, i.e. assuming we are always offered odds on a team of -110, how would the strat perform? (the default should -110)
# backlogtodo set up backtester using pickled GameOdds objects
# backogtodo test if adding in the start of overtime tip performance enhances predictions (may be fatigue facotr/not as good)
# backlogtodo account for overrepresentation of playoff teams

# MISC
# backlogtodo investigate adjsuted starting rankings for low appearance players, i.e. if we can assume certain/lower mu values for a class of player we can improve our predictions
# backlogtodo (OVERKILL) have scheduler for scraping with randomized twice-a-day fetching and telegram alerts
