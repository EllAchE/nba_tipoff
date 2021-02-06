import json
import csv
import pandas as pd

from bs4 import BeautifulSoup
import requests
import time
import random
import re

# todo historical betting lines
# https://widgets.digitalsportstech.com/api/gp?sb=bovada&tz=-5&gameId=in,135430


def getSingleSeasonGameHeaders(season):
    normal_months = ["october", "november", "december", "january", "february", "march", "april", "may", "june"]
    months_2020 = ["october-2019", "november", "december", "january", "february", "march", "july", "august",
                   "september", "october-2020"]
    months_2021 = ["december", "january", "february", "march"]  # may be a shortened season

    season_games = list()
    if season == 2020:
        months = months_2020
    elif season == 2021:
        months = months_2021
    else:
        months = normal_months
    for month in months:
        games_list = getSingleMonthGameHeaders(season, month)
        for game in games_list:
            season_games.append(game)

    return season_games


def getSingleMonthGameHeaders(season, month):
    url = 'https://www.basketball-reference.com/leagues/NBA_{}_games-{}.html'.format(season, month)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    table_game_strs = soup.find_all('th', class_="left")
    table_away_strs = soup.select('td[Data-stat="visitor_team_name"]')
    table_home_strs = soup.select('td[Data-stat="home_team_name"]')

    month_games = list()
    list_len = len(table_game_strs)
    i = 0
    while i < list_len - 1:
        i += 1
        month_games.append(getSingleGameHeaders(table_game_strs, table_home_strs, table_away_strs, i))

    return month_games


def getSingleGameHeaders(table_game_strs, table_home_strs, table_away_strs, i):
    game_str = str(table_game_strs[i])
    away_str_full = str(table_away_strs[i].a.contents[0])
    home_str_full = str(table_home_strs[i].a.contents[0])

    s_index = game_str.index('csk="') + 5
    away_str_short = str(table_away_strs[i])[s_index:s_index + 3]
    home_str_short = str(table_home_strs[i])[s_index:s_index + 3]

    game_short = game_str[s_index:s_index + 12]
    game_long = 'https://www.basketball-reference.com/boxscores/pbp/' + game_short + '.html'

    return [game_short, game_long, home_str_full, away_str_full, home_str_short, away_str_short]


def sleep_checker(sleep_counter, iterations=3, base_time=2, random_multiplier=3):
    sleep_counter += 1
    if sleep_counter % iterations == 0:
        print("sleeping for", str(base_time), "+ random seconds")
        time.sleep(base_time + random.random() * random_multiplier)
        sleep_counter = 0
    return sleep_counter


def getPlayerTeamInSeason(player_link, season, long_code=True):
    if long_code:
        player_link = player_link[11:]
    with open('../Data/player_team_pairs.json') as team_pairs:
        seasons = json.load(team_pairs)
        try:
            return seasons[str(season)][player_link]
        except:
            return player_link


def conditionalDataChecks(home_team, away_team, tipper1, tipper2, tipper1_link, tipper2_link, possession_gaining_player_link, first_scoring_player_link, season):
    if home_team in getPlayerTeamInSeason(tipper1_link, season):
        home_tipper = tipper1
        away_tipper = tipper2
        home_tipper_link = tipper1_link
        away_tipper_link = tipper2_link
    else:
        home_tipper = tipper2
        away_tipper = tipper1
        home_tipper_link = tipper2_link
        away_tipper_link = tipper1_link

    if home_team in getPlayerTeamInSeason(possession_gaining_player_link, season):
        possession_gaining_team = home_team
        possession_losing_team = away_team
        tip_winner = home_tipper
        tip_loser = away_tipper
        tip_winner_link = home_tipper_link
        tip_loser_link = away_tipper_link
    else:
        possession_gaining_team = away_team
        possession_losing_team = home_team
        tip_winner = away_tipper
        tip_loser = home_tipper
        tip_winner_link = away_tipper_link
        tip_loser_link = home_tipper_link

    if home_team in getPlayerTeamInSeason(first_scoring_player_link, season):
        first_scoring_team = home_team
        scored_upon_team = away_team
    else:
        first_scoring_team = away_team
        scored_upon_team = home_team

    if possession_gaining_team == first_scoring_team:
        tip_win_score = 1
    else:
        tip_win_score = 0

    return home_tipper, away_tipper, home_tipper_link, away_tipper_link, possession_gaining_team, possession_losing_team, tip_winner,\
           tip_loser, tip_winner_link, tip_loser_link, first_scoring_team, scored_upon_team, tip_win_score


