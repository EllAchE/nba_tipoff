# https://xgboost.readthedocs.io/en/latest/
# todo list of cols in docs and database creation
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import log_loss

import ENVIRONMENT
from src.utils import customNbaSeasonFormatting
import pandas as pd

dropList = ['Home Scores', 'Game Code']

def getXGBoostVariables(season):
    seasonStr = customNbaSeasonFormatting(season)
    with open(ENVIRONMENT.SEASON_CSV_ML_COLS_UNFORMATTED_PATH.format(seasonStr)) as rFile:
        df = pd.read_csv(rFile)
    y = df['Home Scores']
    x = df.drop([dropList], axis=1)
    return x, y

def XGBoost(season):
    # https://www.datacamp.com/community/tutorials/xgboost-in-python
    x, y = getXGBoostVariables(season)
    dataDMatrix = xgb.DMatrix(data=x, label=y)
    xTrain, xTest, yTrain, yTest = train_test_split(x, y, test_size=0.2, random_state=123)
    xgClassifier = xgb.XGBClassifier(objective='reg:linear', colsample_bytree=0.3, max_depth=5, alpha=10, n_estimators=10)

    xgClassifier.fit(xTrain, yTrain)
    predictions = xgClassifier.predict(xTest)
    logLoss = log_loss(yTest, predictions)
    print("logLoss with base XGBoost is", logLoss)

    params = {"objective": "reg:linear", 'colsample_bytree': 0.3, 'learning_rate': 0.1,
              'max_depth': 5, 'alpha': 10}

    cv_results = xgb.cv(dtrain=dataDMatrix, params=params, nfold=3, num_boost_round=50, early_stopping_rounds=10, metrics="log_loss", as_pandas=True, seed=123)
