import json
import csv
import pandas as pd

import re

# backlogtodo record historical betting lines
# backlogtodo try to find data source for historical betting lines
# https://widgets.digitalsportstech.com/api/gp?sb=bovada&tz=-5&gameId=in,135430
# backlogtodo BACKLOG get playbyplay from NCAA for rookie projections
# https://www.ncaa.com/game/5763659/play-by-play
import ENVIRONMENT
from tipoff.functions.utils import sleepChecker, getSoupFromUrl, getPlayerTeamInSeasonFromBballRefLink, \
    sleepChecker


def getSingleSeasonGameHeaders(season):
    normalMonths = ["october", "november", "december", "january", "february", "march", "april", "may", "june"]
    months2020 = ["october-2019", "november", "december", "january", "february", "march", "july", "august",
                   "september", "october-2020"]
    months2021 = ["december", "january", "february", "march"]  # may be a shortened season

    seasonGames = list()
    if season == 2020:
        months = months2020
    elif season == 2021:
        months = months2021
    else:
        months = normalMonths
    for month in months:
        games_list = getSingleMonthGameHeaders(season, month)
        for game in games_list:
            seasonGames.append(game)

    return seasonGames


def getSingleMonthGameHeaders(season, month):
    url = 'https://www.basketball-reference.com/leagues/NBA_{}_games-{}.html'.format(season, month)
    soup = getSoupFromUrl(url)

    tableGameStrs = soup.find_all('th', class_="left")
    tableAwayStrs = soup.select('td[Data-stat="visitor_team_name"]')
    tableHomeStrs = soup.select('td[Data-stat="home_team_name"]')

    monthGames = list()
    listLen = len(tableGameStrs)
    i = 0
    while i < listLen - 1:
        i += 1
        monthGames.append(getSingleGameHeaders(tableGameStrs, tableHomeStrs, tableAwayStrs, i))

    return monthGames


def getSingleGameHeaders(table_game_strs, table_home_strs, table_away_strs, i):
    gameStr = str(table_game_strs[i])
    awayStrFull = str(table_away_strs[i].a.contents[0])
    homeStrFull = str(table_home_strs[i].a.contents[0])

    sIndex = gameStr.index('csk="') + 5
    awayStrShort = str(table_away_strs[i])[sIndex:sIndex + 3]
    homeStrShort = str(table_home_strs[i])[sIndex:sIndex + 3]

    game_short = gameStr[sIndex:sIndex + 12]
    game_long = 'https://www.basketball-reference.com/boxscores/pbp/' + game_short + '.html'

    return [game_short, game_long, homeStrFull, awayStrFull, homeStrShort, awayStrShort]


def conditionalDataChecks(homeTeam, awayTeam, tipper1, tipper2, tipper1Link, tipper2Link, possessionGainingPlayerLink, firstScoringPlayerLink, season):
    if homeTeam in getPlayerTeamInSeasonFromBballRefLink(tipper1Link, season):
        homeTipper = tipper1
        awayTipper = tipper2
        homeTipperLink = tipper1Link
        awayTipperLink = tipper2Link
    else:
        homeTipper = tipper2
        awayTipper = tipper1
        homeTipperLink = tipper2Link
        awayTipperLink = tipper1Link

    if homeTeam in getPlayerTeamInSeasonFromBballRefLink(possessionGainingPlayerLink, season):
        possessionGainingTeam = homeTeam
        possessionLosingTeam = awayTeam
        tipWinner = homeTipper
        tipLoser = awayTipper
        tipWinnerLink = homeTipperLink
        tipLoserLink = awayTipperLink
    else:
        possessionGainingTeam = awayTeam
        possessionLosingTeam = homeTeam
        tipWinner = awayTipper
        tipLoser = homeTipper
        tipWinnerLink = awayTipperLink
        tipLoserLink = homeTipperLink

    if homeTeam in getPlayerTeamInSeasonFromBballRefLink(firstScoringPlayerLink, season):
        firstScoringTeam = homeTeam
        scoredUponTeam = awayTeam
    else:
        firstScoringTeam = awayTeam
        scoredUponTeam = homeTeam

    if possessionGainingTeam == firstScoringTeam:
        tipWinScore = 1
    else:
        tipWinScore = 0

    return homeTipper, awayTipper, homeTipperLink, awayTipperLink, possessionGainingTeam, possessionLosingTeam, tipWinner,\
           tipLoser, tipWinnerLink, tipLoserLink, firstScoringTeam, scoredUponTeam, tipWinScore


