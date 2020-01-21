import pickle
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import log_loss
from sklearn.metrics import roc_auc_score
import numpy as np
import time
import scipy.stats as stats
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.linear_model import LinearRegression
from scipy import stats
from sklearn.metrics import log_loss
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
import matplotlib.pyplot as plt
from sklearn.metrics import (brier_score_loss, precision_score, recall_score,
                             f1_score)

"""
This code performs cross validation on the RF model generated by
Hal_RF_model_fit.py
"""

model_RF_best_2 = pickle.load(open('/home/jallen17/CPRHD_SES/RF_agg_model_fit', 'rb')) # change this line to select the fit model

time_start = time.time()
data = pd.read_csv('/home/shared/cprhd/DATA_CPRHD_SES/Agg_mirdata.csv',index_col = False)  # Need to edit this line same as fit
print("Data read in:", time.time() - time_start)
agg = data.drop(columns= data.columns[[1,5,7,6,8,9,10,11,12,15,16,17,18,-1,-6]])
agg.iloc[3900]['wnvbinary'] = 1 # Only exceptions
agg_wnv = agg[agg.wnvbinary == 1]
agg_0 = agg[agg.wnvbinary == 0]
l = []
for x in agg.columns:
    print(x + ': ' + str(stats.ks_2samp(agg_wnv[x], agg_0[x])[1]))
    value = stats.ks_2samp(agg_wnv[x], agg_0[x])[1]
    if(value < 0.01):
        l.append(x)
data = agg[l]
x_selected = data.drop(columns = 'wnvbinary')
y_selected = data['wnvbinary'].values

trainX_sel, testX_sel, trainY_sel, testY_sel = train_test_split(x_selected, y_selected, test_size=0.2, random_state=1) # CV
print("data split:", time.time() - time_start)

param_grid = {
    'bootstrap': [True],
    'max_depth': [50,100],
    'max_features': ['sqrt'],
    'min_samples_leaf': [6, 12],
    'min_samples_split': [4,8],
    'n_estimators': [1200]
} 


CV_model_RF_3 = GridSearchCV(model_RF_best_2, param_grid, scoring='neg_log_loss', cv=5)
print("CV model parameterized:", time.time() - time_start)

time_start = time.time()
CV_model_RF_3.fit(trainX_sel, trainY_sel)
print("CV model fit:", time.time() - time_start)

pickle.dump(CV_model_RF_3, open('RF_agg_model_CV_final', 'wb'))

def model_RF_test(model_RF, dataX, dataY, selectedX):
    print("Model performance")
    predict_data = model_RF.predict_proba(dataX)

    # Some stats
    print("Feature Importance : ")
    feature_importances = pd.DataFrame(model_RF.feature_importances_, index = selectedX.columns, columns=['importance'])
    print(model_RF.best_estimator_.feature_importances_)
    print("Total number of WNV occurrence in test set : " + str(len(dataY[dataY > 0])))

    print("Number of WNV occurrence the model is able to capture in test set:" + str(
        dataY[np.where(predict_data[:, 1] > 0)].sum()))

    print("Log loss : " + str(log_loss(dataY, predict_data)))
 
    print("AUC: " + str(roc_auc_score(dataY, predict_data[:,1])))

    print(
        "This is to test the performance of random forest model, ideally, the logloss is low and also it is able to "
        "capture most of the WNV occurrence")

    return None  # Check how many wnv it predicts

model_RF_test(CV_model_RF_3,testX_sel,testY_sel,x_selected)





