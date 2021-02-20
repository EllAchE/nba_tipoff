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
from src.functions.database_access import getUniversalShortCode, getCurrentPlayerTeam
from src.functions.odds_calculator import checkEvPlayerCodesOddsLine, kellyBetFromAOddsAndScoreProb, decimalToAmerican
from src.functions.utils import getTeamFullFromShort, getSoupFromUrl, sleepChecker
# todo add a threshold of ev factor to only take safer bets


def formatUnknownTeamPlayerLines(rawPlayerLines, homeShortCode=None, awayShortCode=None):
    if len(rawPlayerLines) != 10:
        raise ValueError("Must have exactly ten players right now")

    home = []
    away = []
    for player in rawPlayerLines:
        teamShortCode = getCurrentPlayerTeam(player['name'])
        if teamShortCode == homeShortCode:
            home.append({"name": player['name'], "odds": player["odds"], "team": homeShortCode})
        elif teamShortCode == awayShortCode:
            away.append({"name": player['name'], "odds": player["odds"], "team": homeShortCode})
        else:
            raise ValueError("No match for either team", homeShortCode, awayShortCode, "for player", player)

    return home, away

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
    # Rohit has this partly in typescript already
    pass

def bovadaOdds():
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
    scoreFirstBetsSingleTeam = list()
    for bet in allBets:
        print(bet['queryTitle'])
        if bet['queryTitle'].lower() == 'team to score first':
            shortTitle = bet['game']['shortTitle']
            team1Id = bet['game']['team1Id']
            team2Id = bet['game']['team2Id']
            decimalOdds = bet['odds']
            scoreFirstBetsSingleTeam.append({
                "shortTitle": shortTitle,
                "team1id": team1Id,
                "team2id": team2Id,
                "decimalOdds": decimalOdds
            })
    matchedBets = set()

    scoreFirstBetsBothTeams = list()
    for bet in scoreFirstBetsSingleTeam:
        if bet['shortTitle'] not in matchedBets:
            for potentialPair in scoreFirstBetsSingleTeam:
                if potentialPair['shortTitle'] == bet['shortTitle']:
                    matchedBets.add(potentialPair['shortTitle'])
                    shortTitle = bet['shortTitle']
                    team1Id = bet['team1Id']
                    team2Id = bet['team2Id']
                    # todo bovada has player spreads as well, seemingly for games lacking team props

                    scoreFirstBetsBothTeams.append({
                        "shortTitle": shortTitle,
                        "team1Id": team1Id,
                        "team2Id": team2Id,
                        "team1Odds": bet['decimalOdds'],
                        "team2Odds": potentialPair['decimalOdds'],
                    })
                    break

    scoreFirstBetsBothTeamsFormatted = list()
    for item in scoreFirstBetsBothTeams:
        scoreFirstBetsBothTeamsFormatted.append({
            'exchange': 'bovada',
            "home": getUniversalShortCode(item['team1Id']),
            "away": getUniversalShortCode(item['team2Id']),
            "homeTeamFirstQuarterOdds": decimalToAmerican(item['team1Odds']),
            "awayTeamFirstQuarterOdds": decimalToAmerican(item['team2Odds'])
        })

    return scoreFirstBetsBothTeamsFormatted # todo LEFTOFF
            #todo this is just taking a guess at which odds belong to which team assuming second odds for team2

