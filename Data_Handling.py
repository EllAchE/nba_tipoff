'''
reads processed data
'''

import pandas as pd

# create set of all tipping players, in win or lose column
# create a dictionary with their names with values of wins and losses
# go through the two columns of the game list and add or subtract for each time a name is found

path = 'test.csv'


def get_tipoff_records():
    df = pd.read_csv(path)
    all_players = set()

    player_dict = {}

    for player in df['Tipoff Winner']:
        all_players.add(player)
    for player in df['Tipoff Loser']:
        all_players.add(player)

    for player in all_players:
        player_dict[player] = {'appearances': 0, 'wins': 0, 'losses': 0}

    for player in df['Tipoff Winner']:
        try:
            player_dict[player]['appearances'] += 1
        except:
            pass
    for player in df['Tipoff Loser']:
        try:
            player_dict[player]['appearances'] += 1
        except:
            pass

    llen = len(df['Tipoff Loser'])
    wlen = len(df['Tipoff Winner'])
    print(llen)
    print(wlen)

    total_loss = 0
    total_win = 0

    for winner in df['Tipoff Winner']:
        try:
            player_dict[winner]['wins'] += 1
            total_win += 1
        except:
            pass
    for loser in df['Tipoff Loser']:
        try:
            player_dict[loser]['losses'] += 1
            total_loss += 1
        except:
            pass
    print()

get_tipoff_records()
