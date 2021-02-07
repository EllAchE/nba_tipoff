# Finding Games
# https://github.com/swar/nba_api/blob/master/docs/examples/Finding%20Games.ipynb

# Pulling play by play
# https://github.com/swar/nba_api/blob/master/docs/examples/PlayByPlay.ipynb

'''
1. Individual player scoring percent on first shot
2. player score percent overall
3. Team score percent first shot
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

To fetch here
Individual player scoring percent on first shot
Team score percent first shot
Percentage of first shots made by player overall
Percentage of first shots taken by particular player

'''

from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguegamefinder
from nba_api.stats.endpoints import playbyplay

from Functions.Utils import getDashDateAndHomeCodeFromGameCode


def convertBballRefShortToNBA(short_code): #todo have a more robust converter here
    if short_code == 'PHO':
        return 'PHX'
    if short_code == 'BRK':
        return 'BKN'
    return short_code


def getTeamDictionaryFromShortCode(short_code):
    short_code = convertBballRefShortToNBA(short_code)
    nba_teams = teams.get_teams()
    team_dict = [team for team in nba_teams if team['abbreviation'] == short_code][0]
    return team_dict['id']


def getAllGamesForTeam(team_id):
    gamefinder = leaguegamefinder.LeagueGameFinder(team_id_nullable=team_id)
    return gamefinder.get_data_frames()[0]


def getAllGamesInSeason(season, short_code):
    season -= 1
    team_id = getTeamDictionaryFromShortCode(short_code)
    games_df = getAllGamesForTeam(team_id)
    return games_df[games_df.SEASON_ID.str[-4:] == str(season)]


# game date format is YYYY-MM-DD
def getGameOnDate(date_str, short_code):
    team_id = getTeamDictionaryFromShortCode(short_code)
    all_games = getAllGamesForTeam(team_id)
    return all_games[all_games.GAME_DATE == str(date_str)]


def getGameIdFromTeamAndDate(date_str, short_code):
    game_obj = getGameOnDate(date_str, short_code)
    return game_obj.GAME_ID.iloc[0]


def getGamePlayByPlay(game_id):
    return playbyplay.PlayByPlay(game_id).get_data_frames()[0]


def getAllShotsBeforeScore():
    pass


def getTipoffLine(pbpDf, returnIndex=False):
    try:
        tipoffSeries = pbpDf[pbpDf.EVENTMSGTYPE == 10]
        tipoffContent = tipoffSeries.iloc[0]
        type = 10
    except:
        tipoffSeries = pbpDf[pbpDf.EVENTMSGTYPE == 7]
        tipoffContent = tipoffSeries.iloc[0]
        type = 7

    print('Home Desc', tipoffContent.HOMEDESCRIPTION, 'Vis Desc', tipoffContent.VISITORDESCRIPTION, 'Neut Desc', tipoffContent.NEUTRALDESCRIPTION)

    if tipoffContent.HOMEDESCRIPTION is not None:
        content = tipoffContent.HOMEDESCRIPTION
    elif tipoffContent.VISITORDESCRIPTION is not None:
        content = tipoffContent.VISITORDESCRIPTION
    else:
        print('nothing for home or away, neutral said', tipoffContent.NEUTRALDESCRIPTION)

    if type == 10:
        pass
    if type == 7:
        pass
    pass

    tipoffContentList = content.split(' ') # todo use a regex and not a split here ,i.e. violation
    # todo look at home vs. visitor for next action following index of first

    if returnIndex:
        return tipoffContentList, tipoffSeries.index
    return tipoffContentList


def updateMissingTipoffResults(gameId):
    pbpDf = getGamePlayByPlay(gameId)
    tipoffContent = getTipoffLine(pbpDf)
    return tipoffContent #todo this method needs updating


test_bad_data_games = [['199711110MIN', 'MIN', 'SAS'],
                        ['199711190LAL', 'LAL', 'MIN'],
                        ['201911200TOR', 'TOR', 'ORL'],
                        ['201911260DAL', 'DAL', 'LAC'],
                        ['199711240TOR'], ['199711270IND'], ['201911040PHO']]



# class EventMsgType(Enum):
#     FIELD_GOAL_MADE = 1
#     FIELD_GOAL_MISSED = 2
#     FREE_THROWfree_throw_attempt = 3
#     REBOUND = 4
#     TURNOVER = 5
#     FOUL = 6
#     VIOLATION = 7
#     SUBSTITUTION = 8
#     TIMEOUT = 9
#     JUMP_BALL = 10
#     EJECTION = 11
#     PERIOD_BEGIN = 12
#     PERIOD_END = 13

# def getNbaComResultsFromBballReferenceCode(bballCode):
#     date, team_code = getDashDateAndHomeCodeFromGameCode(bballCode)
#     test = getGameIdFromTeamAndDate(date, team_code)
#     deb = getTipoffResults(test)
#     print(deb)


# for item in test_bad_data_games:
#     getNbaComResultsFromBballReferenceCode(item[0])

# todo use this work to fill in the blanks on the missing games in the csv