def draftKingsOdds():
    # https://sportsbook.draftkings.com/leagues/basketball/103?category=game-props&subcategory=odd/even
    # API - https://sportsbook.draftkings.com//sites/US-SB/api/v1/eventgroup/103/full?includePromotions=true&format=json
    allBets = requests.get('https://sportsbook.draftkings.com//sites/US-SB/api/v1/eventgroup/103/full?includePromotions=true&format=json').json()
    offerCategories = allBets['eventGroup']['offerCategories']

    for category in offerCategories:
        if category['name'] == "Game Props":
           gameProps = category['offerSubcategoryDescriptors']
        if category['name'] == "Player Props":
            playerProps = category['offerSubcategoryDescriptors']

    for subCategory in gameProps:
        if subCategory['name'] == "First Team to Score":
            firstTeamToScoreLines = subCategory['offerSubcategory']['offers']
            break

    for subCategory in playerProps:
        if subCategory['name'] == "First Field Goal": #todo an id may work for these
            firstPlayerToScoreLines = subCategory['offerSubcategory']['offers']
            break

    allTeamLines = list()
    for teamLine in firstTeamToScoreLines:
        outcomes = teamLine[0]['outcomes']
        team1 = outcomes[0]['label']
        team1Odds = outcomes[0]['oddsAmerican']
        team2 = outcomes[1]['label']
        team2Odds = outcomes[1]['oddsAmerican']
        allTeamLines.append({
            "exchange": "draftkings",
            "home": getUniversalShortCode(team1),
            "away": getUniversalShortCode(team2),
            "homeTeamFirstQuarterOdds": team1Odds,
            "awayTeamFirstQuarterOdds": team2Odds,
            "homePlayerFirstQuarterOdds": [],
            "awayPlayerFirstQuarterOdds": []
        })

    rawPlayerLines = list()
    for playerLine in firstPlayerToScoreLines:
        outcomes = playerLine[0]['outcomes']
        rawPlayerLines.append({
            "player": outcomes[0]['label'],
            "odds": outcomes[0]['oddsAmerican']
        })

    for rawLine in rawPlayerLines:
        homePlayerLines, awayPlayerLines = formatUnknownTeamPlayerLines(rawLine)
        for teamLine in allTeamLines:
            if teamLine['home'] == homePlayerLines[0]['team']:
                teamLine['homePlayerFirstQuarterOdds'] = teamLine['homePlayerFirstQuarterOdds'].append(rawLine['odds'])
            elif teamLine['away'] == awayPlayerLines[0]['team']:
                teamLine['awayPlayerFirstQuarterOdds'] = teamLine['awayPlayerFirstQuarterOdds'].append(rawLine['odds'])
    return allTeamLines, rawPlayerLines

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

    allGameLines = list()
    for index in range(len(gameIDs)):
        gameURL = "https://cds-api.co.betmgm.com/bettingoffer/fixture-view?x-bwin-accessid=OTU4NDk3MzEtOTAyNS00MjQzLWIxNWEtNTI2MjdhNWM3Zjk3&lang=en-us&country=US&userCountry=US&subdivision=Texas&offerMapping=All&fixtureIds=" + \
                  gameIDs[index]
        gameResponse = requests.get(gameURL, headers=headers)
        oddsInfo = json.loads(gameResponse.text)['fixture']['games']
        sleepChecker(iterations=1, printStop=True)
        for odds in oddsInfo:
            if (odds['name']['value'] == "Which team will score the first points?"):
                team1 = odds['results'][0]['name']['value']
                team1Odds = odds['results'][0]['americanOdds']
                team2 = odds['results'][1]['name']['value']
                team2Odds = odds['results'][1]['americanOdds']
                allGameLines.append({
                    'exchange': 'mgm',
                    "home": getUniversalShortCode(team1),
                    "away": getUniversalShortCode(team2),
                    "homeTeamFirstQuarterOdds": team1Odds,
                    "awayTeamFirstQuarterOdds": team2Odds
                })
    return allGameLines

# def pointsBet():
#     # https://nj.pointsbet.com/sports/basketball/NBA/246723
#     # request for all things that are on the page - https://api-usa.pointsbet.com/api/v2/competitions/105/events/featured?includeLive=false&page=1
#     # single game - https://api-usa.pointsbet.com/api/v2/events/249073
#
#     allGamesUrl = 'https://api-usa.pointsbet.com/api/v2/competitions/105/events/featured?includeLive=false&page=1'
#     allGames = requests.get(allGamesUrl).json()
#
#     for eventId in eventIdList:
#         singleGameUrl = 'https://api-usa.pointsbet.com/api/v2/events/{}'.format(eventId)
#
#     pass

def unibetOdds():
    # https://nj.unibet.com/sports/#event/1007123701
    # single game https://eu-offering.kambicdn.org/offering/v2018/ubusnj/betoffer/event/1007123785.json?lang=en_US&market=US&client_id=2&channel_id=1&ncid=1613612842277&includeParticipants=true
    # all games https://eu-offering.kambicdn.org/offering/v2018/ubusnj/listView/basketball/nba.json?lang=en_US&market=US&client_id=2&channel_id=1&ncid=1613612828579&useCombined=true
    allGamesUrl = 'https://eu-offering.kambicdn.org/offering/v2018/ubusnj/listView/basketball/nba.json?lang=en_US&market=US&client_id=2&channel_id=1&ncid=1613612828579&useCombined=true'
    allEventsResponse = requests.get(allGamesUrl).json()

    eventsList = list()

    for event in allEventsResponse['events']:
        event = event['event']
        eventsList.append([event['id'], event['start'], event['homeName'], event['awayName']])

    singleEventUrlStub = 'https://eu-offering.kambicdn.org/offering/v2018/ubusnj/betoffer/event/{}.json?lang=en_US&market=US&client_id=2&channel_id=1&ncid=1613612842277&includeParticipants=true'

    gameDetailsList = list()
    for event in eventsList:
        sleepChecker(baseTime=0.5, randomMultiplier=2)
        singleGameResponse = requests.get(singleEventUrlStub.format(str(event[0]))).json()
        mostPopular = singleGameResponse[1]
        allMPBets = mostPopular['criterion']
        playerScoreFirstFG = None

        for bet in allMPBets:
            if bet['label'] == "Player to Score the First Field Goal of the Game":
                playerScoreFirstFG = bet
                break
        if playerScoreFirstFG is None:
            raise ValueError("No bet found in unibet for player to score first field goal")

        lines = playerScoreFirstFG['offers'][0]['outcomes']
        playerLinesList = list()
        for playerLine in lines:
            aOdds = playerLine['oddAmerican']
            pName = playerLine['label']
            playerId = playerLine['participantId']
            playerLinesList.append({'name': pName, 'odds': aOdds, 'playerId': playerId})

        homePlayerLines, awayPlayerLines = formatUnknownTeamPlayerLines(playerLinesList)

        gameDetailsList.append({
            'exchange': 'unitbet',
            'startDatetime': event['startDatetime'],
            'home': event['home'],
            'away': event['away'],
            'homePlayerOdds': homePlayerLines,
            'awayPlayerOdds': awayPlayerLines
        })
    return gameDetailsList
    #todo this has a lot of duplication with the barstool method so would be worth extracting


