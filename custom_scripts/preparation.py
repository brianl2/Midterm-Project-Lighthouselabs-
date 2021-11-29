### Pipeline script for preparing data drior to model testing
from typing import Sequence
from sklearn.model_selection import train_test_split
import pandas as pd

RANDOM_STATE = 42
TEST_SIZE = 0.3

def get_train_test_split(X:pd.DataFrame, y:pd.Series)-> list:
    """ Returns train_test_split using consntant values for test size and random state"""
    return train_test_split(X,y, test_size=TEST_SIZE, random_state=RANDOM_STATE)