# Finding Games
# https://github.com/swar/nba_api/blob/master/docs/examples/Finding%20Games.ipynb

# Pulling play by play
# https://github.com/swar/nba_api/blob/master/docs/examples/PlayByPlay.ipynb

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


def getTipoffResults(game_id):
    pbp_df = getGamePlayByPlay(game_id)
    try:
        tipoff_series = pbp_df[pbp_df.EVENTMSGTYPE == 10]
        tipoff_content = tipoff_series.iloc[0]
        tip_index = tipoff_series.index
        possession_after_tipoff = pbp_df.iloc[tip_index + 1]
        type = 10
    except:
        tipoff_series = pbp_df[pbp_df.EVENTMSGTYPE == 7]
        tipoff_content = tipoff_series.iloc[0]
        tip_index = tipoff_series.index
        possession_after_tipoff = pbp_df.iloc[tip_index + 1]
        type = 7

    print('Home Desc', tipoff_content.HOMEDESCRIPTION, 'Vis Desc', tipoff_content.VISITORDESCRIPTION, 'Neut Desc', tipoff_content.NEUTRALDESCRIPTION)

    if tipoff_content.HOMEDESCRIPTION is not None:
        content = tipoff_content.HOMEDESCRIPTION
    elif tipoff_content.VISITORDESCRIPTION is not None: # todo test this for a few cases with the prints to makes sure only one description is populated
        content = tipoff_content.VISITORDESCRIPTION
    else:
        print('nothing for home or away, neutral said', tipoff_content.NEUTRALDESCRIPTION)

    if type == 10:
        pass
    if type == 7:
        pass

    tipoff_content_list = content.split(' ') # todo use a regex and not a split here ,i.e. violation
    # todo look at home vs. visitor for next action following index of first
    return tipoff_content_list


test_bad_data_games = [['199711110MIN', 'MIN', 'SAS'],
                        ['199711190LAL', 'LAL', 'MIN'],
                        ['201911200TOR', 'TOR', 'ORL'],
                        ['201911260DAL', 'DAL', 'LAC'],
                        ['199711240TOR'], ['199711270IND'], ['201911040PHO']]

for item in test_bad_data_games:
    item = item[0]
    date, team_code = getDashDateAndHomeCodeFromGameCode(item)
    test = getGameIdFromTeamAndDate(date, team_code)
    deb = getTipoffResults(test)
    print(deb)

# todo use this work to fill in the blanks on the missing games in the csv