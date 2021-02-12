# todo find out when the best time for placing bets on various sites is (i.e. when do odds move)
# todo next prop - who scores last nba

# getAllExpectedStarters()

# update2021Data()
from tipoff.functions.trueskill_calc import updateSkillDictionary

updateSkillDictionary()

# getDailyOdds('TOR', 'WAS')

# test_bad_data_games = [['199711110MIN', 'MIN', 'SAS'],
#                        ['199711160SEA', 'SEA', 'MIL'],
#                         ['199711190LAL', 'LAL', 'MIN'],
#                         ['201911200TOR', 'TOR', 'ORL'],
#                         ['201911260DAL', 'DAL', 'LAC']] # Last one is a violation, others are misformatted
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

# todo read into glicko math and try to do estimation of rnage
# todo make data overwriting transactional, i.e. locally saved csv should have all or no rows updated, no partial
# todo player to fullname to player code relationship
# todo convert to object oriented, i.e. where players are represented have them be a player object (nba_api may solve this, it has objects for many data types we care about already)
# todo create dictionary of active players (you can possibly use nba_api for this, and then enhance for bball ref compatibility)
# todo set up backtester with assumed odds lines, i.e. assuming we are always offered odds on a team of -110, how would the strat perform? (the default should -110)
# todo OVERKILL set up bankroll tracker (with stored values on each site and overall).
# todo test if adding in the start of overtime tip performance enhances predictions (may be fatigue facotr/not as good)

# MISC
# todo investigate adjsuted starting rankings for low appearance playersy, i.e. if we can assume certain/lower mu values for a class of player we can improve our predictions

# todo betting calendar (i.e. when do sites post their info)
# todo (OVERKILL) have scheduler for scraping with randomized twice-a-day fetching and telegram alerts
# todo see if back to back against same team matters

'''
To avoid arbitrage flags if we go that route: Bet round numbers, don't be super esoteric and bet at normal times.
Also consider parlays as throwaways to placate the monitors
'''
