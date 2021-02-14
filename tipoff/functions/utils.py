import json
import random
import time
import requests
import unicodedata
import unidecode

from bs4 import BeautifulSoup
from nba_api.stats.endpoints import CommonPlayerInfo
from nba_api.stats.static.players import find_players_by_full_name

import ENVIRONMENT


def addSlugToNames():
    with open('../Data/JSON/Public_NBA_API/teams.json') as dat_file:
        team_dict = json.load(dat_file)

    for team in team_dict:
        slug = team['teamName']
        slug = slug.replace(" ", "-")
        slug = slug.lower()
        team['slug'] = slug

    with open('../Data/JSON/Public_NBA_API/teams.json', 'w') as w_file:
        json.dump(team_dict, w_file)
    print('added slugs')

def checkForBadSuffix(suffix):
    if suffix == '/players/c/capelcl01.html':
        return '/players/c/capelca01.html'
    return suffix

def getPlayerSuffix(name: str):
    # copied from this repo https://github.com/vishaalagartha/basketball_reference_scraper/blob/master/basketball_reference_scraper
    normalized_name = unidecode.unidecode(unicodedata.normalize('NFD', name).encode('ascii', 'ignore').decode("utf-8"))
    nameSplit = normalized_name.lower().split(' ')
    initial = nameSplit[-1][0]
    suffix = '/players/' + initial +'/' + createSuffix(name)
    ogSuffix = suffix
    playerRequest = requests.get(f'https://www.basketball-reference.com{suffix}')
    
    while playerRequest.status_code == 200:
        player_soup = BeautifulSoup(playerRequest.content, 'html.parser')
        h1 = player_soup.find('h1', attrs={'itemprop': 'name'})
        
        if h1:
            page_name = h1.find('span').text
            """
                Test if the URL we constructed matches the name of the player on that page; if it does,
                return suffix, if not add 1 to the numbering and recheck.
            """
            if ((unidecode.unidecode(page_name)).lower() == normalized_name.lower()):
                suffix = checkForBadSuffix(suffix)
                return suffix
            else:
                suffix = suffix[:-6] + str(int(suffix[-6])+1) + suffix[-5:]
                playerRequest = requests.get(f'https://www.basketball-reference.com{suffix}')

    print('couldn\'t find match for player', ogSuffix, 'returning naive suffix')
    ogSuffix = checkForBadSuffix(ogSuffix)
    return ogSuffix

def createSuffix(name: str):
    # copied from this repo https://github.com/vishaalagartha/basketball_reference_scraper/blob/master/basketball_reference_scraper
    normalizedName = unicodedata.normalize('NFD', name.replace(".","")).encode('ascii', 'ignore').decode("utf-8")
    normalizedNameNoSpace = normalizedName.replace(' ', '')
    first = unidecode.unidecode(normalizedNameNoSpace[:2].lower())
    lasts = normalizedName.split(' ')[1:] # todo this method breaks on some edge cases like r. j. barrett so I customized it, but not sure how weel it works. Also clint capela breaks the convention
    names = ''.join(lasts)
    second = ""
    if len(names) <= 5:
        second += names[:].lower()

    else:
        second += names[:5].lower()

    return second+first + '01.html' #todo this doesn't account for if the name appears more than once

def getDashDateFromGameCode(gameCode: str):
    gameCode = str(gameCode)
    year = gameCode[:4]
    month = gameCode[4:6]
    day = gameCode[6:8]
    return year + '-' + month + '-' + day


def getTeamFullFromShort(shortCode):
    with open(ENVIRONMENT.TEAM_CONVERSION_PATH) as teamsJson:
        teamDict = json.load(teamsJson)
    for team in teamDict:
        if team["abbreviation"] == shortCode:
            return team["teamName"]
    raise ValueError('No team match found for code', shortCode)


def getHomeTeamFromGameCode(game_code: str):
    return game_code[-3:]

def getSoupFromUrl(url: str, returnStatus: bool = False):
    page = requests.get(url)
    
    if returnStatus:
        return BeautifulSoup(page.content, 'html.parser'), page.status_code
    
    return BeautifulSoup(page.content, 'html.parser')

def getDashDateAndHomeCodeFromGameCode(game_code: str):
    return getDashDateFromGameCode(game_code), getHomeTeamFromGameCode(game_code)

def sleepChecker(sleepCounter: int, iterations: int = 3, baseTime: int = 2, randomMultiplier: int = 3, printStop: bool = False):
    sleepCounter += 1 #todo refactor this to use env or something so that only one line is needed when time delay needs to be added to a func
    if sleepCounter % iterations == 0:
        if printStop:
            print("sleeping for", str(baseTime), "+ random seconds")
        time.sleep(baseTime + random.random() * randomMultiplier)
        sleepCounter = 0
    return sleepCounter

def getPlayerTeamFromFullName(name):
    playerDict = find_players_by_full_name(name)[0] # todo deal with unicode breaking charanacters i.e. in the name bojan bogdonavic 'Bojan Bogdanović'
    playerId = playerDict['id']
    data = CommonPlayerInfo(player_id=playerId)
    playerData = data.common_player_info.get_data_frame()
    abbreviation = playerData['TEAM_ABBREVIATION'].iloc[0] # index of this if list is 19 (20th item)
    return abbreviation

def getPlayerTeamFromNbaApi(name):
    # https://github.com/swar/nba_api/blob/master/docs/nba_api/stats/endpoints/commonplayerinfo.md
    pass

def getPlayerTeamInSeasonFromBballRefLink(playerLink, season, longCode=True):
    if longCode:
        playerLink = playerLink[11:]
    with open('../../Data/JSON/player_team_pairs.json') as teamPairs:
        seasons = json.load(teamPairs)
        try:
            return seasons[str(season)][playerLink]
        except:
            raise ValueError("no match found for player", playerLink)