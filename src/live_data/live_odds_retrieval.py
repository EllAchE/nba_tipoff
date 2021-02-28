# Places to retrieve live lineups
# https://www.rotowire.com/basketball/nba-lineups.php
# https://www.nba.com/players/todays-lineups
# stats api here - https://stats.nba.com/js/data/leaders/00_active_starters_20210128.json
# todo get live

import json
import re

import requests
import pandas as pd

import ENVIRONMENT
from src.functions.database_access import getUniversalShortCode, getPlayerCurrentTeam, getUniversalPlayerName
from src.functions.odds_calculator import checkEvPlayerCodesOddsLine, kellyBetFromAOddsAndScoreProb, decimalToAmerican
from src.functions.utils import getTeamFullFromShort, getSoupFromUrl, sleepChecker


def addTeamToUnknownPlayerLine(rawPlayerLine):
    formattedPlayerName = getUniversalPlayerName(rawPlayerLine['player'])
    teamShortCodeBballRefFormat = getPlayerCurrentTeam(formattedPlayerName)
    teamShortCode = getUniversalShortCode(teamShortCodeBballRefFormat)

    rawPlayerLine['team'] = teamShortCode

    return rawPlayerLine

def getExpectedTipper(team):
    if len(team) != 3:
        raise ValueError('Need to pass universal team short code to getExpectedTipper')

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

def bovadaTeamOdds(allTeamBets):
    scoreFirstBetsSingleTeam = list()
    gameIdSet = set()
    customId = 0
    for bet in allTeamBets:
        gameIdSet.add(bet['game']['id'])
        if bet['queryTitle'].lower() == 'team to score first':
            shortTitle = bet['game']['shortTitle']
            team1Id = bet['game']['team1Id']
            team2Id = bet['game']['team2Id']
            if bet['oddsOverride'] is not None:
                decimalOdds = bet['oddsOverride']
            else:
                decimalOdds = bet['odds']
            scoreFirstBetsSingleTeam.append({
                "shortTitle": shortTitle,
                "team1id": str(team1Id),
                "team2id": str(team2Id),
                "decimalOdds": decimalOdds,
                "customId": customId
            })
            customId += 1
    matchedBets = set()

    scoreFirstBetsBothTeams = list()
    for bet in scoreFirstBetsSingleTeam:
        if bet['shortTitle'] not in matchedBets:
            for potentialPair in scoreFirstBetsSingleTeam:
                if potentialPair['shortTitle'] == bet['shortTitle'] and potentialPair['customId'] != bet['customId']:
                    matchedBets.add(potentialPair['shortTitle'])
                    shortTitle = bet['shortTitle']
                    team1Id = bet['team1id']
                    team2Id = bet['team2id']

                    # This implicitly relies on team1 being the first one on the list
                    scoreFirstBetsBothTeams.append({
                        "shortTitle": shortTitle,
                        "team1id": team1Id,
                        "team2id": team2Id,
                        "team1Odds": potentialPair['decimalOdds'],
                        "team2Odds": bet['decimalOdds'],
                    })
                    break

    scoreFirstBetsBothTeamsFormatted = list()
    for item in scoreFirstBetsBothTeams:
        scoreFirstBetsBothTeamsFormatted.append({
            'exchange': 'bovada',
            "shortTitle": item['shortTitle'],
            "away": getUniversalShortCode(item['team2id']),
            "home": getUniversalShortCode(item['team1id']),
            "awayTeamFirstQuarterOdds": decimalToAmerican(item['team2Odds']),
            "homeTeamFirstQuarterOdds": decimalToAmerican(item['team1Odds']),
            "awayPlayerFirstQuarterOdds": [],
            "homePlayerFirstQuarterOdds": []
        })
        scoreFirstBetsBothTeamsFormatted.append({
            'exchange': 'bovada',
            "away": getUniversalShortCode(item['team1id']),
            "home": getUniversalShortCode(item['team2id']),
            "shortTitle": item['shortTitle'],
            "awayTeamFirstQuarterOdds": decimalToAmerican(item['team2Odds']),
            "homeTeamFirstQuarterOdds": decimalToAmerican(item['team1Odds']),
            "awayPlayerFirstQuarterOdds": [],
            "homePlayerFirstQuarterOdds": []
        })  # This is done as it is unknown for bovada whic hteam belongs to which odds

    return scoreFirstBetsBothTeamsFormatted, gameIdSet

