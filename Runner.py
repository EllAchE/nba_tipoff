from functions.odds_calculator import checkEvPlayerCodesOddsLine, kellyBetFromAOddsAndScoreProb

# teamList = ['NOP','IND', 'CHI', 'ORL', 'TOR', 'BKN', 'MIL', 'CLE', 'CHA', 'WAS', 'MIA', 'OKC', 'MIN', 'DET', 'PHX', 'BOS',\
#            'LAC', 'SAS', 'GSW', 'DAL', 'UTA', 'ATL', 'POR', 'PHI', 'HOU', 'MEM', 'DEN', 'LAL', 'SAC']
# teamList.sort()
# sleepCounter = 0
# for team in teamList:
#     getStarters(team)
#     sleepCounter = sleepChecker(sleepCounter, printStop=False)

a_odds = '-115' # -142
p1 = 'lopezro01.html'
p2 = 'zelleco01.html'
a = checkEvPlayerCodesOddsLine(a_odds, p1, p2)
b = checkEvPlayerCodesOddsLine(a_odds, p2, p1)
print(kellyBetFromAOddsAndScoreProb(a, a_odds, bankroll=5000))
print(kellyBetFromAOddsAndScoreProb(b, a_odds, bankroll=5000))
print()

a_odds = '-125' # -142
p1 = 'goberru01.html'
p2 = 'turnemy01.html'
a = checkEvPlayerCodesOddsLine(a_odds, p1, p2)
b = checkEvPlayerCodesOddsLine(a_odds, p2, p1)
print(kellyBetFromAOddsAndScoreProb(a, a_odds, bankroll=5000))
print(kellyBetFromAOddsAndScoreProb(b, a_odds, bankroll=5000))
print()

a_odds = '-110' # -142
p1 = 'adebaba01.html'
p2 = 'robinmi01.html'
a = checkEvPlayerCodesOddsLine(a_odds, p1, p2)
b = checkEvPlayerCodesOddsLine(a_odds, p2, p1)
print(kellyBetFromAOddsAndScoreProb(a, a_odds, bankroll=5000))
print(kellyBetFromAOddsAndScoreProb(b, a_odds, bankroll=5000))
print()

a_odds = '-110' # -142
p1 = 'thomptr01.html'
p2 = 'aytonde01.html'
a = checkEvPlayerCodesOddsLine(a_odds, p1, p2)
b = checkEvPlayerCodesOddsLine(a_odds, p2, p1)
print(kellyBetFromAOddsAndScoreProb(a, a_odds, bankroll=5000))
print(kellyBetFromAOddsAndScoreProb(b, a_odds, bankroll=5000))
print()

a_odds = '-110' # -142
p1 = 'holmeri01.html'
p2 = 'ibakase01.html'
a = checkEvPlayerCodesOddsLine(a_odds, p1, p2)
b = checkEvPlayerCodesOddsLine(a_odds, p2, p1)
print(kellyBetFromAOddsAndScoreProb(a, a_odds, bankroll=5000))
print(kellyBetFromAOddsAndScoreProb(b, a_odds, bankroll=5000))
print()

# a_odds = '-110' # -108, -118
# p1 = 'greenje02.html'
# p2 = 'embiijo01.html'
# a = checkEvPlayerCodesOddsLine(a_odds, p1, p2)
# b = checkEvPlayerCodesOddsLine(a_odds, p2, p1)
# print(kellyBetFromAOddsAndScoreProb(a, a_odds, bankroll=5000))
# print(kellyBetFromAOddsAndScoreProb(b, a_odds, bankroll=5000))
# print()
#
# a_odds = '-110' # -142
# p1 = 'horfoal01.html'
# p2 = 'reidna01.html'
# a = checkEvPlayerCodesOddsLine(a_odds, p1, p2)
# b = checkEvPlayerCodesOddsLine(a_odds, p2, p1)
# print(kellyBetFromAOddsAndScoreProb(a, a_odds, bankroll=5000))
# print(kellyBetFromAOddsAndScoreProb(b, a_odds, bankroll=5000))
# print()
#
# a_odds = '-125' # -142
# p1 = 'porzikr01.html'
# p2 = 'greendr01.html'
# a = checkEvPlayerCodesOddsLine(a_odds, p1, p2)
# b = checkEvPlayerCodesOddsLine(a_odds, p2, p1)
# print(kellyBetFromAOddsAndScoreProb(a, a_odds, bankroll=5000))
# print(kellyBetFromAOddsAndScoreProb(b, a_odds, bankroll=5000))
# print()
#
# a_odds = '-110' # -142
# p1 = 'valanjo01.html'
# p2 = 'adamsst01.html'
# a = checkEvPlayerCodesOddsLine(a_odds, p1, p2)
# b = checkEvPlayerCodesOddsLine(a_odds, p2, p1)
# print(kellyBetFromAOddsAndScoreProb(a, a_odds, bankroll=5000))
# print(kellyBetFromAOddsAndScoreProb(b, a_odds, bankroll=5000))
# print()
#
# a_odds = '-110' # -142
# p1 = 'plumlma01.html'
# p2 = 'davisan01.html'
# a = checkEvPlayerCodesOddsLine(a_odds, p1, p2)
# b = checkEvPlayerCodesOddsLine(a_odds, p2, p1)
# print(kellyBetFromAOddsAndScoreProb(a, a_odds, bankroll=5000))
# print(kellyBetFromAOddsAndScoreProb(b, a_odds, bankroll=5000))
# print()
#
# a_odds = '-110' # -142
# p1 = 'poeltja01.html'
# p2 = 'couside01.html'
# a = checkEvPlayerCodesOddsLine(a_odds, p1, p2)
# b = checkEvPlayerCodesOddsLine(a_odds, p2, p1)
# print(kellyBetFromAOddsAndScoreProb(a, a_odds, bankroll=5000))
# print(kellyBetFromAOddsAndScoreProb(b, a_odds, bankroll=5000))

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

# Bookmakers https://the-odds-api.com/sports-odds-data/bookmaker-apis.html
# TECHNICAL TODOS (NOT IN ORDER OF IMPT)
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
# todo deal with players who play but aren't catalogued for a team (perhaps bad Data, i.e. satorto)
# todo scrape/use api from nba.com instead of bball reference https://www.nba.com/game/phx-vs-nyk-0021000598/play-by-play

'''
To avoid arbitrage flags if we go that route: Bet round numbers, don't be super esoteric and bet at normal times.
Also consider parlays as throwaways to placate the monitors
'''
