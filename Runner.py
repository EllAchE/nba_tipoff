from Data_Handling import one_season

start_season = 2021

# sss = [1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021]
#
# for start_season in sss:

all_at_once_path = "tipoff_and_first_score_details_starting_" + str(start_season) + "_season.csv"
single_season_path = "tipoff_and_first_score_details_" + str(start_season) + "_season.csv"

one_season(start_season, single_season_path)

# todo add possession gaining player to csv columns
# todo one edge case is not solved, i.e. a player is traded to a team and then plays against them, having both on their record for the season
# todo bundle together all of the low appearance players as a single entity
# todo ask brad to find some bookies
# todo offensive reboudning/defensive rebounding


# NON TECHNICAL TODOS
# todo find data source of historical efficiency
# todo find other betting sites with tipoff/score first. Prejudice

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
# todo deal with players who play but aren't catalogued for a team (perhaps bad data, i.e. satorto)
# todo account for injuries
# todo get first shooting player
# todo add first scored upon team
# todo scrape/use api from nba.com instead of bball reference https://www.nba.com/game/phx-vs-nyk-0021000598/play-by-play

### POTENTIAL ADDITIONAL VARIABLES FOR ODDS MODEL
# Offensive Efficiency
# Defensive Efficiency
# Home advantage
# new center record (for low data on tipper)

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