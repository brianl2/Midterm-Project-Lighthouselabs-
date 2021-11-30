### Pipeline script for preparing data drior to model testing
from typing import Sequence
from pandas.core.arrays import categorical
from sklearn.model_selection import train_test_split
import pandas as pd

RANDOM_STATE = 42
TEST_SIZE = 0.3

NUMERIC_FEATURES = [    "fl_num_avg_arr_delay",
                        "fl_num_avg_dep_delay",
                        "fl_num_carrier_delay",
                        "fl_num_weather_delay",
                        "fl_num_avg_nas_delay",
                        "fl_num_security_delay",
                        "fl_num_taxi_out",
                        "fl_num_wheels_off", 
                        "fl_num_wheels_on", 
                        "fl_num_taxi_in", 
                        "fl_num_crs_elapsed_time",
                        "fl_num_actual_elapsed_time",
                        "fl_num_air_time",
                        "fl_num_late_aircraft_delay",
                        "fl_num_total_add_gtime",
                        "fl_num_longest_add_gtime"] 
CATEGORICAL_FEATURES =[]                              


def get_train_test_split(X:pd.DataFrame, y:pd.Series)-> list:
    """ Returns train_test_split using consntant values for test size and random state"""
    return train_test_split(X,y, test_size=TEST_SIZE, random_state=RANDOM_STATE)


def standardize_data(data_arr:list, scaler, 
        numeric_features:list = NUMERIC_FEATURES, categorical_features:list = CATEGORICAL_FEATURES) -> list:
    """ Requires list of dataframe and scaler.  Optional arguments numeric_features and
        categorical_features for selecting specific features to standardize.
        returns list of dataframes with just categorical dummies
        and numeric features scaled to the first dataframe in the list"""
    try:
        scaler.fit(for_scaling = data_arr[0][NUMERIC_FEATURES])
    except Exception as e:
        print(f'Unable to fit scaler:\n{e}')
        return None
    prepared_data_arr = ()
    for df in data_arr:
        numeric = scaler.transform(df[NUMERIC_FEATURES])
        categorical =  pd.get_dummies(df[CATEGORICAL_FEATURES])
        prepared_data_arr.append(pd.merge(numeric,categorical))
    
    
    

    
    


def build_all_features(flight_data: pd.DataFrame) -> pd.DataFrame:
    """ Returns dataframe with all features added. """
    flight_data = build_all_features(flight_data.copy())
    


def build_historic_average_features(flight_data):
    """ Returns dataframe with added historic average features """
    average_delays = pd.read_csv('../../data/preprocessing/averages_by_fl_num.csv')
    return pd.merge(flight_data.copy(), average_delays, on='op_carrier_fl_num')




