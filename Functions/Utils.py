import json

import ENVIRONMENT


def tip_score_prob(tip_win_odds, tip_winner_score_odds=ENVIRONMENT.TIP_WINNER_SCORE_ODDS):
    return tip_win_odds * tip_winner_score_odds + (1-tip_win_odds) * (1-tip_winner_score_odds)


def add_slug_to_names():
    with open('../Data/Public_NBA_API/teams.json') as dat_file:
        team_dict = json.load(dat_file)

    for team in team_dict:
        slug = team['teamName']
        slug = slug.replace(" ", "-")
        slug = slug.lower()
        team['slug'] = slug

    with open('../Data/Public_NBA_API/teams.json', 'w') as w_file:
        json.dump(team_dict, w_file)

    print('added slugs')
