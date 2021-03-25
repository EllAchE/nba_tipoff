# https://xgboost.readthedocs.io/en/latest/
import warnings

import xgboost as xgb
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import log_loss

import ENVIRONMENT
from src.utils import customNbaSeasonFormatting
import pandas as pd
import matplotlib.pyplot as plt

alwaysDropList = ['Game Code', 'Full Hyperlink', 'Home', 'Away', 'Home Short', 'Away Short', 'Home Tipper', 'Away Tipper', 'First Scorer',
                    'Tip Winning Team', 'Tip Losing Team', 'Possession Gaining Player', 'Possession Gaining Player Link', 'First Scoring Team',
                    'Scored Upon Team', 'Tip Winner', 'Tip Winner Link', 'Tip Loser', 'Tip Loser Link', 'Tip Winner Scores', 'Home Scores',
                    'Home Tipper Wins', 'Away Tipper Wins']
# These columns in the dataframe will be ignored
gamesPlayed = ['Home Games Played', 'Away Games Played']
algos = ['Home TS Mu', 'Away TS Mu', 'Home TS Sigma', 'Away TS Sigma', 'Home Glicko Mu', 'Away Glicko Mu', 'Home Glicko Phi', 'Away Glicko Phi', 'Home Glicko Phi', 'Home Glicko Sigma', 'Away Glicko Sigma', 'Home Elo', 'Away Elo']
metaAlgos = ['Glicko Tip Win Prob', 'Glicko Difference', 'Elo Difference', 'TrueSkill Difference']
custom = ['Full_A_N_Adj', 'Full_H_N_Adj', 'Mid_A_N_Adj', 'Mid_H_N_Adj', 'Combined_Full_N_Adj']
fg = ['HOME_FG2A_FREQUENCY', 'AWAY_FG2A_FREQUENCY', 'HOME_FG_PCT', 'AWAY_FG_PCT']
rebounds = ['HOME_E_OREB_PCT', 'AWAY_E_OREB_PCT', 'AWAY_E_REB_PCT_RANK', 'HOME_E_REB_PCT_RANK', ]
advancedMetrics = ['AWAY_E_OFF_RATING', 'HOME_E_OFF_RATING', 'AWAY_E_OFF_RATING_RANK', 'HOME_E_OFF_RATING_RANK', 'AWAY_E_DEF_RATING_RANK', 'HOME_E_DEF_RATING_RANK', 'AWAY_E_DEF_RATING', 'HOME_E_DEF_RATING']
wins = ['HOME_W_PCT_RANK', 'AWAY_W_PCT_RANK']
turnovers = ['AWAY_E_TM_TOV_PCT', 'HOME_E_TM_TOV_PCT']
tips = ['Away Lifetime Appearances', 'Home Lifetime Appearances', 'Away Tipper Losses', 'Home Tipper Losses']
temp = ['HOME_W_PCT', 'AWAY_W_PCT', 'HOME_E_DREB_PCT', 'AWAY_E_DREB_PCT', 'HOME_E_REB_PCT', 'AWAY_E_REB_PCT', 'HOME_E_OREB_PCT_RANK', 'AWAY_E_OREB_PCT_RANK', 'HOME_FG2_PCT', 'AWAY_FG2_PCT', 'HOME_FG3_PCT', 'AWAY_FG3_PCT', 'HOME_FG3A_FREQUENCY', 'AWAY_FG3A_FREQUENCY']

testDropList = gamesPlayed + algos + custom + fg + rebounds + advancedMetrics + wins + turnovers + tips + temp + metaAlgos
dropList = alwaysDropList + testDropList

def getXGBoostVariablesALlML():
    with open('all_ml_cols.csv') as rFile:
        df = pd.read_csv(rFile)
    # df['Home Scores'] = df['Home Scores'].astype('category')
    # df['Home Scores'] = pd.to_numeric(df['Home Scores'])
    y = df['Home Scores']
    x = df.drop(dropList, axis=1)
    print('x columns', x.columns)
    return x, y

def getXGBoostVariablesSeason(season):
    seasonStr = customNbaSeasonFormatting(season)
    with open(ENVIRONMENT.SEASON_CSV_ML_COLS_UNFORMATTED_PATH.format(seasonStr)) as rFile:
        df = pd.read_csv(rFile)
    # df['Home Scores'] = df['Home Scores'].astype('category')
    df['Home Scores'] = pd.to_numeric(df['Home Scores'])
    y = df['Home Scores']
    x = df.drop(dropList, axis=1)
    print('x columns', x.columns)
    return x, y

