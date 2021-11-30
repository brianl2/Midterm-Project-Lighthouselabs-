### Pipeline script for preparing data drior to model testing
from sklearn.model_selection import train_test_split
import numpy as np
import pandas as pd
import math

RANDOM_STATE = 42
TEST_SIZE = 0.3

NUMERIC_FEATURES = [    "fl_num_avg_arr_delay",
                        "fl_num_avg_dep_delay",
                        "fl_num_avg_carrier_delay",
                        "fl_num_avg_weather_delay",
                        "fl_num_avg_nas_delay",
                        "fl_num_avg_security_delay",
                        "fl_num_avg_taxi_out",
                        "fl_num_avg_wheels_off", 
                        "fl_num_avg_wheels_on", 
                        "fl_num_avg_taxi_in", 
                        "fl_num_avg_crs_elapsed_time",
                        "fl_num_avg_actual_elapsed_time",
                        "fl_num_avg_air_time",
                        "fl_num_avg_late_aircraft_delay",
                        "fl_num_avg_total_add_gtime",
                        "fl_num_avg_longest_add_gtime"] 

CATEGORICAL_FEATURES =[]                              

OTHER_FEATURES = ['arr_time_sin',
                  'arr_time_cos',
                  'dep_time_sin',
                  'dep_time_cos']

def get_train_test_split(X:pd.DataFrame, y:pd.Series)-> list:
    """ Returns train_test_split using consntant values for test size and random state"""
    return train_test_split(X,y, test_size=TEST_SIZE, random_state=RANDOM_STATE)


def standardize_data(data_arr:list, scaler, 
        numeric_features:list = NUMERIC_FEATURES, categorical_features:list = CATEGORICAL_FEATURES) -> list:
    """ Requires list of dataframe and scaler.  Optional arguments numeric_features and
        categorical_features for selecting specific features to standardize.
        returns list of dataframes with just categorical dummies
        and numeric features scaled to the first dataframe in the list
        Example: 
            standard_df_arr = standardize_data([df1,df2,df3], StandardScaler())"""
    try:
        scaler.fit(data_arr[0][numeric_features])
    except Exception as e:
        print(f'Unable to fit scaler, are Dataframes given in list?:\n{e}')
        return None
    prepared_data_arr = []
    for df in data_arr:
        numeric = pd.DataFrame(scaler.transform(df[numeric_features]), columns=numeric_features)
        prepared_data_arr.append(numeric)
        # categorical =  pd.get_dummies(df[categorical_features])
        # prepared_data_arr.append(pd.merge(numeric,categorical))
    return prepared_data_arr
      


def build_all_features(flight_data: pd.DataFrame) -> pd.DataFrame:
    """ Returns dataframe with all features added. """
    flight_data = build_historic_average_features(flight_data)
    flight_data = build_time_features(flight_data)
    return flight_data


def build_historic_average_features(flight_data):
    """ Returns dataframe with added historic average features """
    average_delays = pd.read_csv('../data/preprocessing/averages_by_fl_num.csv')
    return pd.merge(flight_data.copy(), average_delays, on='op_carrier_fl_num')


def build_time_features(flight_data):
    flight_data = flight_data.copy()
    ### pad values
    flight_data['arrival_time'] = flight_data['crs_arr_time'].astype(str).str.zfill(4)
    flight_data['departure_time'] = flight_data['crs_dep_time'].astype(str).str.zfill(4)
    ### convert to datetime
    flight_data['arrival_time'] = pd.to_datetime(flight_data['arrival_time'], format = '%H%M', errors='coerce')
    flight_data['departure_time'] = pd.to_datetime(flight_data['departure_time'], format = '%H%M', errors='coerce')
    ### convert to minute of day
    flight_data['arrival_time'] = flight_data['arrival_time'].dt.hour * 60 + flight_data['arrival_time'].dt.minute
    flight_data['departure_time'] = flight_data['departure_time'].dt.hour * 60 + flight_data['departure_time'].dt.minute
    ### normalize with 2*PI
    flight_data['arrival_time'] = 2 * math.pi * flight_data['arrival_time'] / flight_data['arrival_time'].max()
    flight_data['departure_time'] = 2 * math.pi * flight_data['departure_time'] / flight_data['departure_time'].max()
    ### create sin feature
    flight_data['arr_time_sin'] = np.sin(flight_data['arrival_time'])
    flight_data['dep_time_sin'] = np.sin(flight_data['departure_time'])
    ### create cos feature
    flight_data['arr_time_cos'] = np.cos(flight_data['arrival_time'])
    flight_data['dep_time_cos'] = np.cos(flight_data['departure_time'])
    ### drop placeholder features
    flight_data.drop(['arrival_time','departure_time'],1,inplace=True)
    return flight_data