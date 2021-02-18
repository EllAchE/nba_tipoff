# Places to retrieve live lineups
# https://www.rotowire.com/basketball/nba-lineups.php
# https://www.nba.com/players/todays-lineups
# stats api here - https://stats.nba.com/js/data/leaders/00_active_starters_20210128.json
# https://rotogrinders.com/lineups/nba
# https://dailynbalineups.com/
# https://www.lineups.com/nba/lineups

import json
import re

import requests
import pandas as pd

import ENVIRONMENT
from tipoff.functions.odds_calculator import check_for_edge, checkEvPlayerCodesOddsLine, kellyBetFromAOddsAndScoreProb
from tipoff.functions.utils import sleepChecker, getTeamFullFromShort, getPlayerTeamFromFullName, getSoupFromUrl
from tipoff.historical_data.historical_data_retrieval import getPlayerTeamInSeasonFromBballRefLink


# todo add a threshold of ev factor to only take safer bets
def getExpectedTipper(team):
#     lastTipper = getLastTipper()
#     injuryCheck = checkInjury(lastTipper)
#     starterCheck = checkStarter(lastTipper)
# todo find a way to get and confirm expected tipper; i.e. you have to look at injuries, changes to starting lineup & team history if it's a nonstandard lineup. May be best to just flag edge cases
# todo in cases where a starter who tips is out we probably want an alert as these are good opportunties for mispricing

    if len(team) != 3:
        raise ValueError('Need to pass team short code to getExpectedTipper')

    tipper = tipperFromTeam(team)
    return tipper

    if len(team) != 3:
        raise ValueError('Need to pass team short code to getExpectedTipper')

    tipper = tipperFromTeam(team)
    return tipper

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

def teamCodeToSlugName(team_code, team_dict=None, json_path=None):
    if json_path is not None:
        with open(json_path) as j_file:
            team_dict = json.load(j_file)
    elif team_dict is None:
        with open('Data/JSON/Public_NBA_API/teams.json') as j_file:
            team_dict = json.load(j_file)

    for team in team_dict:
        if team['abbreviation'] == team_code:
            return team['slug']

    raise ValueError('no matching team for abbreviation')

def fanduelOdds():
    # https://sportsbook.fanduel.com/cache/psevent/UK/1/false/958472.3.json
    pass

def bovadaOdds():
    # https://widgets.digitalsportstech.com/api/gp?sb=bovada&tz=-5&gameId=in,135430
    # above requires game ids as input but returns odds

    # https://widgets.digitalsportstech.com/?sb=bovada&language=en&oddsType=american&currency=usd&leagueId=123&preMatchOnly=true
    # Above gets game ids in a .js

    soup = getSoupFromUrl('https://widgets.digitalsportstech.com/?sb=bovada&language=en&oddsType=american&currency=usd&leagueId=123&preMatchOnly=true')
    gameIdString = soup.find('script').contents[0]

    uniqueIds = set()
    allGameIds = re.findall(r'(?<="id":)([0-9]{6}?)(?=,)', gameIdString)

    for id in allGameIds:
        uniqueIds.add(id)

    url = 'https://widgets.digitalsportstech.com/api/gp?sb=bovada&tz=-5&gameId=in'
    for id in uniqueIds:
        url += ',' + str(id)

    allBets = requests.get(url).json()
    scoreFirstBets = list()
    for bet in allBets:
        print(bet['queryTitle'])
        if bet['queryTitle'].lower() == 'team to score first':
            scoreFirstBets.append(bet)
    return scoreFirstBets # todo this only seems to return half of the bets, in decimal odds and needs to be complete to format the bets