def createClassifierAndReturnAssociatedData(x, y, params):
    xTrain, xTest, yTrain, yTest = train_test_split(x, y, test_size=0.2, random_state=123)
    xgClassifier = xgb.XGBClassifier(objective='binary:logistic', colsample_bytree=params['colsample_bytree'], max_depth=params['max_depth'], alpha=params['alpha'], n_estimators=10)
    xgClassifier.fit(xTrain, yTrain, verbose=1, eval_metric='logloss')
    predictions = xgClassifier.predict_proba(xTest)
    return xgClassifier, predictions, xTrain, xTest, yTrain, yTest

def customEvaluationMetrics(predictions, yTest):
    lenPred = len(predictions)
    totalMiss = 0
    expectedTotal = 0
    actualTotal = 0
    for i in range(0, lenPred-1):
        if yTest.iloc[i] == 1:
            totalMiss += 1 - predictions[i][1]
        elif yTest.iloc[i] == 0:
            totalMiss += predictions[i][0]
        else:
            raise ValueError("DDD")
        actualTotal += yTest.iloc[i]
        expectedTotal += predictions[i][1]

    logLoss = log_loss(yTest, predictions)

    print("Difference", totalMiss/lenPred)
    print('Expected', expectedTotal)
    print('Actual', actualTotal)
    print('bias?', expectedTotal/actualTotal)
    print("logLoss is", logLoss)

def crossValidation(dataDMatrix, hyperParams):
    crossValidationResults = xgb.cv(params=hyperParams, dtrain=dataDMatrix, nfold=3, num_boost_round=50, early_stopping_rounds=10,
                                    metrics="logloss", as_pandas=True, seed=123)
    print('Cross Validation head')
    print(crossValidationResults.head(5))
    print('Cross Validation tail')
    print(crossValidationResults.tail(5))

def XGBoost(season=None):
    # https://www.datacamp.com/community/tutorials/xgboost-in-python
    hyperParams = {"objective": "binary:logistic", 'colsample_bytree': 0.3, 'learning_rate': 0.1,
              'max_depth': 7, 'alpha': 5}

    x, y = getXGBoostVariablesALlML() if season is None else getXGBoostVariablesSeason(season)
    dataDMatrix = xgb.DMatrix(data=x, label=y, enable_categorical=True)
    xgClassifier, predictions, xTrain, xTest, yTrain, yTest = createClassifierAndReturnAssociatedData(x, y, hyperParams)

    customEvaluationMetrics(predictions, yTest)
    crossValidation(dataDMatrix, hyperParams)

    # gridSearchParams(xgClassifier, x, y)
    trainAndPlotVisualizations(dataDMatrix, hyperParams, xgClassifier)

def trainAndPlotVisualizations(dataDMatrix, hyperParams, xgClassifier=None):
    xgTrained = xgb.train(params=hyperParams, dtrain=dataDMatrix, num_boost_round=10)
    xgb.plot_tree(xgTrained,num_trees=0)
    plt.rcParams['figure.figsize'] = [50, 10]
    plt.show()

    xgb.plot_importance(xgTrained)
    plt.rcParams['figure.figsize'] = [50,50]
    plt.show()

    if xgClassifier is not None:
        plt.bar(range(len(xgClassifier.feature_importances_)), xgClassifier.feature_importances_)
        plt.show()

def gridSearchParams(estimator, x, y):
    warnings.filterwarnings("ignore")
    # https://www.analyticsvidhya.com/blog/2016/03/complete-guide-parameter-tuning-xgboost-with-codes-python/
    paramTest1 = {
        'max_depth': range(4, 10, 1),
        'min_child_weight': range(2, 6, 1),
        'alpha': range(5, 15, 1),
        'learning_rate': [0.1, 0.2]
    }
    # learning rate
    #    'gamma':
    #    'min_child_weight':
    # https://xgboost.readthedocs.io/en/latest/python/python_api.html search classifer
    # params defaults https://xgboost.readthedocs.io/en/latest/parameter.html
    #}

    gridSearchEstimator = GridSearchCV(estimator=estimator, param_grid=paramTest1)
    gridSearchEstimator.fit(x, y)
    print('line', gridSearchEstimator.best_params_, gridSearchEstimator.best_score_)