def getTipWinnerAndFirstScore(gameLink, season, homeTeam, awayTeam):
    # https://www.basketball-reference.com/boxscores/pbp/201901220OKC.html
    url = 'https://www.basketball-reference.com/boxscores/pbp/{}.html'.format(gameLink)
    soup, statusCode = getSoupFromUrl(url, returnStatus=True)
    print("GET request for game", gameLink, "returned status", statusCode)

    # table = soup.select('table[id="pbp"]')
    possessionWinLine = soup.select('td[colspan="5"]')[0].contents

    if str(possessionWinLine[0]) == "Start of 1st quarter":
        possessionWinLine = soup.select('td[colspan="5"]')[1].contents

    firstScoreLineOptions = soup.find_all('td', class_='bbr-play-score', limit=2)[:2]
    if re.search(r'makes', str(firstScoreLineOptions[0])) is not None:
        firstScoreLine = firstScoreLineOptions[0].contents
    else:
        firstScoreLine = firstScoreLineOptions[1].contents

    def pNameAndCode(tag):
        return tag.contents[0], re.search(r'(?<=")(.*?)(?=")', str(tag)).group(0)

    firstScoringPlayer, firstScoringPlayerLink = pNameAndCode(firstScoreLine[0])
    try:
        tipper1, tipper1Link = pNameAndCode(possessionWinLine[1])
        tipper2, tipper2Link = pNameAndCode(possessionWinLine[3])
        possessing_player, possessing_player_link = pNameAndCode(possessionWinLine[5])

        homeTipper, awayTipper, homeTipperLink, awayTipperLink,  tipWinTeam, tipLosingTeam, tipWinner, tipLoser,\
        tipWinnerLink, tipLoserLink, firstScoringTeam, scoredUponTeam, tipWinScore = conditionalDataChecks(
            homeTeam, awayTeam, tipper1, tipper2, tipper1Link, tipper2Link, possessing_player_link,
            firstScoringPlayerLink, season)

        return [homeTipper, homeTipperLink, awayTipper, awayTipperLink, firstScoringPlayer, tipWinTeam,
                tipLosingTeam, possessing_player, possessing_player_link, firstScoringTeam, scoredUponTeam,
                tipWinner, tipWinnerLink, tipLoser, tipLoserLink, tipWinScore]
    except:
        return [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]


def getSingleTeamOffDefData(row, season):
    defRate = row.contents[-1].contents[0]
    offRate = row.contents[-2].contents[0]
    orr = row.contents[5].contents[0]
    drr = row.contents[6].contents[0]
    rebr = row.contents[7].contents[0]
    effectiveFg = row.contents[8].contents[0]
    teamName = row.contents[1].contents[0].contents[0]

    return teamName, {"team": teamName, "orr": orr, "drr": drr, "rebr": rebr, "eff_fg": effectiveFg, "offRate": offRate, "def_rate": defRate, "season": season}


def getOffDefRatings(season=None, savePath=None):
    if season is not None:
        url = 'http://www.espn.com/nba/hollinger/teamstats/_/year/'.format(season)
    else:
        url = 'http://www.espn.com/nba/hollinger/teamstats'
        season = 2021
    # http://www.espn.com/nba/hollinger/teamstats/_/year/2020
    soup, statusCode = getSoupFromUrl(url, returnStatus=True)
    print('GET to', url, 'returned status', statusCode)

    seasonDict = {}
    seasonDict['season'] = season
    rows = soup.select('tr[class*="row team-"]')

    for row in rows:
        teamName, teamStats = getSingleTeamOffDefData(row, season)
        seasonDict[teamName] = teamStats

    if savePath is not None:
        with open(savePath, 'w') as jsonF:
            json.dump(seasonDict, jsonF)

    return seasonDict

def updateCurrentSeason(pathToData='Data/CSV/tipoff_and_first_score_details_2021_season.csv', currentSeason=2021):
    df = pd.read_csv(pathToData)
    appendFile = open(pathToData, 'a')
    indexAfterLastGame = len(df)

    with appendFile:
        csvWriter = csv.writer(appendFile)
        gameHeaders = getSingleSeasonGameHeaders(currentSeason)
        gameHeadersLength = len(gameHeaders)

        while indexAfterLastGame < gameHeadersLength:
            sleepChecker(iterations=16, baseTime=0, randomMultiplier=1)
            try:
                line = gameHeaders[indexAfterLastGame]
                row = line + getTipWinnerAndFirstScore(line[0], currentSeason, line[4], line[5])
                print(row)
                csvWriter.writerow(row)
                indexAfterLastGame += 1
            except:
                break

def oneSeasonFromScratch(season, path):
    temp = pd.DataFrame()
    temp.to_csv(path)
    dFile = open(path, 'w')

    with dFile:
        csvWriter = csv.writer(dFile)
        csvWriter.writerow(
            ['Game Code', 'Full Hyperlink', 'Home', 'Away', 'Home Short', 'Away Short', 'Home Tipper', 'Home Tipper Link', 'Away Tipper',
             'Away Tipper Link', 'First Scorer', 'Tip Winning Team', 'Tip Losing Team', 'Possession Gaining Player', 'Possession Gaining Player Link',
             'First Scoring Team', 'Scored Upon Team', 'Tip Winner', 'Tip Winner Link', 'Tip Loser',
             'Tip Loser Link', 'Tip Winner Scores'])
        gameHeaders = getSingleSeasonGameHeaders(season)

        for line in gameHeaders:
            sleepChecker(iterations=16, baseTime=0, randomMultiplier=1)
            try:
                row = line + getTipWinnerAndFirstScore(line[0], season, line[4], line[5])
                print(row)
                csvWriter.writerow(row)
            except:
                break
