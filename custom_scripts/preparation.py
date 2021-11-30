### Pipeline script for preparing data drior to model testing
from datetime import datetime
import sys
sys.path.append("..")

from sklearn.model_selection import train_test_split
import numpy as np
import pandas as pd
import math
from custom_scripts import weather

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

CATEGORICAL_FEATURES =[ "day_of_year", 
                        "day_of_week"]                              

OTHER_FEATURES = ['arr_time_sin',
                  'arr_time_cos',
                  'dep_time_sin',
                  'dep_time_cos']

def get_train_test_split(X:pd.DataFrame, y:pd.Series)-> list:
    """ Returns train_test_split using consntant values for test size and random state"""
    return train_test_split(X,y, test_size=TEST_SIZE, random_state=RANDOM_STATE)


def standardize_data(data_arr:list, scaler, 
        numeric_features:list = NUMERIC_FEATURES, 
        categorical_features:list = CATEGORICAL_FEATURES, 
        other_features:list = OTHER_FEATURES) -> list:
    """ Requires list of dataframe and scaler.  Optional arguments numeric_features and
        categorical_features for selecting specific features to standardize.
        returns list of dataframes with just categorical dummies
        and numeric features scaled to the first dataframe in the list
        Example: 
            standard_df_arr = standardize_data([df1,df2,df3], StandardScaler())"""
    try:
        if len(numeric_features) > 0:
            fitting_data = data_arr[0]
            scaler.fit(fitting_data[numeric_features])
    except Exception as e:
        print(f'Unable to fit scaler, are Dataframes given in list?:\n{e}')
        return None
    prepared_data_arr = []
    for df in data_arr:
        segments = []
        if len(other_features) > 0:
            segments.append(df[other_features])
        if len(numeric_features) > 0:
            segments.append(pd.DataFrame(scaler.transform(df[numeric_features]), columns=numeric_features, index=df.index))   
        if len(categorical_features) > 0: 
            segments.append(pd.get_dummies(df[categorical_features].astype(str)))
        prepared_data_arr.append(pd.concat(segments,1))
    return prepared_data_arr
      

def build_all_features(flight_data: pd.DataFrame) -> pd.DataFrame:
    """ Returns dataframe with all features added. """
    flight_data = build_historic_average_features(flight_data)
    flight_data = build_time_features(flight_data)
    flight_data = build_day_features(flight_data)
    flight_data = build_weather_features(flight_data)
    return flight_data


def build_historic_average_features(flight_data: pd.DataFrame) -> pd.DataFrame:
    """ Returns dataframe with added historic average features """
    average_delays = pd.read_csv('../data/preprocessing/averages_by_fl_num.csv')
    return pd.merge(flight_data.copy(), average_delays, on='op_carrier_fl_num')


def build_time_features(flight_data: pd.DataFrame) -> pd.DataFrame:
    """ Returns dataframe with added time sin/cos features """
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

def build_day_features(flight_data: pd.DataFrame) -> pd.DataFrame:
    """ Returns dataframe with added day of year and day of week features """
    flight_data = flight_data.copy()
    flight_data['day_of_year'] = pd.to_datetime(flight_data['fl_date']).dt.dayofyear
    flight_data['day_of_week'] = pd.to_datetime(flight_data['fl_date']).dt.dayofweek
    return flight_data


def build_weather_features(flight_data: pd.DataFrame) -> pd.DataFrame:
    """ Returns dataframe with added weather features """
    flight_data = flight_data.copy()
    # Read the relevant weather_all.csv into a dataframe
    weather_table = pd.read_csv('../data/Weather_data/weather_all.csv')
    weather_data = weather.get_weather( weather_table, 
                                        flight_data['fl_date'].min(), 
                                        flight_data['fl_date'].max())
    #renaming column to merge dataframes
    weather_data = weather_data.rename(columns = {'iata_code':'origin', 'StartTime(UTC)':'fl_date'})
    # Drop duplicates in the data frame
    weather_data = weather_data.drop_duplicates(['origin','fl_date','Severity','Type'])
    #Create dummies
    dummy_weather = weather_data.copy()
    # combine the UNK severity type with Other, simplifies, may also need the same code to convert NaNs
    dummy_weather = dummy_weather.replace('UNK','Other')
    severity_nums = {"Severity": {"Sunny": 0, "Other": 1, "Light": 2, "Moderate": 3, "Heavy": 4, "Severe": 5}} 
    dummy_weather = dummy_weather.replace(severity_nums)
    #Get dummies for the Type of weather
    dummy_weather = pd.get_dummies(dummy_weather,columns = ['Type'])
    #Merging with Test data to get sample final results
    flight_data = flight_data.merge(dummy_weather , how = 'left', on = ['origin', 'fl_date'])
    flight_data['Type_Rain'] = flight_data['Type_Rain'].fillna(0)
    return flight_data
    
# #For testing purposes, importing a file from training data (not on github)
# test = pd.read_csv('fl_samples.csv')
# weather = pd.read_csv('../../data/Weather_data/weather_all.csv')
# #Plug and play example, changing dates
# df_weather = weather.get_weather(weather,'2019-01-01','2019-01-31')
# df_weather = df_weather.rename(columns = {'iata_code':'origin', 'StartTime(UTC)':'fl_date'})
# df_weather = df_weather.drop_duplicates(['origin','fl_date','Severity','Type'])

# test.merge(df_weather , how = 'left', on = ['origin', 'fl_date'])
# df_dummy_weather = df_weather.copy()
# df_dummy_weather = df_dummy_weather.replace('UNK', 'Other')
# #replace severity as ranking, leave 0 for when you have NaN's as "Sunny" - Will be useful with NaNs
# severity_nums = {"Severity": {"Sunny": 0, "Other": 1, "Light": 2, "Moderate": 3, "Heavy": 4, "Severe": 5}} 
# df_dummy_weather = df_dummy_weather.replace(severity_nums)
# #Get dummies for the Type of weather
# df_dummy_final = pd.get_dummies(df_dummy_weather,columns = ['Type'])
# #Merging with Test data to get sample final results
# df1 = test.merge(df_dummy_final , how = 'left', on = ['origin', 'fl_date'])
# df1['Type_Rain'] = df1['Type_Rain'].fillna(0)