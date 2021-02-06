# sites with game props
# https://www.bovada.lv/sports/basketball/nba
# https://sportsbook.fanduel.com/sports/event/958472.3
# https://sportsbook.draftkings.com/leagues/basketball/103?category=game-props&subcategory=odd/even
# https://www.betnow.eu/nba/ says it has props bets

# Places to retrieve live lineups
# https://www.rotowire.com/basketball/nba-lineups.php
# https://www.nba.com/players/todays-lineups
# stats api here - https://stats.nba.com/js/data/leaders/00_active_starters_20210128.json
# https://rotogrinders.com/lineups/nba
# https://dailynbalineups.com/
# https://www.lineups.com/nba/lineups
import json

import requests
import pandas as pd

import ENVIRONMENT
from Classes.GameOdds import GameOdds
from Functions.Odds_Calculator import check_for_edge


def getExpectedTipper():
    lastTipper = getLastTipper()
    injuryCheck = checkInjury(lastTipper)
    starteerCheck = checkStarter(lastTipper) #todo confirmation of expected tipper
    pass


def getLastTipper(team_code, season_csv='CSV/tipoff_and_first_score_details_2021_season.csv'):
    df = pd.read_csv(season_csv)
    i = len(df['Game Code']) - 1
    while i >= 0:
        if df['Home Short'].iloc[i] == team_code:
            name = df['Home Tipper'].iloc[i]
            print('last tipper for', team_code, 'was', name)
            return name  # , get_player_suffix(name)
        elif df['Away Short'].iloc[i] == team_code:
            name = df['Away Tipper'].iloc[i]
            print('last tipper for', team_code, 'was', name)
            return name  # , get_player_suffix(name)
        i += 1

    raise ValueError('No match found for team code this season')


def fetch_live_lines():
    pass


def getGameInfo():
    # return time, home team, away team, starting centers
    pass


def teamCodeToSlugName(team_code, team_dict=None, json_path=None):
    if json_path is not None:
        with open(json_path) as j_file:
            team_dict = json.load(j_file)
    elif team_dict is None:
        with open('Data/Public_NBA_API/teams.json') as j_file:
            team_dict = json.load(j_file)

    for team in team_dict:
        if team['abbreviation'] == team_code:
            return team['slug']

    raise ValueError('no matching team for abbreviation')


def getAllOddsLines(bankroll=ENVIRONMENT.BANKROLL):
    all_lines = fetch_live_lines()
    game_odds_list = list()

    for game in all_lines:
        gi = getGameInfo(game)
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


def mgm_odds():
    # https://sports.co.betmgm.com/en/sports/events/minnesota-timberwolves-at-san-antonio-spurs-11101908?market=10000
    pass


# def betfair_odds():
#     # https://www.betfair.com/sport/basketball/nba/houston-rockets-oklahoma-city-thunder/30266729
#     # these are not american odds so will need some new methods for these
#     pass


def getStarters(team_code, team_dict=None): # todo look for a confirmed tag on this
    full_name = teamCodeToSlugName(team_code, team_dict)

    url = 'https://api.lineups.com/nba/fetch/lineups/current/{}'.format(full_name)
    response = requests.get(url).json()
    starters = response['starters']

    def sort_fn(e):
        return e[1]

    starters_list = list()
    for player in starters:
        starters_list.append([player['name'], player['position']])

    date = response['nav']['matchup_day']
    confirmed = 'lineup confirmed for'
    if not response['nav']['lineup_confirmed']:
        confirmed = 'LINEUP NOT YET CONFIRMED for'

    starters_list.sort(key=sort_fn)
    print(confirmed, date + '.', 'Starters for', team_code, 'are', starters_list)
    return starters_list


def displayUniqueBetsByEV(betDict):
    pass


def displayUniqueBetsByEV(betDict):
    pass


def displayAllBetsByEV(betDict):
    oddsList = convertDictToGameOddsObjList(betDict)
    oddsList.sort(key=lambda x: x.bestEVFactor)
    pass


def displayAllBetsByDatetime(betDict):
    oddsList = convertDictToGameOddsObjList(betDict)
    oddsList.sort(key=lambda x: x.bestEVFactor)
    oddsList.sort(key=lambda x: x.gameDatetime)
    pass


def displayAllBetsByExchange(betDict):
    oddsList = convertDictToGameOddsObjList(betDict)
    oddsList.sort(key=lambda x: x.bestEVFactor)
    oddsList.sort(key=lambda x: x.gameDatetime)
    oddsList.sort(key=lambda x: x.exchange)
    pass


def convertDictToGameOddsObjList(betDict):
    gameOddsObjList = list()
    for game in betDict['games']:
        oddsObj = GameOdds(game)
        gameOddsObjList.append(oddsObj)
    return gameOddsObjList


def printOddsObjDetails(oddsList, showAll=False):
    i = 0
    for g in oddsList:
        if not showAll and not g.betEither():
            continue
        betOn = g.betOn()
        fhsp = round(float(g.homeScoreprob), 2)
        fmbo = round(float(g.minHomeWinPercentage), 2) if g.betOnHome else round(float(g.minAwayWinPercentage), 2)
        bov = g.bestBetIsTeamOrPlayers()

        print(str(i) + '.', g.gameCode, "|| Bet On:", betOn, "Via:", bov, "|| Kelly Bet:", g.kellyBet, "|| EV Factor:", g.bestEVFactor) # ". Home/Away:", g.home, g.away,
        print("   Tipoff:", g.gameDatetime, "Tippers-H/A", g.expectedHomeTipper, g.expectedAwayTipper,
              "Odds Home Wins", fhsp, "Min Odds (HoDef):", fmbo, "Home Line:", g.bestHomeOdds, "Away Line:", g.bestAwayOdds)
        print('   Exchange:', g.exchange, 'Market URL', g.url, 'Odds as of:', g.fetchedDatetime)
        print()
        i += 1
        #todo add the player Spread display here
