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
                        "fl_num_avg_longest_add_gtime",
                        'Severity', 
                        'distance',
                        'crs_elapsed_time'] 

CATEGORICAL_FEATURES =[ "day_of_year", 
                        "day_of_week"]                              

OTHER_FEATURES = ['arr_time_sin',
                  'arr_time_cos',
                  'dep_time_sin',
                  'dep_time_cos',
                  'Cold', 
                  'Fog',
                  'Hail',
                  'Precipitation',
                  'Rain',
                  'Snow',
                  'Storm']

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
    ### change 2400 to 0000 to avoid nans
    flight_data['crs_arr_time'].replace({2400:0000},inplace=True)
    flight_data['crs_dep_time'].replace({2400:0000},inplace=True)
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
    # Clean table
    weather_table = weather_table[weather_table['Type'].notna()]
    weather_table.drop('AirportCode', 1, inplace= True)
    weather_table.rename(columns={"StartTime(UTC)": 'fl_date', 
                                'iata_code': 'origin'}, inplace= True)
    # Build and merge severity table
    severity = weather_table.replace({"Severity": { "Sunny": 0, 
                                                    "Other": 1, 
                                                    "Light": 2, 
                                                    "Moderate": 3, 
                                                    "Heavy": 4, 
                                                    "Severe": 5, 
                                                    "UNK": 1, 
                                                    np.nan: 1   }} )
    severity.drop('Type',1,inplace=True)
    severity
    severity = severity.sort_values('Severity', ascending=False).drop_duplicates(['origin','fl_date'])
    flight_data = pd.merge(flight_data, severity, how='left')
    flight_data['Severity'] = flight_data['Severity'].fillna(0)
    # Build and merge weather tables
    weather_table = weather_table.drop('Severity', 1)
    weather_table['Type'].unique()    
    for weather in weather_table['Type'].unique():
        table = weather_table[weather_table['Type'] == weather].drop_duplicates(['origin','fl_date','Type'])
        table['Type'] = 1
        table.rename(columns={"Type": weather}, inplace=True)
        flight_data = pd.merge(flight_data, table, how='left')
        flight_data[weather] =flight_data[weather].fillna(0)
    return flight_data

# def build_weather_features(flight_data: pd.DataFrame) -> pd.DataFrame:
#     """ Returns dataframe with added weather features """
#     flight_data = flight_data.copy()
#     # Read the relevant weather_all.csv into a dataframe
#     weather_table = pd.read_csv('../data/Weather_data/weather_all.csv')
#     weather_data = weather.get_weather( weather_table, 
#                                         flight_data['fl_date'].min(), 
#                                         flight_data['fl_date'].max())
#     #renaming column to merge dataframes
#     weather_data = weather_data.rename(columns = {'iata_code':'origin', 'StartTime(UTC)':'fl_date'})
#     # Drop duplicates in the data frame
#     weather_data = weather_data.drop_duplicates(['origin','fl_date','Severity','Type'])
#     #Create dummies
#     dummy_weather = weather_data.copy()
#     # combine the UNK severity type with Other, simplifies, may also need the same code to convert NaNs
#     dummy_weather = dummy_weather.replace('UNK','Other')
#     severity_nums = {"Severity": {"Sunny": 0, "Other": 1, "Light": 2, "Moderate": 3, "Heavy": 4, "Severe": 5}} 
#     dummy_weather = dummy_weather.replace(severity_nums)
#     #Get dummies for the Type of weather
#     dummy_weather = pd.get_dummies(dummy_weather,columns = ['Type'])
#     #Merging with Test data to get sample final results
#     flight_data = flight_data.merge(dummy_weather , how = 'left', on = ['origin', 'fl_date'])
#     flight_data['Type_Rain'] = flight_data['Type_Rain'].fillna(0)
#     flight_data['Type_Hail'] = flight_data['Type_Hail'].fillna(0)
#     flight_data['Type_Cold'] = flight_data['Type_Cold'].fillna(0)
#     flight_data['Type_Fog'] = flight_data['Type_Fog'].fillna(0)
#     flight_data['Type_Snow'] = flight_data['Type_Snow'].fillna(0)
#     flight_data['Type_Storm'] = flight_data['Type_Storm'].fillna(0)
#     flight_data['Type_Precipitation'] = flight_data['Type_Precipitation'].fillna(0)
#     flight_data['Severity'] = flight_data['Severity'].fillna(0)
#     return flight_data