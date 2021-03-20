import json
from src.utils import getSoupFromUrl

def getSingleTeamOffDefData(row, season):
    defRate = row.contents[-1].contents[0]
    offRate = row.contents[-2].contents[0]
    orr = row.contents[5].contents[0]
    drr = row.contents[6].contents[0]
    rebr = row.contents[7].contents[0]
    effectiveFg = row.contents[8].contents[0]
    teamName = row.contents[1].contents[0].contents[0]

    return teamName, {
        "team": teamName,
        "orr": orr,
        "drr": drr,
        "rebr": rebr,
        "eff_fg": effectiveFg,
        "offRate": offRate,
        "def_rate": defRate,
        "season": season
    }

def getOffDefRatings(season=None, savePath=None):
    if season is not None:
        url = 'http://www.espn.com/nba/hollinger/teamstats/_/year/'.format(season)
    else:
        url = 'http://www.espn.com/nba/hollinger/teamstats'
        season = 2021

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
            json.dump(seasonDict, jsonF, indent=4)

    return seasonDict