def barstoolOdds(): #only has player prosp to score (first field goal)
    # https://www.barstoolsportsbook.com/sports/basketball/nba
    # all events https://eu-offering.kambicdn.org/offering/v2018/pivuspa/listView/basketball/nba/all/all/matches.json?includeParticipants=true&useCombined=true&lang=en_US&market=US
    # odds lines single game - https://api.barstoolsportsbook.com/offerings/grouped_event/1007161722/pre_match_event/?lang=en_US&market=US
    allEventsUrl = 'https://eu-offering.kambicdn.org/offering/v2018/pivuspa/listView/basketball/nba/all/all/matches.json?includeParticipants=true&useCombined=true&lang=en_US&market=US'
    allEventsResponse = requests.get(allEventsUrl).json()
    eventsList = list()

    for event in allEventsResponse['events']:
        event = event['event']
        eventsList.append({"id": event['id'], "startDatetime": event['start'], "home": event['homeName'], "away": event['awayName']})

    singleEventUrlStub = 'https://api.barstoolsportsbook.com/offerings/grouped_event/{}/pre_match_event/?lang=en_US&market=US'

    gameDetailsList = list()
    for event in eventsList:
        sleepChecker(baseTime=0.5, randomMultiplier=2)
        singleGameResponse = requests.get(singleEventUrlStub.format(event['id']), headers={"consumer":"www"}).json()
        mostPopular = singleGameResponse[1]
        allMPBets = mostPopular['criterion']
        playerScoreFirstFG = None

        for bet in allMPBets:
            if bet['label'] == "Player to Score the First Field Goal of the Game":
                playerScoreFirstFG = bet
                break
        if playerScoreFirstFG is None:
            raise ValueError("No bet found in barstool for player to score first field goal")

        lines = playerScoreFirstFG['offers'][0]['outcomes']
        playerLinesList = list()
        for playerLine in lines:
            aOdds = playerLine['oddAmerican']
            pName = playerLine['label']
            playerId = playerLine['participantId']
            playerLinesList.append({'name': pName, 'odds': aOdds, 'playerId': playerId})

        homePlayerLines, awayPlayerLines = formatUnknownTeamPlayerLines(playerLinesList)

        gameDetailsList.append({
            'exchange': 'barstool',
            'startDatetime': event['startDatetime'],
            'home': event['home'],
            'away': event['away'],
            'homePlayerOdds': homePlayerLines,
            'awayPlayerOdds': awayPlayerLines
        })
    return gameDetailsList

# Other bookmakers https://the-odds-api.com/sports-odds-data/bookmaker-apis.html

# def betfair_odds():
#     # https://www.betfair.com/sport/basketball/nba/houston-rockets-oklahoma-city-thunder/30266729
#     # these are not american odds so will need some new methods for these
#     # betfair homepage https://www.betfair.com/sport/basketball
#     # betfair single game page https://www.betfair.com/sport/basketball/nba/miami-heat-golden-state-warriors/30289841
#     # betfair odds retrieval - have a curl request that gets them based on ids from an api endpoint, however doing so is pointless
# as you need to scrape the page to get the ids anyways (at least as far as I know)
#     pass

# def sugarHouseOdds():
#     # https://www.playsugarhouse.com/?page=sports#event/1007123701
#     # this is a mirror of pointsbets for specific geos, so backlogged
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
    for team in teamList:
        sleepChecker(iterations=5, baseTime=1, randomMultiplier=1)
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


def createTeamTipperDict():
    teamList = ['NOP', 'IND', 'CHI', 'ORL', 'TOR', 'BKN', 'MIL', 'CLE', 'CHA', 'WAS', 'MIA', 'OKC', 'MIN', 'DET', 'PHX',
                'BOS', 'LAC', 'SAS', 'GSW', 'DAL', 'UTA', 'ATL', 'POR', 'PHI', 'HOU', 'MEM', 'DEN', 'LAL', 'SAC']
    teamList.sort()
    startersList = list()
    tipperList = list()
    fullJson = {}

    for teamLine in teamList:
        startersList.append({"starters": getStarters(teamLine), "team": teamLine})
        sleepChecker(printStop=False)

    for teamLine in startersList:
        player = teamLine["starters"][0]
        nameList = player[0].split(' ')
        lcode = ''
        i = 0
        while i < 5:
            try:
                lcode += nameList[1][i]
                i += 1
            except:
                break
        code = lcode + nameList[0][:2] + '01.html'
        code = code.lower()

        tipperList.append({"playerCode":code, "team": teamLine["team"]})
    fullJson["pairs"] = tipperList

    with open ('Data/JSON/team_tipper_pairs.json', 'w') as file:
        json.dump(fullJson, file)
