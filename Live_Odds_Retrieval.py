# sites with game props
# https://www.bovada.lv/sports/basketball/nba
# https://sportsbook.fanduel.com/sports/event/958472.3
# draftkings
# https://www.betnow.eu/nba/ says it has props bets

# https://www.rotowire.com/basketball/nba-lineups.php
# https://www.nba.com/players/todays-lineups
# stats api here - https://stats.nba.com/js/data/leaders/00_active_starters_20210128.json
# https://rotogrinders.com/lineups/nba
# https://dailynbalineups.com/
# https://www.lineups.com/nba/lineups

import requests


def team_code_to_full_name(team_code):
    full_name = 'Indiana-Pacers'
    return full_name


def get_current_starters(team_code):
    full_name = team_code_to_full_name(team_code)

    url = 'https://api.lineups.com/nba/fetch/lineups/current/{}'.format(full_name)
    response = requests.get(url).json()
    starters = response.starters

    starters_list = list()
    for player in starters:
        starters_list.append(player.name)
    return starters_list


def fanduel_odds():
    # https://sportsbook.fanduel.com/cache/psevent/UK/1/false/958472.3.json
    pass


def bovada_odds():
    # https://widgets.digitalsportstech.com/api/gp?sb=bovada&tz=-5&gameId=in,135430
    pass


def draftkings_odds():
    # https://sportsbook.draftkings.com/leagues/basketball/103?category=game-props&subcategory=odd/even
    pass