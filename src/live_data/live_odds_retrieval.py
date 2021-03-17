# Places to retrieve live lineups
# https://www.rotowire.com/basketball/nba-lineups.php
# https://www.nba.com/players/todays-lineups
# stats api here - https://stats.nba.com/js/data/leaders/00_active_starters_20210128.json

import json
import re
from datetime import datetime

import requests
import pandas as pd
from bs4 import BeautifulSoup

import ENVIRONMENT
from src.database.database_access import getUniversalTeamShortCode, getPlayerCurrentTeam, getUniversalPlayerName
from src.odds_and_statistics.odds_calculator import checkEvPlayerCodesOddsLine, kellyBetFromAOddsAndScoreProb, decimalToAmerican
from src.utils import getTeamFullFromShort, getSoupFromUrl, sleepChecker


def addTeamToUnknownPlayerLine(rawPlayerLine):
    formattedPlayerName = getUniversalPlayerName(rawPlayerLine['player'])
    teamShortCodeBballRefFormat = getPlayerCurrentTeam(formattedPlayerName)
    teamShortCode = getUniversalTeamShortCode(teamShortCodeBballRefFormat)

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

def getLastTipper(team_code, season_csv=ENVIRONMENT.CURRENT_SEASON_CSV):
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
        with open(ENVIRONMENT.TEAM_NAMES_PATH) as j_file:
            team_dict = json.load(j_file)

    for team in team_dict:
        if team['abbreviation'] == team_code:
            return team['slug']

    raise ValueError('no matching team for abbreviation')

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
        # todo look at response when bet DNE
        if item['team2Odds'] == 1 or item['team1Odds'] == 1:
            print('invalid odds for bet', item['shortTitle'], '(decimal odds of 1)')
            continue

        scoreFirstBetsBothTeamsFormatted.append({
            'exchange': 'bovada',
            "shortTitle": item['shortTitle'],
            "away": getUniversalTeamShortCode(item['team2id']),
            "home": getUniversalTeamShortCode(item['team1id']),
            "awayTeamFirstQuarterOdds": decimalToAmerican(item['team2Odds']),
            "homeTeamFirstQuarterOdds": decimalToAmerican(item['team1Odds']),
            "awayPlayerFirstQuarterOdds": [],
            "homePlayerFirstQuarterOdds": []
        })
        scoreFirstBetsBothTeamsFormatted.append({
            'exchange': 'bovada',
            "away": getUniversalTeamShortCode(item['team1id']),
            "home": getUniversalTeamShortCode(item['team2id']),
            "shortTitle": item['shortTitle'],
            "awayTeamFirstQuarterOdds": decimalToAmerican(item['team2Odds']),
            "homeTeamFirstQuarterOdds": decimalToAmerican(item['team1Odds']),
            "awayPlayerFirstQuarterOdds": [],
            "homePlayerFirstQuarterOdds": []
        })  # This is done as it is unknown for bovada whic hteam belongs to which odds

    return scoreFirstBetsBothTeamsFormatted, gameIdSet

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
                        "team": getUniversalTeamShortCode(homeShort)
                    })
                elif player['player']['team']['abbreviation'] == awayShort:
                    awayPlayerOdds.append({
                        "player": player['player']['name'],
                        "odds": actualOdds,
                        "team": getUniversalTeamShortCode(awayShort)
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

# backlogtodo fix this to account for vames that don't yet matter

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
            print("no player lines found for bovada game", gameLine)

    return scoreFirstBetsBothTeamsFormatted

def draftKingsOdds():
    # https://sportsbook.draftkings.com/leagues/basketball/103?category=game-props&subcategory=odd/even
    # API - https://sportsbook.draftkings.com//sites/US-SB/api/v1/eventgroup/103/full?includePromotions=true&format=json
    allBets = requests.get('https://sportsbook.draftkings.com//sites/US-SB/api/v1/eventgroup/103/full?includePromotions=true&format=json').json()
    offerCategories = allBets['eventGroup']['offerCategories']

    playerProps = gameProps = None
    for category in offerCategories:
        if category['name'] == "Game Props":
            gameProps = category['offerSubcategoryDescriptors']
        if category['name'] == "Player Props":
            playerProps = category['offerSubcategoryDescriptors']

    teamMatch = playerMatch = False
    if gameProps is not None:
        for subCategory in gameProps:
            if subCategory['name'] == "First Team to Score":
                firstTeamToScoreLines = subCategory['offerSubcategory']['offers']
                teamMatch = True
                break
    else:
        print('no game props found for Draftkings odds')

    if playerProps is not None:
        for subCategory in playerProps:
            if subCategory['name'] == "First Field Goal":
                firstPlayerToScoreLines = subCategory['offerSubcategory']['offers']
                playerMatch = True
                break
    else:
        print('no player props found for Draftkings odds')

    teamSet = set()
    allGameLines = list()
    if teamMatch:
        for teamLine in firstTeamToScoreLines:
            outcomes = teamLine[0]['outcomes']
            team1 = getUniversalTeamShortCode(outcomes[0]['label'])
            team1Odds = outcomes[0]['oddsAmerican']
            team2 = getUniversalTeamShortCode(outcomes[1]['label'])
            team2Odds = outcomes[1]['oddsAmerican']
            teamSet.add(team2)
            teamSet.add(team1)

            print('Adding game', team2, '@', team1, 'from draftkings to list')

            allGameLines.append({
                "exchange": "draftkings",
                "home": team1,
                "away": team2,
                "homeTeamFirstQuarterOdds": str(team1Odds),
                "awayTeamFirstQuarterOdds": str(team2Odds),
                "homePlayerFirstQuarterOdds": [],
                "awayPlayerFirstQuarterOdds": []
            })
    else:
        print('No team odds for draftkings currently')

    rawPlayerLines = list()
    if playerMatch:
        for game in firstPlayerToScoreLines:
            outcomes = game[0]['outcomes']
            for playerOdds in outcomes:
                rawPlayerLines.append({
                    "player": playerOdds['label'],
                    "odds": playerOdds['oddsAmerican']
                })
    else:
        print('No player odds for draftkings currently')

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

def getAmericanOddsFanduel(currentpriceup, currentpricedown):
    if currentpriceup is None:
        return None
    if currentpriceup >= currentpricedown:
        return '+' + str((currentpriceup / currentpricedown) * 100)
    elif currentpriceup < currentpricedown:
        return str((100 / currentpriceup) * currentpricedown * -1)
    else:
        raise ValueError('fanduel odds messed up')

def fanduelOddsToday():
    return _fanduelOddsAll()

def fanduelOddsTomorrow():
    return _fanduelOddsAll(today=False)

def _fanduelOddsAll(today=True):
    currentDate = datetime.today().strftime('%Y-%m-%d')
    gamesResponse = requests.get("https://sportsbook.fanduel.com/cache/psmg/UK/63747.3.json").json()
    teamSet = set()

    quarterOddsList = list()
    unassignedPlayerOddsList = list()
    gameIdSet = set()
    listOfGames = gamesResponse['events']

    for game in listOfGames:
        if game['tsstart'][:10] == currentDate and today:
            gameIdSet.add(game['idfoevent'])
        elif game['tsstart'][:10] != currentDate and not today:
            gameIdSet.add(game['idfoevent'])

    allEventMatch = None
    for gameId in gameIdSet:
        gameResponse = requests.get('https://sportsbook.fanduel.com/cache/psevent/UK/1/false/{}.json'.format(gameId)).json()
        print('running for fanduel game', gameResponse['externaldescription'])
        sleepChecker(iterations=1, baseTime=2, randomMultiplier=8)
        # backlogtodo test the start time to ignore ongoing games, not just by date
        try:
            for eventMarketGroup in gameResponse['eventmarketgroups']:
                if eventMarketGroup['name'] == 'All':
                    allEventMatch = True
                    break
        except:
            print('game', gameResponse['externaldescription'], 'had no matches for eventmarketgroups. Game has likely already started, or is tomorrow.')
            continue

        teamScoreFirstQuarter1 = teamScoreFirstQuarter2 = teamScoreFirstQuarter3 = teamScoreFirstQuarter4 = playerScoreFirst = None
        if allEventMatch:
            for market in eventMarketGroup['markets']:
                if 'to Score First' in market['name']:
                    if market['name'] == 'Team to Score First':
                        teamScoreFirstQuarter1 = market
                    elif market['name'] == '2nd Quarter Team to Score First':
                        teamScoreFirstQuarter2 = market
                    elif market['name'] == '3rd Quarter Team to Score First':
                        teamScoreFirstQuarter3 = market
                    elif market['name'] == '4th Quarter Team to Score First':
                        teamScoreFirstQuarter4 = market
                elif market['name'] == 'First Basket':
                    playerScoreFirst = market

        if playerScoreFirst is not None:
            for selection in playerScoreFirst['selections']:
                unassignedPlayerOddsList.append({
                    "player": selection['name'],
                    "odds": getAmericanOddsFanduel(selection['currentpriceup'], selection['currentpricedown']),
                })
        else:
            print('no player odds for this fanduel game currently')

        home1Odds = away1Odds = home2Odds = away2Odds = home3Odds = away3Odds = home4Odds = away4Odds = None
        if teamScoreFirstQuarter1 is not None:
            quarter1home = teamScoreFirstQuarter1['selections'][0] if teamScoreFirstQuarter1['selections'][0]['hadvalue'] == 'H' else teamScoreFirstQuarter1['selections'][1]
            quarter1away = teamScoreFirstQuarter1['selections'][0] if teamScoreFirstQuarter1['selections'][0]['hadvalue'] == 'A' else teamScoreFirstQuarter1['selections'][1]
            home1Odds = getAmericanOddsFanduel(quarter1home['currentpriceup'], quarter1home['currentpricedown'])
            away1Odds = getAmericanOddsFanduel(quarter1away['currentpriceup'], quarter1away['currentpricedown'])
        else:
            print('no team odds for this fanduel game currently')
        if teamScoreFirstQuarter2 is not None:
            quarter2home = teamScoreFirstQuarter2['selections'][0] if teamScoreFirstQuarter2['selections'][0]['hadvalue'] == 'H' else teamScoreFirstQuarter2['selections'][1]
            quarter2away = teamScoreFirstQuarter2['selections'][0] if teamScoreFirstQuarter2['selections'][0]['hadvalue'] == 'A' else teamScoreFirstQuarter2['selections'][1]
            home2Odds = getAmericanOddsFanduel(quarter2home['currentpriceup'], quarter2home['currentpricedown'])
            away2Odds = getAmericanOddsFanduel(quarter2away['currentpriceup'], quarter2away['currentpricedown'])
        if teamScoreFirstQuarter3 is not None:
            quarter3home = teamScoreFirstQuarter3['selections'][0] if teamScoreFirstQuarter3['selections'][0]['hadvalue'] == 'H' else teamScoreFirstQuarter3['selections'][1]
            quarter3away = teamScoreFirstQuarter3['selections'][0] if teamScoreFirstQuarter3['selections'][0]['hadvalue'] == 'A' else teamScoreFirstQuarter3['selections'][1]
            home3Odds = getAmericanOddsFanduel(quarter3home['currentpriceup'], quarter3home['currentpricedown'])
            away3Odds = getAmericanOddsFanduel(quarter3away['currentpriceup'], quarter3away['currentpricedown'])
        if teamScoreFirstQuarter4 is not None:
            quarter4home = teamScoreFirstQuarter4['selections'][0] if teamScoreFirstQuarter4['selections'][0]['hadvalue'] == 'H' else teamScoreFirstQuarter4['selections'][1]
            quarter4away = teamScoreFirstQuarter4['selections'][0] if teamScoreFirstQuarter4['selections'][0]['hadvalue'] == 'A' else teamScoreFirstQuarter4['selections'][1]
            home4Odds = getAmericanOddsFanduel(quarter4home['currentpriceup'], quarter4home['currentpricedown'])
            away4Odds = getAmericanOddsFanduel(quarter4away['currentpriceup'], quarter4away['currentpricedown'])

        home = getUniversalTeamShortCode(gameResponse['participantshortname_home'].split(" ")[1])
        away = getUniversalTeamShortCode(gameResponse['participantshortname_away'].split(" ")[1])
        teamSet.add(home)
        teamSet.add(away)

        quarterOddsList.append({
            "gameDatetime": gameResponse['tsstart'],
            "home": home,
            "away": away,
            "exchange": "fanduel",
            "homeTeamFirstQuarterOdds": home1Odds,
            "awayTeamFirstQuarterOdds": away1Odds,
            "homeTeamSecondQuarterOdds": home2Odds,
            "awayTeamSecondQuarterOdds": away2Odds,
            "homeTeamThirdQuarterOdds": home3Odds,
            "awayTeamThirdQuarterOdds": away3Odds,
            "homeTeamFourthQuarterOdds": home4Odds,
            "awayTeamFourthQuarterOdds": away4Odds,
        })

        playerTeamDict = {}
        for team in teamSet:
            playerTeamDict[team] = []
        for rawLine in unassignedPlayerOddsList:
            playerLine = addTeamToUnknownPlayerLine(rawLine)
            team = getUniversalTeamShortCode(playerLine['team'])
            playerTeamDict[team] += [playerLine]

        for gameLine in quarterOddsList:
            gameLine["homePlayerFirstQuarterOdds"] = playerTeamDict[gameLine["home"]]
            gameLine["awayPlayerFirstQuarterOdds"] = playerTeamDict[gameLine["away"]]

        quarterOddsListWithAtLeastOneSetOfOdds = list()
        for gameLine in quarterOddsList:
            if (len(gameLine['homePlayerFirstQuarterOdds']) > 4 and len(gameLine['homePlayerFirstQuarterOdds']) > 4) or gameLine['homeTeamFirstQuarterOdds'] is not None:
                quarterOddsListWithAtLeastOneSetOfOdds.append(gameLine)

    if len(gameIdSet) == 0:
        print('No game ids were found on fanduel, make sure you are looking for the proper day (today or tomorrow are your options).')
    else:
        return quarterOddsListWithAtLeastOneSetOfOdds

def mgmOdds():
    # https://sports.co.betmgm.com/en/sports/events/minnesota-timberwolves-at-san-antonio-spurs-11101908?market=10000
    url = "https://cds-api.co.betmgm.com/bettingoffer/fixtures?x-bwin-accessid=OTU4NDk3MzEtOTAyNS00MjQzLWIxNWEtNTI2MjdhNWM3Zjk3&lang=en-us&country=US&userCountry=US&subdivision=Texas&fixtureTypes=Standard&state=Latest&offerMapping=Filtered&offerCategories=Gridable&fixtureCategories=Gridable,NonGridable,Other&sportIds=7&regionIds=9&competitionIds=6004&skip=0&take=50&sortBy=Tags"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'}
    response = requests.get(url, headers=headers)

    betmgmGames = json.loads(response.text)['fixtures']
    gameIDs = []
    for game in betmgmGames:
        if (game['stage'] == "PreMatch"):
            gameIDs.append(game['id'])

    allGameLines = list()
    for index in range(len(gameIDs)):
        print('Fetching MGM for game', gameIDs[index])
        gameURL = "https://cds-api.co.betmgm.com/bettingoffer/fixture-view?x-bwin-accessid=OTU4NDk3MzEtOTAyNS00MjQzLWIxNWEtNTI2MjdhNWM3Zjk3&lang=en-us&country=US&userCountry=US&subdivision=Texas&offerMapping=All&fixtureIds=" + \
                  gameIDs[index]
        gameResponse = requests.get(gameURL, headers=headers)
        oddsInfo = json.loads(gameResponse.text)['fixture']['games']
        sleepChecker(iterations=1)

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
                    "home": getUniversalTeamShortCode(team2),
                    "away": getUniversalTeamShortCode(team1),
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
        homeTeam = getUniversalTeamShortCode(event['homeTeam'])
        awayTeam = getUniversalTeamShortCode(event['awayTeam'])
        singleGameUrl = 'https://api-usa.pointsbet.com/api/v2/events/{}'.format(eventId)
        singleGameResponse = requests.get(singleGameUrl).json()
        print('retrieved pointsbet data for game', event['awayTeam'], "@", event['homeTeam'])

        # assumes just a single game
        for market in singleGameResponse['fixedOddsMarkets']:
            if market['eventName'] == "First Basket":
                firstBasketMarket = market
                for outcome in firstBasketMarket['outcomes']:
                    rawPlayerLines.append({
                        "player": outcome['name'],
                        "teamId": outcome['teamId'],
                        "odds": '+' + str(outcome['price'] * 100 - 100)
                    })

                homePlayerList = list()
                awayPlayerList = list()
                for player in rawPlayerLines:
                    universalName = getUniversalPlayerName(player['player'])
                    player['team'] = getUniversalTeamShortCode(getPlayerCurrentTeam(universalName))
                    if player['team'] == homeTeam:
                        homePlayerList.append(player)
                    elif player['team'] == awayTeam:
                        awayPlayerList.append(player)
                    else:
                        raise ValueError("player didn't match either team, or teams are misformatted/don't match universal team code", player)

                gameDict = {
                    'exchange': 'pointsBet',
                    "home": homeTeam,
                    "away": awayTeam,
                    "isFirstFieldGoal": True,
                    "homePlayerFirstQuarterOdds": homePlayerList,
                    "awayPlayerFirstQuarterOdds": awayPlayerList
                }

                if len(gameDict['homePlayerFirstQuarterOdds']) < 5 or len(gameDict['awayPlayerFirstQuarterOdds']) < 5:
                    print("not enough players in list")
                else:
                    gameDictList.append(gameDict)
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
        homeTeam = getUniversalTeamShortCode(event[2])
        awayTeam = getUniversalTeamShortCode(event[3])
        print('retrieved unibet data for game', awayTeam, '@', homeTeam)
        allBets = singleGameResponse['betOffers']

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
            player['team'] = getUniversalTeamShortCode(getPlayerCurrentTeam(universalName))
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

    # backlogtodo see if this needs optimization, may be duplciate values with unibet
    gameDetailsList = list()
    for event in eventsList:
        sleepChecker(baseTime=0.5, randomMultiplier=2)
        singleGameResponse = requests.get(singleEventUrlStub.format(event['id']), headers={"consumer":"www"}).json()
        homeTeam = getUniversalTeamShortCode(event['home'])
        awayTeam = getUniversalTeamShortCode(event['away'])
        print('retrieved barstool data for game', awayTeam, '@', homeTeam)

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

def getBetfairCurl(gameIdAndTeamNames):
    cookies = {
        'vid': 'e95eec18-e6e8-415d-a45f-c1e71a607cf2',
        '_gcl_au': '1.1.592435068.1612500111',
        'PI': '3013',
        'StickyTags': 'rfr=3013',
        'TrackingTags': '',
        'pi': 'partner3013',
        'rfr': '3013',
        'storageSSC': 'lsSSC%3D1',
        'OptanonAlertBoxClosed': '2021-02-05T04:41:58.656Z',
        'userhistory': '15854612871612500123657|1|N|050221|050221|home|N',
        'bucket': '3~36~test_search',
        'bfj': 'US',
        'bftim': '1612500301477',
        'bid_pPBFRdxAR61DXgGaYvvIPWQ7pAaq8QQJ': '58495c5b-f347-4bf2-83d3-ac01380c5656',
        'language': 'en_GB',
        'bfsd': 'ts=1613143926701|st=rp',
        'exp': 'sb',
        '_ga': 'GA1.1.231154474.1613613763',
        '__cfduid': 'dd15064b1017cbed2bc1dd4fd2f9e4eaf1615598351',
        'xsrftoken': '1e4dceb0-839a-11eb-b07e-fa163e3cd428',
        'wsid': '1e4dceb1-839a-11eb-b07e-fa163e3cd428',
        'betexPtk': 'betexLocale%3Den%7EbetexRegion%3DGBR%7EbetexCurrency%3DGBP',
        'betexPtkSess': 'betexCurrencySessionCookie%3DGBP%7EbetexLocaleSessionCookie%3Den%7EbetexRegionSessionCookie%3DGBR',
        'cashoutBetsToken': '',
        '_ga_K0W97M6SNZ': 'GS1.1.1615793964.4.1.1615793973.51',
        'OptanonConsent': 'isIABGlobal=false&datestamp=Mon+Mar+15+2021+02%3A39%3A34+GMT-0500+(Central+Daylight+Time)&version=6.6.0&hosts=&consentId=5b83ec42-c520-42d6-af1f-654334a6e758&interactionCount=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A0%2CC0002%3A0%2CC0004%3A0&geolocation=%3B&AwaitingReconsent=false',
    }

    headers = {
        'authority': 'www.betfair.com',
        'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
        'bf-fp': '908',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
        'accept': '*/*',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://www.betfair.coms{}'.format(gameIdAndTeamNames),
        'accept-language': 'en-US,en;q=0.9',
    }

    params = (
        ('selectedGroup', '-78637064'),
        ('action', 'changeMarketGroup'),
        ('modules', 'marketgroups@1053'),
        ('lastId', '1056'),
        ('d18', 'Main'),
        ('d31', 'Middle'),
        ('isAjax', 'true'),
        ('ts', '1615794006588'),
        ('alt', 'json'),
        ('xsrftoken', '1e4dceb0-839a-11eb-b07e-fa163e3cd428'),
    )

    return requests.get('https://www.betfair.com{}'.format(gameIdAndTeamNames),
                            headers=headers, params=params, cookies=cookies)

    # NB. Original query string below. It seems impossible to parse and
    # reproduce query strings 100% accurately so the one below is given
    # in case the reproduced version is not "correct".
    # response = requests.get('https://www.betfair.com/sport/basketball/nba/milwaukee-bucks-washington-wizards/30352512?selectedGroup=-78637064&action=changeMarketGroup&modules=marketgroups%401053&lastId=1056&d18=Main&d31=Middle&isAjax=true&ts=1615794006588&alt=json&xsrftoken=1e4dceb0-839a-11eb-b07e-fa163e3cd428', headers=headers, cookies=cookies)


def betfairOdds():
    # https://www.betfair.com/sport/basketball/nba/houston-rockets-oklahoma-city-thunder/30266729
    # betfair homepage https://www.betfair.com/sport/basketball
    # betfair single game page https://www.betfair.com/sport/basketball/nba/miami-heat-golden-state-warriors/30289841
    # betfair odds retrieval - have a curl request that gets them based on ids from an api endpoint, however doing so is pointless

    allGameUrl = 'https://www.betfair.com/sport/basketball'
    headers = {
        "authority": "www.betfair.com",
        "sec-ch-ua":"\"Google Chrome\";v=\"89\", \"Chromium\";v=\"89\", \";Not A Brand\";v=\"99\"",
        "bf-fp":"908",
        "sec-ch-ua-mobile":"?0",
        "user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
        "accept":"*/*",
        "sec-fetch-site":"same-origin",
        "sec-fetch-mode":"cors",
        "sec-fetch-dest":"empty",
        "referer":"https://www.betfair.com/sport/basketball/nba/milwaukee-bucks-washington-wizards/30352512",
        "accept-language":"en-US,en;q=0.9",
        "host": "www.betfair.com"
    }

    soup = getSoupFromUrl(allGameUrl, headers=headers)
    allLinks = soup.select('a[data-competition="NBA"]')
    allLinkSet = set()

    # assumes the link has length 8 for its game identifiers
    for link in allLinks:
        allLinkSet.add(str(link['href']))

    for link in allLinkSet:
        page = getBetfairCurl(link)
        soup = str(page.content)

        test = soup.find_all('a')
        print(test)

    print('finished fetching betfair data')


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
    with open(ENVIRONMENT.TEAM_TIPPER_PAIRS_PATH) as file:
        dict = json.load(file)
    for row in dict["pairs"]:
        if teamShort == row["team"]:
            return row["playerCode"]

def getAllExpectedStarters():
    teamList = ENVIRONMENT.CURRENT_TEAMS
    teamList.sort()
    for team in teamList:
        sleepChecker(iterations=5, baseTime=1, randomMultiplier=1)
        getStarters(team)

# backlogtodo confirm a minimum number of appearances
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
    teamList = ENVIRONMENT.CURRENT_TEAMS
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

    with open(ENVIRONMENT.TEAM_TIPPER_PAIRS_PATH, 'w') as file:
        json.dump(fullJson, file, indent=4)


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
