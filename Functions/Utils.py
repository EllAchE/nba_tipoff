import json
import unicodedata

import unidecode as unidecode
from bs4 import BeautifulSoup
from requests import get

import ENVIRONMENT


def tip_score_prob(tip_win_odds, tip_winner_score_odds=ENVIRONMENT.TIP_WINNER_SCORE_ODDS):
    return tip_win_odds * tip_winner_score_odds + (1-tip_win_odds) * (1-tip_winner_score_odds)


def add_slug_to_names():
    with open('../Data/Public_NBA_API/teams.json') as dat_file:
        team_dict = json.load(dat_file)

    for team in team_dict:
        slug = team['teamName']
        slug = slug.replace(" ", "-")
        slug = slug.lower()
        team['slug'] = slug

    with open('../Data/Public_NBA_API/teams.json', 'w') as w_file:
        json.dump(team_dict, w_file)

    print('added slugs')


def get_player_suffix(name):
    # copied from this repo https://github.com/vishaalagartha/basketball_reference_scraper/blob/master/basketball_reference_scraper
    normalized_name = unidecode.unidecode(unicodedata.normalize('NFD', name).encode('ascii', 'ignore').decode("utf-8"))
    initial = normalized_name.split(' ')[1][0].lower()
    suffix = '/players/'+initial+'/'+create_suffix(name)+'01.html'
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


def create_suffix(name):
    # copied from this repo https://github.com/vishaalagartha/basketball_reference_scraper/blob/master/basketball_reference_scraper
    normalized_name = unicodedata.normalize('NFD', name.replace(".","")).encode('ascii', 'ignore').decode("utf-8")
    first = unidecode.unidecode(normalized_name[:2].lower())
    lasts = normalized_name.split(' ')[1:]
    names = ''.join(lasts)
    second = ""
    if len(names) <= 5:
        second += names[:].lower()

    else:
        second += names[:5].lower()

    return second+first + '01.html' #todo this doesn't account for if the name appears more than once

print(create_suffix('Deandre Jordan'))