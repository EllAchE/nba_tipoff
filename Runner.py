from Functions.Odds_Calculator import checkEvPlayerCodesOddsLine, kellyBetFromAOddsAndScoreProb

# getStarters('NOP')
# getStarters('IND')
# getStarters('CHI')
# getStarters('ORL')
# getStarters('TOR')
# getStarters('BKN')
# getStarters('MIL')
# getStarters('CLE')
# getStarters('CHA')
# getStarters('WAS')
# getStarters('MIA')
# getStarters('OKC')
# getStarters('MIN')
# getStarters('DET')
# getStarters('PHX')
# getStarters('BOS')
# getStarters('LAC')
# getStarters('GSW')
# getStarters('DAL')
# getStarters('UTA')
# getStarters('ATL')
# getStarters('POR')
# getStarters('PHI')
# getStarters('HOU')
# getStarters('MEM')
# getStarters('DEN')
# getStarters('LAL')

a_odds = '-110' # -142
p1 = 'horfoal01.html'
p2 = 'reidna01.html'
a = checkEvPlayerCodesOddsLine(a_odds, p1, p2)
b = checkEvPlayerCodesOddsLine(a_odds, p2, p1)
print(kellyBetFromAOddsAndScoreProb(a, a_odds, bankroll=5000))
print(kellyBetFromAOddsAndScoreProb(b, a_odds, bankroll=5000))
print()

a_odds = '-110' # -142
p1 = 'gaffoda01.html'
p2 = 'vucevni01.html'
a = checkEvPlayerCodesOddsLine(a_odds, p1, p2)
b = checkEvPlayerCodesOddsLine(a_odds, p2, p1)
print(kellyBetFromAOddsAndScoreProb(a, a_odds, bankroll=5000))
print(kellyBetFromAOddsAndScoreProb(b, a_odds, bankroll=5000))
print()
a_odds = '-110' # -142
p1 = 'baynear01.html'
p2 = 'greenje02.html'
a = checkEvPlayerCodesOddsLine(a_odds, p1, p2)
b = checkEvPlayerCodesOddsLine(a_odds, p2, p1)
print(kellyBetFromAOddsAndScoreProb(a, a_odds, bankroll=5000))
print(kellyBetFromAOddsAndScoreProb(b, a_odds, bankroll=5000))
print()
a_odds = '+108' # -142
p1 = 'drumman01.html'
p2 = 'lopezbr01.html'
a = checkEvPlayerCodesOddsLine(a_odds, p1, p2)
b = checkEvPlayerCodesOddsLine(a_odds, p2, p1)
print(kellyBetFromAOddsAndScoreProb(a, a_odds, bankroll=5000))
print(kellyBetFromAOddsAndScoreProb(b, a_odds, bankroll=5000))
print()

a_odds = '-110' # -142
p1 = 'goberru01.html'
p2 = 'zelleco01.html'
a = checkEvPlayerCodesOddsLine(a_odds, p1, p2)
b = checkEvPlayerCodesOddsLine(a_odds, p2, p1)
print(kellyBetFromAOddsAndScoreProb(a, a_odds, bankroll=5000))
print(kellyBetFromAOddsAndScoreProb(b, a_odds, bankroll=5000))
print()

a_odds = '-110' # -142
p1 = 'ibakase01.html'
p2 = 'thomptr01.html'
a = checkEvPlayerCodesOddsLine(a_odds, p1, p2)
b = checkEvPlayerCodesOddsLine(a_odds, p2, p1)
print(kellyBetFromAOddsAndScoreProb(a, a_odds, bankroll=5000))
print(kellyBetFromAOddsAndScoreProb(b, a_odds, bankroll=5000))
print()

a_odds = '-110' # -142
p1 = 'aytonde01.html'
p2 = 'plumlma01.html'
a = checkEvPlayerCodesOddsLine(a_odds, p1, p2)
b = checkEvPlayerCodesOddsLine(a_odds, p2, p1)
print(kellyBetFromAOddsAndScoreProb(a, a_odds, bankroll=5000))
print(kellyBetFromAOddsAndScoreProb(b, a_odds, bankroll=5000))

a_odds = '-110' # -142
p1 = 'adamsst01.html'
p2 = 'turnemy01.html'
a = checkEvPlayerCodesOddsLine(a_odds, p1, p2)
b = checkEvPlayerCodesOddsLine(a_odds, p2, p1)
print(kellyBetFromAOddsAndScoreProb(a, a_odds, bankroll=5000))
print(kellyBetFromAOddsAndScoreProb(b, a_odds, bankroll=5000))



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

# TECHNICAL TODOS (NOT IN ORDER OF IMPT)
# todo fetch odds lines for the day from all sites offering props bets
# todo make data overwriting transactional
# todo setup odds prediction to use Ev or win prob rather than bet threshold
# todo player to fullname to player code relationship
# todo convert to object oriented (nba_api may solve this)
# todo create dictionary of active players (use nba_api for this)
# todo set up a database
# todo if not proper relational database at least proxy it with json/dictionaries
# todo use glicko2/compare it to trueskill
# todo add time decay to glicko/true skill RD
# todo add possible ranges of prediction accuracy based on RD to prediction prints (don't use in calcs yet)
# todo set up backtester with assumed odds lines
# todo set up bankroll tracker (with stored values on each site)
# todo player last name, season and team matcher
# todo deal with circular imports, make more files
# todo test if adding in the start of overtime tip performance enhances predictions (may be fatigue facotr/not as good)

# MISC
# todo unsolved edge case: a player is traded then plays against their original team, having both on their record for the season
# todo bundle together all of the low appearance players as a single entity
# todo offensive rebounding/defensive rebounding influence
# todo track stats on first appearance vs an experienced tipper
# todo track stats on appearance first time midseason, first tip ever etc.

# todo betting calendar (i.e. when do sites post their info)
# todo have scheduler
# todo deal with players who play but aren't catalogued for a team (perhaps bad Data, i.e. satorto)
# todo account for injuries
# todo get first shooting player
# todo scrape/use api from nba.com instead of bball reference https://www.nba.com/game/phx-vs-nyk-0021000598/play-by-play
# todo incorporate other stats in (see below)
# todo add other stats and run ludwig/ai checker

'''
To avoid arbitrage flags if we go that route: Bet round numbers, don't be super esoteric and bet at normal times
'''

### POTENTIAL ADDITIONAL VARIABLES FOR ODDS MODEL
# Offensive Efficiency
# Defensive Efficiency
# new center record (for low Data on tipper)

# Recency bias in ranking (ARIMA model or similar)
# Season leaders
# Likely first shooter percentages
# Likely other shooter percentages
# Height matchup
# combine vertical
# Injury
# Back to back/overtime
# Return from long absence