# todo get bovada player spreads
def bovadaPlayerOdds(playerBetGamesList):
    playerTeamDict = {}
    match = False
    for game in playerBetGamesList:
        for betCategory in game:
            if betCategory['settings']['title'] == "First Point":
                match = True
                selections = betCategory['selections']
                break

        if match:
            match = False
            shortTitle = betCategory['settings']['games'][0]['shortTitle']
            homeShort = shortTitle.split()[-1]
            awayShort = shortTitle.split()[0]
            homePlayerOdds = list()
            awayPlayerOdds = list()

            for player in selections:
                actualOdds = player['odds'] if player['oddsOverride'] is None else player['oddsOverride']
                if player['player']['team']['abbreviation'] == homeShort:
                    homePlayerOdds.append({
                        "player": player['player']['name'],
                        "odds": actualOdds,
                        "team": getUniversalShortCode(homeShort)
                    })
                elif player['player']['team']['abbreviation'] == awayShort:
                    awayPlayerOdds.append({
                        "player": player['player']['name'],
                        "odds": actualOdds,
                        "team": getUniversalShortCode(awayShort)
                    })
                else:
                    raise ValueError("Bovada misformattted something in player and team codes")

            playerTeamDict[homePlayerOdds[0]['team']] = homePlayerOdds
            playerTeamDict[awayPlayerOdds[0]['team']] = awayPlayerOdds

    return playerTeamDict


# backlogtodo these could have the wrong odds on the wrong team, so currently add two versions. Fix this
def bovadaOdds():
    soup = getSoupFromUrl('https://widgets.digitalsportstech.com/?sb=bovada&language=en&oddsType=american&currency=usd&leagueId=123&preMatchOnly=true&liveOnly=true')
    gameIdString = soup.find('script').contents[0]

    uniqueIds = set()
    allGameIds = re.findall(r'(?<="id":)([0-9]{6}?)(?=,)', gameIdString)

    for id in allGameIds:
        uniqueIds.add(id)

    teamBetUrl = 'https://widgets.digitalsportstech.com/api/gp?sb=bovada&tz=-5&preMatchOnly=true&liveOnly=true&gameId=in'
    for id in uniqueIds:
        teamBetUrl += ',' + str(id)
    allTeamBets = requests.get(teamBetUrl).json()

    scoreFirstBetsBothTeamsFormatted, gameIdSet = bovadaTeamOdds(allTeamBets)

#todo fix this to account for vames that don't yet matter

    playerBetUrlStub = 'https://widgets.digitalsportstech.com/api/custom-markets?sb=bovada&tz=-5&gameId='
    playerBetGames = list()
    for id in gameIdSet:
        playerBetGame = requests.get(playerBetUrlStub + str(id)).json()
        playerBetGames.append(playerBetGame)

    scoreFirstBetsAllPlayersDict = bovadaPlayerOdds(playerBetGames)

    for gameLine in scoreFirstBetsBothTeamsFormatted:
        try:
            gameLine["homePlayerFirstQuarterOdds"] = scoreFirstBetsAllPlayersDict[gameLine["home"]]
            gameLine["awayPlayerFirstQuarterOdds"] = scoreFirstBetsAllPlayersDict[gameLine["away"]]
        except:
            print("no player lines found for game", gameLine)

    return scoreFirstBetsBothTeamsFormatted

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

    teamMatch = False
    playerMatch = False
    for subCategory in gameProps:
        if subCategory['name'] == "First Team to Score":
            firstTeamToScoreLines = subCategory['offerSubcategory']['offers']
            teamMatch = True
            break

    for subCategory in playerProps:
        if subCategory['name'] == "First Field Goal":
            firstPlayerToScoreLines = subCategory['offerSubcategory']['offers']
            playerMatch = True
            break

    if not playerMatch:
        print('No player odds for draftkings currently')
    if not teamMatch:
        print('No team odds for draftkings currently')

    teamSet = set()
    allGameLines = list()
    if teamMatch:
        for teamLine in firstTeamToScoreLines:
            outcomes = teamLine[0]['outcomes']
            team1 = getUniversalShortCode(outcomes[0]['label'])
            team1Odds = outcomes[0]['oddsAmerican']
            team2 = getUniversalShortCode(outcomes[1]['label'])
            team2Odds = outcomes[1]['oddsAmerican']
            teamSet.add(team2)
            teamSet.add(team1)

            allGameLines.append({
                "exchange": "draftkings",
                "home": team1,
                "away": team2,
                "homeTeamFirstQuarterOdds": str(team1Odds),
                "awayTeamFirstQuarterOdds": str(team2Odds),
                "homePlayerFirstQuarterOdds": [],
                "awayPlayerFirstQuarterOdds": []
            })

    rawPlayerLines = list()
    if playerMatch:
        for game in firstPlayerToScoreLines:
            outcomes = game[0]['outcomes']
            for playerOdds in outcomes:
                rawPlayerLines.append({
                    "player": playerOdds['label'],
                    "odds": playerOdds['oddsAmerican']
                })

    playerTeamDict = {}
    for team in teamSet:
        playerTeamDict[team] = []
    for rawLine in rawPlayerLines:
        playerLine = addTeamToUnknownPlayerLine(rawLine)
        playerTeamDict[playerLine['team']] += [playerLine]

    for gameLine in allGameLines:
        gameLine["homePlayerFirstQuarterOdds"] = playerTeamDict[gameLine["home"]]
        gameLine["awayPlayerFirstQuarterOdds"] = playerTeamDict[gameLine["away"]]

    return allGameLines

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

                if team1Odds > 0:
                    team1Odds = '+' + str(team1Odds)
                else:
                    team1Odds = str(team1Odds)
                team2 = odds['results'][1]['name']['value']
                team2Odds = odds['results'][1]['americanOdds']
                if team2Odds > 0:
                    team2Odds = '+' + str(team1Odds)
                else:
                    team2Odds = str(team2Odds)

                allGameLines.append({
                    'exchange': 'mgm',
                    "home": getUniversalShortCode(team2),
                    "away": getUniversalShortCode(team1),
                    "homeTeamFirstQuarterOdds": str(team2Odds),
                    "awayTeamFirstQuarterOdds": str(team1Odds)
                })
    return allGameLines

