'''
Existing apis etc.:

nba.com:
https://github.com/bttmly/nba-client-template/blob/master/nba.json
https://github.com/bttmly/nba

basketball reference:
https://github.com/vishaalagartha/basketball_reference_scraper/blob/master/API.md
'''

# TECHNICAL TODOS (NOT IN ORDER OF IMPT)
# todo fetch odds lines for the day from all sites offering props bets
# todo make data overwriting transactional
# todo setup odds prediction to use Ev or win prob rather than bet threshold
# todo player to fullname to player code relationship
# todo convert to object oriented
# todo create dictionary of active players
# todo change true skill calc to add rows to csv showing ratings at that instant (prior to game)
# todo set up a database
# todo if not proper relational database at least proxy it with json/dictionaries
# todo use glicko2/compare it to trueskill
# todo add time decay to glicko/true skill RD
# todo add possible ranges of prediction accuracy based on RD to prediction prints (don't use in calcs yet)
# todo set up backtester with assumed odds lines
# todo set up bankroll tracker (with stored values on each site)
# todo change default sleep checker to be zeros

# MISC
# todo unsolved edge case: a player is traded then plays against their original team, having both on their record for the season
# todo bundle together all of the low appearance players as a single entity
# todo offensive rebounding/defensive rebounding influence
# todo track stats on first appearance vs an experienced tipper
# todo track stats on appearance first time midseason
# todo use fuzzywuzzy to match teamnames

# todo betting calendar (i.e. when do sites post their info)
# todo have scheduler
# todo deal with players who play but aren't catalogued for a team (perhaps bad Data, i.e. satorto)
# todo account for injuries
# todo get first shooting player
# todo add first scored upon team
# todo scrape/use api from nba.com instead of bball reference https://www.nba.com/game/phx-vs-nyk-0021000598/play-by-play
# todo incorporate other stats in (see below)
# todo add other stats and run ludwig/ai checker

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
