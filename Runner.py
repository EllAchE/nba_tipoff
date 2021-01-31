# todo set up a database
from Live_Odds_Retrieval import get_center
from Functions.Odds_Calculator import win_rate_for_positive_ev, kelly_bet, cost_for_1
from Functions.True_Skill_Calc import tip_win_probability
from Functions.Utils import tip_score_prob


def check_for_edge(home_team, away_team, home_odds, away_odds, bankroll):
    home_c = get_center(home_team)
    away_c = get_center(away_team)
    pass


def get_bet_size(score_prob, american_odds, bankroll):
    loss_amt = cost_for_1(american_odds)
    return kelly_bet(loss_amt, score_prob, bankroll)


def check_ev_positive_and_get_score_prob(team_odds, team_center_code, opponent_center_code):
    min_win_rate = win_rate_for_positive_ev(team_odds)
    min_loss_rate = 1 - min_win_rate
    tip_win_odds = tip_win_probability(team_center_code, opponent_center_code)
    score_prob = tip_score_prob(tip_win_odds)

    if score_prob > min_win_rate:
        print('bet on them')
        return score_prob
    elif (1-score_prob) > min_loss_rate:
        print('bet against them')
        return (1-score_prob)
    else:
        print('don\'t bet either side')
        return None




# I need to - provide team name
# get starting centers
# get if they are home or away
# get odds for the bets of the day
# get positive EV threshold
# get the center ratings
# calculate expected odds of tip win
# multiply expected tip win by tip winner scoring ratio to get expected score prob (include tip loss score case)
# OPTIONAL - Adjust for home court etc.
# see if expected score prob is higher than EV threshold (or below 1 - EV thresh)
# if bet should be done
# calculate kelly bet size
# reduce to kelly consumable size

# i
# Format is https://www.basketball-reference.com/boxscores/pbp/201901220OKC.html
# Home team 3 letter symbol is used after a 0, i.e. YYYYMMDD0###.html
#
# URL for game https://www.basketball-reference.com/boxscores/pbp/201901220OKC.html
# Where YYYYMMDD0### (# = home team code)
#
# game schedule in order for seasons https://www.basketball-reference.com/leagues/NBA_2019_games.html
# Creating json/dictonary would probably be best
#
# Games played https://www.basketball-reference.com/leagues/NBA_2019_games-october.html
# Year is ending year (i.e. 2018-2019 is 2019)
# All relevant are October-June except 2019-2020 and 2020-21 (first bc covid, second is in progress)


# Steps to NBA check:
#
# Base requirements:
# -	Find the starters for each team/who does the tipoff:
# -	Player W/L %
#
# Additional variables
# -	Ref
# -	Is starter out
# -	Home/away
# -	Who they tip it to
# -	Matchup
# -	Height
# -	Offensive effectiveness
# -	Back-to-back games/overtime etc.
# -	Age decline
# -	Recent history weighting



# todo one edge case is not solved, i.e. a player is traded to a team and then plays against them, having both on their record for the season
# todo bundle together all of the low appearance players as a single entity
# todo offensive reboudning/defensive rebounding
# todo track stats on first appearance vs an experienced tipper
# todo track stats on appearance first time midseason
# todo use fuzzywuzzy to match teamnames

# TECHNICAL TODOS IN ORDER OF IMPT
# todo player to fullname to player code relationship
# todo fetch the odds for the day from draftkings or other site
# todo refactor/improve/standardize code base
# todo change true skill calc to add rows to csv
# todo add time decay to glicko/true skill RD
# todo player lineup checker
# todo incorporate other stats in (see below)
# i.e. store player codes consistently

# todo betting calendar
# todo have scheduler
# todo deal with players who play but aren't catalogued for a team (perhaps bad Data, i.e. satorto)
# todo account for injuries
# todo get first shooting player
# todo add first scored upon team
# todo scrape/use api from nba.com instead of bball reference https://www.nba.com/game/phx-vs-nyk-0021000598/play-by-play

### POTENTIAL ADDITIONAL VARIABLES FOR ODDS MODEL
# Offensive Efficiency
# Defensive Efficiency
# new center record (for low Data on tipper)

# Recency bias in ranking
# Season leaders
# Likely first shooter percentages
# Likely other shooter percentages
# Height matchup
# combine vertical
# Injury
# Back to back/overtime
# Return from long absence

# def all_in_one(start_season, path):
#     temp = pd.DataFrame()
#     temp.to_csv(path)
#     data_file = open(path, 'w')
#
#     with data_file:
#         csv_writer = csv.writer(data_file)
#         csv_writer.writerow(
#             ['Game Link', 'Home Team', 'Away Team', 'Home Team Short', 'Away Team Short', 'Home Tipper', 'Away Tipper',
#              'First Scorer', 'Tipoff Winning Team', 'First Scoring Team'])
#         game_headers = bball.get_game_headers(start_season)
#
#         sleep_counter = 0
#         for line in game_headers:
#             sleep_counter = bball.sleep_checker(sleep_counter, iterations=6, base_time=1, random_multiplier=1)
#             row = line + bball.get_tipoff_winner_and_first_score(line[0], start_season, line[3], line[4])
#             print(row)
#             csv_writer.writerow(row)