#Script for streamlining model tests and saving/load models and their results to local drive 

from os import listdir
from os.path import isfile, join
from typing import Dict
import pandas as pd
import sklearn
from datetime import datetime
import time
import pickle
from sklearn.base import is_classifier, is_regressor
from sklearn.metrics import (ConfusionMatrixDisplay, RocCurveDisplay,
                            f1_score, recall_score, precision_score, accuracy_score,
                            mean_squared_error, mean_absolute_error, explained_variance_score)

CLASSIFIER_METRICS = [f1_score, recall_score, precision_score]
REGRESSOR_METRICS = [mean_squared_error, mean_absolute_error, explained_variance_score]


def run_test(X_train:pd.DataFrame, X_test:pd.DataFrame, 
             y_train:pd.Series, y_test:pd.Series, 
             model: sklearn.base.BaseEstimator, notes:str="") -> sklearn.base.BaseEstimator:
    """
    Fits and tests a model, saving the results and model pickle to local directory for record,
    and returns model.
    
    Accepts optional notes argument for record keeping.
    
    Example:
    
    model = RandomForestClassifier(n_estimators=300)
    notes = 'n_estimators = 300'
    run_test(X_train, X_test, y_train, y_test, model, notes)
    """
    start_time = time.time()
    if not model.is_classifier() and not model.is_regressor():
        print("run_test only accepts SKlearn regression and classifier models")
        return None
    try:
        model.fit(X_train, y_train)
    except Exception as e:
        print(f'Unable to fit model:\n{e}')
        return None
    try:
        results = model.predict(X_test)
    except Exception as e:
        print(f'Unable to predit sample:\n{e}')
        return None
    execution_time = time.time() - start_time
    
    record = _calculate_results(y_test, results, model.is_classifier())
    record['notes'] = notes
    record['executrion_time'] = execution_time
    record['date_time'] = datetime.now()
    record['file_name'] = _next_file_index()   

    return model 
    
    
def _next_file_index() -> int:
    """
    Returns index for next file in local pickle directory
    """
    files = [f for f in listdir('../data/local/pickles') if isfile(join('../data/local/pickles', f))]
    files.sort()
    index = int(files[-1].split('.')[0])
    appendix = files[-1].split('.')[1]
    return f'{index+1}.{appendix}'


def _calculate_results(true:pd.Series, guess:pd.Series, is_classifier:bool) -> Dict:
    """ 
    Runs scoring metrics and returns results
    """
    results = {}
    if is_classifier:
        for metric in CLASSIFIER_METRICS:
            results[metric.__name__] = metric(true,guess)
        RocCurveDisplay.from_predictions(true, guess)
    else:
        for metric in REGRESSOR_METRICS:
            results[metric.__name__] = metric(true,guess)
        ConfusionMatrixDisplay.from_predictions(true, guess)
    return results