def draftKingsOdds():
    # https://sportsbook.draftkings.com/leagues/basketball/103?category=game-props&subcategory=odd/even
    # API - https://sportsbook.draftkings.com//sites/US-SB/api/v1/eventgroup/103/full?includePromotions=true&format=json
    allBets = requests.get('https://sportsbook.draftkings.com//sites/US-SB/api/v1/eventgroup/103/full?includePromotions=true&format=json').json()
    offerCategories = allBets['eventGroup']['offerCategories']

    for category in offerCategories:
        if category['name'] == "Game Props":
           gameProps = category['offerSubcategoryDescriptors']
        # if category['name'] == "Player Props":
        #     playerProps = category['offerSubcategoryDescriptors']

    for subCategory in gameProps:
        if subCategory['name'] == "First Team to Score":
            firstTeamToScoreLines = subCategory['offerSubcategory']['offers']
            break

    # for subCategory in playerProps:
    #     if subCategory['name'] == "First Field Goal": #todo an id may work for these
    #         firstPlayerToScoreLines = subCategory['offerSubcategory']['offers']
    #         break

    allTeamLines = list()
    for teamLine in firstTeamToScoreLines:
        outcomes = teamLine[0]['outcomes']
        team1 = outcomes[0]['label']
        team1Odds = outcomes[0]['oddsAmerican']
        team2 = outcomes[1]['label']
        team2Odds = outcomes[1]['oddsAmerican']
        allTeamLines.append({team1: team1Odds, team2: team2Odds})

    # allPlayerLines = list()
    # for allPlayerLinesForGame in firstPlayerToScoreLines:
    #     gamePlayerLines = allPlayerLinesForGame[0]['outcomes']
    #     for playerLine in gamePlayerLines:
    #         name = playerLine['label']
    #         aOdds = playerLine['oddsAmerican']
    #         # playerTeam = getPlayerTeamFromFullName(name)
    #         allPlayerLines.append({name: aOdds}) #, "possibleTeams": playerTeam})

    return allTeamLines #, allPlayerLines

def betNowOdds():
    # https://www.betnow.eu/nba/ says it has props bets
    # this needs to be verified
    pass

def mgmOdds():
    # https://sports.co.betmgm.com/en/sports/events/minnesota-timberwolves-at-san-antonio-spurs-11101908?market=10000
    url = "https://cds-api.co.betmgm.com/bettingoffer/fixtures?x-bwin-accessid=OTU4NDk3MzEtOTAyNS00MjQzLWIxNWEtNTI2MjdhNWM3Zjk3&lang=en-us&country=US&userCountry=US&subdivision=Texas&fixtureTypes=Standard&state=Latest&offerMapping=Filtered&offerCategories=Gridable&fixtureCategories=Gridable,NonGridable,Other&sportIds=7&regionIds=9&competitionIds=6004&skip=0&take=50&sortBy=Tags"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'}
    response = requests.get(url, headers=headers)

    betmgmGames = json.loads(response.text)['fixtures']
    gameIDs = []
    for game in betmgmGames:
        if (game['stage'] == "PreMatch"):
            gameIDs.append(game['id'])

    sleepCounter = 0
    allTeamLines = list()
    for index in range(len(gameIDs)):
        gameURL = "https://cds-api.co.betmgm.com/bettingoffer/fixture-view?x-bwin-accessid=OTU4NDk3MzEtOTAyNS00MjQzLWIxNWEtNTI2MjdhNWM3Zjk3&lang=en-us&country=US&userCountry=US&subdivision=Texas&offerMapping=All&fixtureIds=" + \
                  gameIDs[index]
        gameResponse = requests.get(gameURL, headers=headers)
        oddsInfo = json.loads(gameResponse.text)['fixture']['games']
        sleepChecker(sleepCounter, iterations=1, printStop=True)
        for odds in oddsInfo:
            if (odds['name']['value'] == "Which team will score the first points?"):
                t1Name = odds['results'][0]['name']['value']
                t1Odds = odds['results'][0]['americanOdds']
                t2Name = odds['results'][1]['name']['value']
                t2Odds = odds['results'][1]['americanOdds']
                allTeamLines.append({t1Name: t1Odds, t2Name: t2Odds})

    return allTeamLines

