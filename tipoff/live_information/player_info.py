from datetime import datetime
from dateutil.relativedelta import relativedelta
from Functions.Utils import getSoupFromUrl


def getPlayerHeightAndAge(playerLink):
    playerLink = playerLink[0] + '/' + playerLink # assumes playerLink doesn't have first initial
    url = 'https://www.basketball-reference.com/players/{}'.format(playerLink)
    soup = getSoupFromUrl(url)
    heightTag = soup.select('span[itemprop="height"]')
    height = heightTag.contents[0]
    bDateTag = soup.select('span[itemprop="birthDate"]')
    bDate = bDateTag['data-birth'] # in YYYY-MM-DD form
    return height, birthDateToAge(bDate)


def birthDateToAge(birthDate): # in YYYY-MM-DD form
    list = [int(x) for x in birthDate.split('-')]
    now = datetime.now
    born = datetime(list[0], list[1], list[2])
    return relativedelta(now, born).years