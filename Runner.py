# backlogtodo find out when the best time for placing bets on various sites is (i.e. when do odds move)
# backlogtodo next prop - who scores last nba, race to 5 points
# todo compare top rank vs. bottom rank losses
# backlogtodo add exchange names to the jsonpickle file name
# backlogtodo convert from printing desired bets to putting them into a json/csv
# backlogtodo unsolved edge case: a player is traded then plays against their original team, having both on their record for the season
# backlogtodo a solution to the edge case above: use the nba api team fetching for cases when there is a match
from src.database.database_creation import getAllGameData
from src.historical_data.historical_data_retrieval import updateCurrentSeason
from src.historical_data.nba_public import getAllFirstPossessionStatisticsIncrementally, \
    splitAllSeasonsFirstShotDataToMultipleFiles, getSingleGameStarters, saveAllHistoricalStarters
from src.live_data.display_bets import getAllOddsAndDisplayByEv
from src.live_data.live_odds_retrieval import getAllExpectedStarters, getDailyOdds
from src.odds_and_statistics.prediction_enhancements import getFirstShotStats, getCurrentSeasonUsageRate
from src.trueskill.trueskill_calc import updateSkillDictionary

# getAllGameData()

# splitAllSeasonsFirstShotDataToMultipleFiles()

# createPlayerNameRelationship()
# saveActivePlayersTeams(1998)

# todo TEST optimized player spreads across exchanges (i.e. look at first point on fd, bovada and dk; Need to consider first field goal as well
# todo add player start percentage to 1st shot summary (retrieve game rotation stats from NBA API)
# todo fix fanduel when there are games to fetch data from
# todo performance improvements, binary search of player db
# todo performance improvements, backwards count and metadata sto

# getCurrentSeasonUsageRate()
saveAllHistoricalStarters()
# updateCurrentSeason()
# updateSkillDictionary()

# getFirstShotStats(2021)
#
# getAllExpectedStarters()

# getDailyOdds('BOS', 'TOR', '-111')
# getDailyOdds('PHX', 'GSW', '+116')
# getDailyOdds('IND', 'DEN', '-111')
# getDailyOdds('LAC', 'WAS', '+100')

# getAllOddsAndDisplayByEv(getDk=True, getBovada=True, getMgm=True)#, getPointsBet=True, getUnibet=True, getBarstool=True)

#backlogtodo see about optimizing this fetching

# test_bad_data_games = [['199711110MIN', 'MIN', 'SAS'],
#                        ['199711160SEA', 'SEA', 'MIL'],
#                        ['199711190LAL', 'LAL', 'MIN'],
#                        ['201911200TOR', 'TOR', 'ORL'],
#                        ['201911260DAL', 'DAL', 'LAC']] # Last one is a violation, others are misformatted
# '199711210SEA', '199711240TOR', '199711270IND', '201911040PHO',

'''
Existing apis etc.:

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

# backlogtodo make data overwriting transactional, i.e. locally saved csv could have all or no rows updated, no overwrites and partial
# backlogtodo set up backtester with assumed odds lines, i.e. assuming we are always offered odds on a team of -110, how would the strat perform? (the default should -110)
# backlogtodo OVERKILL set up bankroll tracker (with stored values on each site and overall).
# backogtodo test if adding in the start of overtime tip performance enhances predictions (may be fatigue facotr/not as good)
# backlogtodo account for overrepresentation of playoff teams

# MISC
# todo investigate adjsuted starting rankings for low appearance playersy, i.e. if we can assume certain/lower mu values for a class of player we can improve our predictions
# backlogtodo (OVERKILL) have scheduler for scraping with randomized twice-a-day fetching and telegram alerts
# backlogtodo see if back to back against same team matters
