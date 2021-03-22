# https://xgboost.readthedocs.io/en/latest/
# todo list of cols in docs and database creation
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import log_loss

import ENVIRONMENT
from src.utils import customNbaSeasonFormatting
import pandas as pd

dropList = ['Game Code', 'Full Hyperlink', 'Home', 'Away', 'Home Short', 'Away Short', 'Home Tipper', 'Away Tipper', 'First Scorer',
            'Tip Winning Team', 'Tip Losing Team', 'Possession Gaining Player', 'Possession Gaining Player Link', 'First Scoring Team',
            'Scored Upon Team', 'Tip Winner', 'Tip Winner Link', 'Tip Loser', 'Tip Loser Link', 'Tip Winner Scores', 'Home Scores']

# def specifyMLColumns(df):
#     return df

def getXGBoostVariables(season):
    seasonStr = customNbaSeasonFormatting(season)
    with open(ENVIRONMENT.SEASON_CSV_ML_COLS_UNFORMATTED_PATH.format(seasonStr)) as rFile:
        df = pd.read_csv(rFile)
    # df['Home Scores'] = df['Home Scores'].astype('category')
    df['Home Scores'] = pd.to_numeric(df['Home Scores'])
    y = df['Home Scores']
    x = df.drop(dropList, axis=1)
    return x, y

def XGBoost(season):
    # https://www.datacamp.com/community/tutorials/xgboost-in-python
    x, y = getXGBoostVariables(season)
    # dataDMatrix = xgb.DMatrix(data=x, label=y, enable_categorical=True)
    xTrain, xTest, yTrain, yTest = train_test_split(x, y, test_size=0.2, random_state=123)
    xgClassifier = xgb.XGBClassifier(objective='binary:logistic', colsample_bytree=0.3, max_depth=5, alpha=10, n_estimators=10)

    xgClassifier.fit(xTrain, yTrain)
    predictions = xgClassifier.predict(xTest)
    lenPred = len(predictions)
    totalMiss = 0
    for i in range(0, lenPred-1):
        totalMiss += abs(yTest.iloc[i] - predictions[i])
    print("Difference", totalMiss/lenPred)
    logLoss = log_loss(yTest, predictions)
    print("logLoss with base XGBoost is", logLoss)
    # todo visualize xgboost

    # params = {"objective": "reg:linear", 'colsample_bytree': 0.3, 'learning_rate': 0.1,
    #           'max_depth': 5, 'alpha': 10}
    #
    # cv_results = xgb.cv(dtrain=dataDMatrix, params=params, nfold=3, num_boost_round=50, early_stopping_rounds=10, metrics="log_loss", as_pandas=True, seed=123)