def pointsBet():
    # https://nj.pointsbet.com/sports/basketball/NBA/246723
    # request for all things that are on the page - https://api-usa.pointsbet.com/api/v2/competitions/105/events/featured?includeLive=false&page=1
    # single game - https://api-usa.pointsbet.com/api/v2/events/249073
    pass

def sugarHouseOdds():
    # https://www.playsugarhouse.com/?page=sports#event/1007123701
    # this is a mirror of pointsbets for specific geos, so backlogged
    pass

def betRiversOdds():
    # find the url
    pass

def unibetOdds():
    # https://nj.unibet.com/sports/#event/1007123701
    pass

def barstoolOdds():
    # https://www.barstoolsportsbook.com/sports/basketball/nba
    # all events https://eu-offering.kambicdn.org/offering/v2018/pivuspa/listView/basketball/nba/all/all/matches.json?includeParticipants=true&useCombined=true&lang=en_US&market=US
    # odds lines single game - https://api.barstoolsportsbook.com/offerings/grouped_event/1007161722/pre_match_event/?lang=en_US&market=US
    pass

# Other bookmakers https://the-odds-api.com/sports-odds-data/bookmaker-apis.html


# def betfair_odds():
#     # https://www.betfair.com/sport/basketball/nba/houston-rockets-oklahoma-city-thunder/30266729
#     # these are not american odds so will need some new methods for these
#     pass

def getStarters(team_code: str, team_dict: dict=None):
    full_name = teamCodeToSlugName(team_code, team_dict)

    url = 'https://api.lineups.com/nba/fetch/lineups/current/{}'.format(full_name)
    response = requests.get(url).json()
    starters = response['starters']

    starters_list = list()
    for player in starters:
        starters_list.append([player['name'], player['position']])

    date = response['nav']['matchup_day']
    confirmed = 'lineup confirmed for'
    if not response['nav']['lineup_confirmed']:
        confirmed = 'LINEUP NOT YET CONFIRMED for'

    def sortFn(e):
        return e[1]

    starters_list.sort(key=sortFn)
    print(confirmed, date + '.', 'Starters for', team_code, 'are', starters_list)
    return starters_list

def tipperFromTeam(teamShort: str):
    with open('Data/JSON/team_tipper_pairs.json') as file:
        dict = json.load(file)
    for row in dict["pairs"]:
        if teamShort == row["team"]:
            return row["playerCode"]

def getAllExpectedStarters():
    teamList = ['NOP', 'IND', 'CHI', 'ORL', 'TOR', 'BKN', 'MIL', 'CLE', 'CHA', 'WAS', 'MIA', 'OKC', 'MIN', 'DET', 'PHX',
                'BOS', 'LAC', 'SAS', 'GSW', 'DAL', 'UTA', 'ATL', 'POR', 'PHI', 'HOU', 'MEM', 'DEN', 'LAL', 'SAC']
    sleepCounter = 0
    for team in teamList:
        sleepChecker(sleepCounter, iterations=5, baseTime=1, randomMultiplier=1)
        getStarters(team)

def getDailyOdds(t1: str, t2: str, aOdds: str = '-110', exchange: str ='Fanduel'):
    p1 = tipperFromTeam(t1)
    p2 = tipperFromTeam(t2)
    odds1 = checkEvPlayerCodesOddsLine(aOdds, p1, p2)
    odds2 = checkEvPlayerCodesOddsLine(aOdds, p2, p1)
    t1FullName = getTeamFullFromShort(t1)
    t2FullName = getTeamFullFromShort(t2)
    print('On', exchange, 'bet', kellyBetFromAOddsAndScoreProb(odds1, aOdds, bankroll=ENVIRONMENT.BANKROLL), 'on', t1FullName, 'assuming odds', str(aOdds))
    print('On', exchange, 'bet', kellyBetFromAOddsAndScoreProb(odds2, aOdds, bankroll=ENVIRONMENT.BANKROLL), 'on', t2FullName, 'assuming odds', str(aOdds))
    print()

# test = bovadaOdds()
# print(test)
# print()