def getTipWinnerAndFirstScore(game_link, season, home_team, away_team):
    # https://www.basketball-reference.com/boxscores/pbp/201901220OKC.html
    url = 'https://www.basketball-reference.com/boxscores/pbp/{}.html'.format(game_link)
    page = requests.get(url)
    print("GET request for game", game_link, "returned status", page.status_code)

    soup = BeautifulSoup(page.content, 'html.parser')
    # table = soup.select('table[id="pbp"]')
    possession_win_line = soup.select('td[colspan="5"]')[0].contents

    if str(possession_win_line[0]) == "Start of 1st quarter":
        possession_win_line = soup.select('td[colspan="5"]')[1].contents

    first_score_line_options = soup.find_all('td', class_='bbr-play-score', limit=2)[:2]
    if re.search(r'makes', str(first_score_line_options[0])) is not None:
        first_score_line = first_score_line_options[0].contents
    else:
        first_score_line = first_score_line_options[1].contents

    def pNameAndCode(tag):
        return tag.contents[0], re.search(r'(?<=")(.*?)(?=")', str(tag)).group(0)

    first_scoring_player, first_scoring_player_link = pNameAndCode(first_score_line[0])
    try:
        tipper1, tipper1_link = pNameAndCode(possession_win_line[1])
        tipper2, tipper2_link = pNameAndCode(possession_win_line[3])
        possessing_player, possessing_player_link = pNameAndCode(possession_win_line[5])

        home_tipper, away_tipper, home_tipper_link, away_tipper_link,  tip_win_team, tip_losing_team, tip_winner, tip_loser,\
        tip_winner_link, tip_loser_link, first_scoring_team, scored_upon_team, tip_win_score = conditionalDataChecks(
            home_team, away_team, tipper1, tipper2, tipper1_link, tipper2_link, possessing_player_link,
            first_scoring_player_link, season)

        return [home_tipper, home_tipper_link, away_tipper, away_tipper_link, first_scoring_player, tip_win_team,
                tip_losing_team, possessing_player, possessing_player_link, first_scoring_team, scored_upon_team,
                tip_winner, tip_winner_link, tip_loser, tip_loser_link, tip_win_score]
    except:
        return [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]


def getSingleTeamOffDefData(row, season):
    def_rate = row.contents[-1].contents[0]
    off_rate = row.contents[-2].contents[0]
    orr = row.contents[5].contents[0]
    drr = row.contents[6].contents[0]
    rebr = row.contents[7].contents[0]
    eff_fg = row.contents[8].contents[0]
    team_name = row.contents[1].contents[0].contents[0]

    return team_name, {"team": team_name, "orr": orr, "drr": drr, "rebr": rebr, "eff_fg": eff_fg, "off_rate": off_rate, "def_rate": def_rate, "season": season}


def getOffDefRatings(season=None, save_path=None):
    if season is not None:
        url = 'http://www.espn.com/nba/hollinger/teamstats/_/year/'.format(season)
    else:
        url = 'http://www.espn.com/nba/hollinger/teamstats'
        season = 2021
    # http://www.espn.com/nba/hollinger/teamstats/_/year/2020
    response = requests.get(url)
    print('GET to', url, 'returned status', response.status_code)
    soup = BeautifulSoup(response.content, 'html.parser')

    season_dict = {}
    season_dict['season'] = season
    rows = soup.select('tr[class*="row team-"]')

    for row in rows:
        team_name, team_stats = getSingleTeamOffDefData(row, season)
        season_dict[team_name] = team_stats

    if save_path is not None:
        with open(save_path, 'w') as json_f:
            json.dump(season_dict, json_f)

    return season_dict


def correctBlanksInTable(): #todo fix this
    pass


def oneSeason(season, path):
    temp = pd.DataFrame()
    temp.to_csv(path)
    data_file = open(path, 'w')

    with data_file:
        csv_writer = csv.writer(data_file)
        csv_writer.writerow(
            ['Game Code', 'Full Hyperlink', 'Home', 'Away', 'Home Short', 'Away Short', 'Home Tipper', 'Away Tipper',
             'First Scorer', 'Tip Winning Team', 'Tip Losing Team', 'Possession Gaining Player', 'Possession Gaining Player Link',
             'First Scoring Team', 'Scored Upon Team', 'Tip Winner', 'Tip Winner Link', 'Tip Loser',
             'Tip Loser Link', 'Tip Winner Scores'])
        game_headers = getSingleSeasonGameHeaders(season)

        sleep_counter = 0
        for line in game_headers:
            sleep_counter = sleep_checker(sleep_counter, iterations=16, base_time=0, random_multiplier=1)
            try:
                row = line + getTipWinnerAndFirstScore(line[0], season, line[4], line[5])
                print(row)
                csv_writer.writerow(row)
            except:
                break


def getHistoricalDataRunnerExtraction():
    start_season = 2021

    # sss = [1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021]
    #
    # for start_season in sss:

    all_at_once_path = "tip_and_first_score_details_starting_" + str(start_season) + "_season.csv"
    single_season_path = "tip_and_first_score_details_" + str(start_season) + "_season.csv"

    oneSeason(start_season, single_season_path)

test_bad_data_games = [['199711110MIN', 'MIN', 'SAS'],
                       ['199711160SEA', 'SEA', 'MIL'],
                        ['199711190LAL', 'LAL', 'MIN'],
                        ['201911200TOR', 'TOR', 'ORL'],
                        ['201911260DAL', 'DAL', 'LAC']] # Last one is a violation, others are misformatted
# '199711210SEA', '199711240TOR', '199711270IND', '201911040PHO',
#