import json
import random
import time
import unicodedata

import requests
import unidecode as unidecode
from bs4 import BeautifulSoup
from requests import get


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


def getPlayerSuffix(name):
    # copied from this repo https://github.com/vishaalagartha/basketball_reference_scraper/blob/master/basketball_reference_scraper
    normalized_name = unidecode.unidecode(unicodedata.normalize('NFD', name).encode('ascii', 'ignore').decode("utf-8"))
    initial = normalized_name.split(' ')[1][0].lower()
    suffix = '/players/' + initial +'/' + createSuffix(name) + '01.html'
    player_r = get(f'https://www.basketball-reference.com{suffix}')
    while player_r.status_code==200:
        player_soup = BeautifulSoup(player_r.content, 'html.parser')
        h1 = player_soup.find('h1', attrs={'itemprop': 'name'})
        if h1:
            page_name = h1.find('span').text
            """
                Test if the URL we constructed matches the 
                name of the player on that page; if it does,
                return suffix, if not add 1 to the numbering
                and recheck.
            """
            if ((unidecode.unidecode(page_name)).lower() == normalized_name.lower()):
                return suffix
            else:
                suffix = suffix[:-6] + str(int(suffix[-6])+1) + suffix[-5:]
                player_r = get(f'https://www.basketball-reference.com{suffix}')

    return None


def createSuffix(name):
    # copied from this repo https://github.com/vishaalagartha/basketball_reference_scraper/blob/master/basketball_reference_scraper
    normalizedName = unicodedata.normalize('NFD', name.replace(".","")).encode('ascii', 'ignore').decode("utf-8")
    first = unidecode.unidecode(normalizedName[:2].lower())
    lasts = normalizedName.split(' ')[1:]
    names = ''.join(lasts)
    second = ""
    if len(names) <= 5:
        second += names[:].lower()

    else:
        second += names[:5].lower()

    return second+first + '01.html' #todo this doesn't account for if the name appears more than once


def getDashDateFromGameCode(gameCode):
    gameCode = str(gameCode)
    year = gameCode[:4]
    month = gameCode[4:6]
    day = gameCode[6:8]
    return year + '-' + month + '-' + day


def getHomeTeamFromGameCode(game_code):
    return game_code[-3:]


def getSoupFromUrl(url, returnStatus=False):
    page = requests.get(url)
    if returnStatus:
        return BeautifulSoup(page.content, 'html.parser'), page.status_code
    return BeautifulSoup(page.content, 'html.parser')


def getDashDateAndHomeCodeFromGameCode(game_code):
    return getDashDateFromGameCode(game_code), getHomeTeamFromGameCode(game_code)


def sleepChecker(sleepCounter, iterations=3, baseTime=2, randomMultiplier=3, printStop=True):
    sleepCounter += 1 #todo refactor this to use env or something so that only one line is needed when time delay needs to be added to a func
    if sleepCounter % iterations == 0:
        if printStop:
            print("sleeping for", str(baseTime), "+ random seconds")
        time.sleep(baseTime + random.random() * randomMultiplier)
        sleepCounter = 0
    return sleepCounter