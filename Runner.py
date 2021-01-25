'''
Runner calls methods from Data_Retrieval.py
'''
import Data_Retrieval as bball
import pandas as pd
import csv

start_season = 2016

path = "tipoff_and_first_score_details_starting_" + str(start_season) + "_season.csv"

temp = pd.DataFrame()
temp.to_csv(path)
data_file = open(path, 'w')

with data_file:
    csv_writer = csv.writer(data_file)
    csv_writer.writerow(['Game Link', 'Home Team', 'Away Team', 'Home Team Short', 'Away Team Short', 'Home Tipper', 'Away Tipper', 'First Scorer', 'Tipoff Winning Team', 'First Scoring Team'])
    game_headers = bball.get_game_headers(start_season)

    sleep_counter = 0
    for line in game_headers:
        sleep_counter = bball.sleep_checker(sleep_counter, iterations=6, base_time=1, random_multiplier=1)
        row = line + bball.get_tipoff_winner_and_first_score(line[0], start_season, line[3], line[4])
        print(row)
        csv_writer.writerow(row)


# todo add possession gaining player to csv columns
