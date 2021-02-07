# todo offensive rebounding/defensive rebounding influence
# todo incorporate other stats in (see below)
# todo add other stats and run ludwig/ai checker
from datetime import datetime

from dateutil.relativedelta import relativedelta

from Functions.Utils import getSoupFromUrl


def getPlayerHeightAndAge(playerLink):
    playerLink = playerLink[0] + '/' + playerLink #assumes playerLink doesn't have first initial
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

# Additional variables'
# Top that are def worht
'''
1. Individual player scoring percent on first shot
2. player score percent overall
3. Team score precent first shot
4. Team score percent overall
5. The above but for defense (opponents)
6. Percentage of first shots taken by particular player
7. Percentage of first shots made by player overall
8. Above two extended up until first basket made/for first X shots
9. Above for opponents
10. Team FT rate, two point vs. 3 point etc.
11. Number of shots until first made
12. First tip performance
13. Non standard tip
14. Low appearance tip
'''




# -	Ref (this would be complicated, but it's actually highly likely that certain refs will throw the ball in a way that benefits one other another)
# -	Is starter out
# -	Home/away - Data fetched
# -	Who they tip it to - possesion gaining player (fetched)
# -	Matchup
# -	Height - Being Fetched
# -	Offensive effectiveness
# -	Back-to-back games/overtime etc.
# -	Age decline - Being Fetched
# -	Recent history weighting

### POTENTIAL ADDITIONAL VARIABLES FOR ODDS MODEL
# Offensive Efficiency
# Defensive Efficiency
# new center record (for low Data on tipper)

# Recency bias in ranking (ARIMA model or similar)
# Season leaders
# Likely first shooter percentages
# Likely other shooter percentages
# combine vertical
# Injury
# Back to back/overtime
# Return from long absence/injury