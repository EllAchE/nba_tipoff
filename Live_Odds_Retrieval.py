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

import ENVIRONMENT
from Runner import check_for_edge


def team_code_to_full_name(team_code):
    full_name = 'Indiana-Pacers'
    return full_name


def get_starters(team_code):
    full_name = team_code_to_full_name(team_code)

    url = 'https://api.lineups.com/nba/fetch/lineups/current/{}'.format(full_name)
    response = requests.get(url).json()
    starters = response.starters

    starters_list = list()
    for player in starters:
        starters_list.append(player.name)
    return starters_list


def get_center(team_code):
    return team_code


def fetch_live_lines():
    pass


def get_game_info():
    # return time, home team, away team, starting centers
    pass


def get_all_odds_line(bankroll=ENVIRONMENT.BANKROLL):
    all_lines = fetch_live_lines()
    game_odds_list = list()

    for game in all_lines:
        gi = get_game_info(game)
        home = gi['home']
        away = gi['away']

        bet_size, win_odds, required_ev = check_for_edge(gi['home'], gi['away'], gi['h_odds'], gi['a_odds'], bankroll)
        game_odds_list.append([gi['datetime'], gi['homeCenter'], home, gi['awayCenter'], away, win_odds, required_ev, bet_size])

    return game_odds_list


def fanduel_odds():
    # https://sportsbook.fanduel.com/cache/psevent/UK/1/false/958472.3.json
    pass


def bovada_odds():
    # https://widgets.digitalsportstech.com/api/gp?sb=bovada&tz=-5&gameId=in,135430
    pass


def draftkings_odds():
    # https://sportsbook.draftkings.com/leagues/basketball/103?category=game-props&subcategory=odd/even
    pass