# backlogtodo figure out the math on pointsbets accelerators etc. (seem not worth)
# backlogtodo add accelerators maybe
def pointsBetOdds():
    # https://nj.pointsbet.com/sports/basketball/NBA/246723
    # request for all things that are on the page - https://api-usa.pointsbet.com/api/v2/competitions/105/events/featured?includeLive=false&page=1
    # single game - https://api-usa.pointsbet.com/api/v2/events/249073

    allGamesUrl = 'https://api-usa.pointsbet.com/api/v2/competitions/105/events/featured?includeLive=false&page=1'
    allGames = requests.get(allGamesUrl).json()

    gameDictList = list()
    for event in allGames['events']:
        rawPlayerLines = list()
        eventId = event['key']
        homeTeam = getUniversalShortCode(event['homeTeam'])
        awayTeam = getUniversalShortCode(event['awayTeam'])
        singleGameUrl = 'https://api-usa.pointsbet.com/api/v2/events/{}'.format(eventId)
        singleGameResponse = requests.get(singleGameUrl).json()

        # assumes just a single game
        for market in singleGameResponse['fixedOddsMarkets']:
            if market['eventName'] == "First Basket":
                firstBasketMarket = market
                for outcome in firstBasketMarket['outcomes']:
                    rawPlayerLines.append({
                        "player": outcome['name'],
                        "teamId": outcome['teamId'],
                        "odds": '+' + str(outcome['price'] * 100 - 100) #todo confirm this needs the -100
                    })

                homePlayerList = list()
                awayPlayerList = list()
                for player in rawPlayerLines:
                    universalName = getUniversalPlayerName(player['player'])
                    player['team'] = getUniversalShortCode(getPlayerCurrentTeam(universalName))
                    if player['team'] == homeTeam:
                        homePlayerList.append(player)
                    elif player['team'] == awayTeam:
                        awayPlayerList.append(player)
                    else:
                        raise ValueError("player didn't match either team, or teams are misformatted/don't match universal team code", player)

                gameDictList.append({
                    'exchange': 'pointsBet',
                    "home": homeTeam,
                    "away": awayTeam,
                    "isFirstFieldGoal": True,
                    "homePlayerFirstQuarterOdds": homePlayerList,
                    "awayPlayerFirstQuarterOdds": awayPlayerList
                })
            else:
                # print("no first basket market found for game", awayTeam, "@", homeTeam)
                pass

    return gameDictList

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
        sleepChecker(baseTime=0.5, randomMultiplier=3)
        singleGameResponse = requests.get(singleEventUrlStub.format(str(event[0]))).json()
        allBets = singleGameResponse['betOffers']
        homeTeam = getUniversalShortCode(event[2])
        awayTeam = getUniversalShortCode(event[3])

        playerScoreFirstFG = None
        for bet in allBets:
            if bet['criterion']['label'] == "Player to Score the First Field Goal of the Game":
                playerScoreFirstFG = bet
                break
        if playerScoreFirstFG is None:
            print("No bet found in unibet for player to score first field goal for event", event)
            continue

        lines = playerScoreFirstFG['outcomes']
        rawPlayerLines = list()
        for playerLine in lines:
            aOdds = '+' + playerLine['oddsAmerican']
            pName = playerLine['label']
            playerId = playerLine['participantId']
            rawPlayerLines.append({'player': pName, 'odds': aOdds, 'playerId': playerId})

        homePlayerLines = list()
        awayPlayerLines = list()
        for player in rawPlayerLines:
            universalName = getUniversalPlayerName(player['player'])
            player['team'] = getUniversalShortCode(getPlayerCurrentTeam(universalName))
            if player['team'] == homeTeam:
                homePlayerLines.append(player)
            elif player['team'] == awayTeam:
                awayPlayerLines.append(player)
            else:
                raise ValueError(
                    "player didn't match either team, or teams are misformatted/don't match universal team code",
                    player)

        gameDetailsList.append({
            'exchange': 'unibet',
            "isFirstFieldGoal": True,
            'home': homeTeam,
            'away': awayTeam,
            'homePlayerFirstQuarterOdds': homePlayerLines,
            'awayPlayerFirstQuarterOdds': awayPlayerLines
        })
    return gameDetailsList
    # backlogtodo this has a lot of duplication with the barstool method so would be worth extracting


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

    # todo see if this needs optimization, may be duplciate values with unibet
    gameDetailsList = list()
    for event in eventsList:
        sleepChecker(baseTime=0.5, randomMultiplier=2)
        singleGameResponse = requests.get(singleEventUrlStub.format(event['id']), headers={"consumer":"www"}).json()
        homeTeam = getUniversalShortCode(event['home'])
        awayTeam = getUniversalShortCode(event['away'])

        hasPlayerSpecials = False
        for category in singleGameResponse:
            if category['name'] == "Player Specials":
                hasPlayerSpecials = True
                break
        if not hasPlayerSpecials:
            continue

        betOptions = category['criterion']

        hasFirstFieldGoal = False
        for option in betOptions:
            if option['label'] == "Player to Score the First Field Goal of the Game":
                hasFirstFieldGoal = True
                break
        if not hasFirstFieldGoal:
            continue

        allOffers = option['offers'][0]['outcomes']

        playerLinesList = list()
        for playerLine in allOffers:
            aOdds = '+' + str(playerLine['oddsAmerican'])
            pName = playerLine['englishLabel']
            playerLinesList.append({'player': pName, 'odds': aOdds})

        formattedPlayerlines = list()
        for playerOdds in playerLinesList:
            formattedPlayerlines.append(addTeamToUnknownPlayerLine(playerOdds))

        homePlayerList = list()
        awayPlayerList = list()
        for player in formattedPlayerlines:
            if player['team'] == homeTeam:
                homePlayerList.append(player)
            elif player['team'] == awayTeam:
                awayPlayerList.append(player)

        gameDetailsList.append({
            'exchange': 'barstool',
            'startDatetime': event['startDatetime'],
            'home': homeTeam,
            'away': awayTeam,
            'homePlayerFirstQuarterOdds': homePlayerList,
            'awayPlayerFirstQuarterOdds': awayPlayerList
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

# https://www.lineups.com/nba/lineups
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
    teamList = ['NOP', 'IND', 'CHI', 'ORL', 'TOR', 'BKN', 'MIL', 'CLE', 'CHA', 'WAS', 'MIA', 'OKC', 'MIN', 'DET', 'PHX', 'NYK',
                'BOS', 'LAC', 'SAS', 'GSW', 'DAL', 'UTA', 'ATL', 'POR', 'PHI', 'HOU', 'MEM', 'DEN', 'LAL', 'SAC']
    teamList.sort()
    for team in teamList:
        sleepChecker(iterations=5, baseTime=1, randomMultiplier=1)
        getStarters(team)

def getDailyOdds(t1: str, t2: str, aOdds: str = '-110', exchange: str ='unspecified exchange'):
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
    teamList = ['NOP', 'IND', 'CHI', 'ORL', 'TOR', 'BKN', 'MIL', 'CLE', 'CHA', 'WAS', 'MIA', 'OKC', 'MIN', 'DET', 'PHX', 'NYK'
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

    with open('Data/JSON/team_tipper_pairs.json', 'w') as file:
        json.dump(fullJson, file)


        # mostPopular = singleGameResponse
        # allMPBets = mostPopular['criterion']
        # playerScoreFirstFG = None
        #
        # for bet in allMPBets:
        #     if bet['label'] == "Player to Score the First Field Goal of the Game":
        #         playerScoreFirstFG = bet
        #         break
        # if playerScoreFirstFG is None:
        #     print("No bet found in barstool for player to score first field goal in game", event)
        #     continue

        # lines = playerScoreFirstFG['offers'][0]['outcomes']
