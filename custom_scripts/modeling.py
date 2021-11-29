#Script for streamlining model tests and saving/load models and their results to local drive 

from os import listdir
from os.path import isfile, join, exists
from typing import Dict
from numpy import mod
import pandas as pd
import sklearn
from datetime import datetime
import time
import pickle
from sklearn.base import is_classifier, is_regressor
from sklearn.metrics import (ConfusionMatrixDisplay, RocCurveDisplay,
                            f1_score, recall_score, precision_score, accuracy_score, 
                            r2_score, mean_squared_error, mean_absolute_error, explained_variance_score)
PICKLE_APPENDIX = 'pickle'
PICKLE_DIRECTORY = '../data/local/pickles/'
MODEL_RECORD_PATH = '../data/local/model_record.csv'

CLASSIFIER_METRICS = [f1_score, recall_score, precision_score, accuracy_score]
REGRESSOR_METRICS = [r2_score, mean_squared_error, mean_absolute_error, explained_variance_score]


def run_test(X_train:pd.DataFrame, X_test:pd.DataFrame, 
             y_train:pd.Series, y_test:pd.Series, 
             model: sklearn.base.BaseEstimator, notes:str="") -> sklearn.base.BaseEstimator:
    """
    Fits and tests a model, saving the results and pickled model to local directory for
    record keeping and returns model.
    
    Accepts optional notes argument for record keeping.
    
    Example:
    
    model = RandomForestClassifier(n_estimators=300)
    notes = 'n_estimators = 300'
    run_test(X_train, X_test, y_train, y_test, model, notes)
    """
    start_time = time.time()
    if not is_classifier(model) and not is_regressor(model):
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
    file_name = _next_file_index()
    record = {'model': model.__class__.__name__, 
              'notes': notes, 
              'training_time' : time.time() - start_time }
    record.update(_run_metrics(y_test, results, is_classifier(model)))
    # record['date_time'] = datetime.now()
    _save_record(record, file_name)
    _pickle(model, file_name)   

    return model 

def get_pickle(index:int) -> sklearn.base.BaseEstimator:
    """Retrieve pickle from local pickle directory by index
            Example:
            get_pickle(12) -> retrieves 12.pickle from local/pickles"""
    file_name = f'{index}.{PICKLE_APPENDIX}'
    save_file = open(PICKLE_DIRECTORY+file_name, 'rb')
    p = pickle.load(save_file)
    save_file.close()
    return p

def get_records() -> pd.DataFrame:
    return pd.read_csv('../data/local/model_record.csv', index_col=0)
    
def _pickle(model, file_name) -> None:
    """ save model as pickle to pickle directory"""
    save_file = open(PICKLE_DIRECTORY+file_name, 'wb')
    pickle.dump(model,save_file)
    save_file.close()
    


def _save_record(record, file_name) -> None:
    """ Save record to file """
    record_table = pd.DataFrame(record,[file_name])
    if exists(MODEL_RECORD_PATH):
        loaded_records = pd.read_csv(MODEL_RECORD_PATH, index_col=0)
        record_table = loaded_records.append(record_table)
    record_table.to_csv(MODEL_RECORD_PATH)
        
    
    
    
def _next_file_index() -> int:
    """
    Returns index for next file in local pickle directory
    """
    files = [f for f in listdir('../data/local/pickles') if isfile(join('../data/local/pickles', f))]
    if not files:
        return f'1.{PICKLE_APPENDIX}'
    indices = [int(x.split('.')[0]) for x in files]
    indices.sort()
    index = indices[-1]
    return f'{index+1}.{PICKLE_APPENDIX}'


def _run_metrics(true:pd.Series, guess:pd.Series, is_classifier:bool) -> Dict:
    """ 
    Runs scoring metrics and returns results
    """
    results = {}
    if is_classifier:
        for metric in CLASSIFIER_METRICS:
            try:
                ### Filter metrics to account for multiclass scenarios
                if not metric.__name__ == 'accuracy_score':
                    if len(set(guess)) > 2:
                        results[metric.__name__] = metric(true,guess, average='weighted')
                    else:
                        results[metric.__name__] = metric(true,guess)
                else:
                    results[metric.__name__] = metric(true,guess)
            except Exception as e:
                print(f'{metric.__name__} unable to score:\n{e}')
        ConfusionMatrixDisplay.from_predictions(true, guess)
    else:
        for metric in REGRESSOR_METRICS:
            try:
                results[metric.__name__] = metric(true,guess)
            except Exception as e:
                print(f'{metric.__name__} unable to score:\n{e}')
    print(results)
    return results