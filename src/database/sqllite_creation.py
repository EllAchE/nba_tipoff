# https://docs.python.org/3/library/sqlite3.html
import ENVIRONMENT
import pandas as pd


def addExtraUrlToPlayerLinks():
    for season in ENVIRONMENT.ALL_SEASONS_LIST:
        df = pd.read_csv(ENVIRONMENT.SEASON_CSV_UNFORMATTED_PATH.format(season))
    for i in range(0, len(df['Game Code']) - 1):
        temp = df['Tip Winner Link'].iloc[i]
        if "players/" not in temp:
            df.at[i, 'Tip Winner Link'] =  "/players/" + temp[0] + "/" + temp
            temp2 = df['Tip Loser Link'].iloc[i]
            df.at[i, 'Tip Loser Link'] = "/players/" + temp2[0] + "/" + temp2