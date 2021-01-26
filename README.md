# nba-tipoff-scraper

Player tipoff skill ranking is done using glicko2 algorithm. Elo and trueskill from Microsoft were also considered but
Elo doesn't account for uncertainty and true skill doesn't have a time drift

Retrieves raw data from pages as csv

Steps to NBA check:

Base requirements:
-	Find the starters for each team/who does the tipoff:
-	Player W/L %

Additional variables
-	Ref
-	Is starter out
-	Home/away
-	Who they tip it to
-	Matchup
-	Height
-	Offensive effectiveness
-	Back-to-back games/overtime etc.
-	Age decline
-	Recent history weighting

Format is https://www.basketball-reference.com/boxscores/pbp/201901220OKC.html
Home team 3 letter symbol is used after a 0, i.e. YYYYMMDD0###.html
https://fansided.com/stats/jump-ball-statistics-1998-present/
Guy who compiled the tip off stats https://twitter.com/FattMemrite
https://sportsbook.draftkings.com/leagues/basketball/103?category=game-props&subcategory=first-team-to-score
'''

URL for game https://www.basketball-reference.com/boxscores/pbp/201901220OKC.html
Where YYYYMMDD0### (# = home team code)

game schedule in order for seasons https://www.basketball-reference.com/leagues/NBA_2019_games.html
Creating json/dictonary would probably be best

Games played https://www.basketball-reference.com/leagues/NBA_2019_games-october.html
Year is ending year (i.e. 2018-2019 is 2019)
All relevant are October-June except 2019-2020 and 2020-21 (first bc covid, second is in progress)