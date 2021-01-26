'''
reads processed data
'''
import json

import pandas as pd


def team_tipoff_scoring_records(save_path, data_path):
    df = pd.read_csv(data_path)
    team_dict = {}

    all_teams = set()
    for team in df['Home Short']: #todo this may be the wrong name
        all_teams.add(team)

    json_file = open(save_path, 'w')

    with json_file:
        json.dump(team_dict, json_file)


# def get_player_tipoff_records(save_path, data_path):
#     df = pd.read_csv(data_path)
#     all_players = set()
#
#     player_dict = {}
#
#     for player in df['Tipoff Winner']:
#         all_players.add(player)
#     for player in df['Tipoff Loser']:
#         all_players.add(player)
#
#     for player in all_players:
#         player_dict[player] = {'appearances': 0, 'wins': 0, 'losses': 0}
#
#     for player in df['Tipoff Winner']:
#         try:
#             player_dict[player]['appearances'] += 1
#         except:
#             pass
#     for player in df['Tipoff Loser']:
#         try:
#             player_dict[player]['appearances'] += 1
#         except:
#             pass
#
#     for winner in df['Tipoff Winner']:
#         try:
#             player_dict[winner]['wins'] += 1
#         except:
#             pass
#     for loser in df['Tipoff Loser']:
#         try:
#             player_dict[loser]['losses'] += 1
#         except:
#             pass
