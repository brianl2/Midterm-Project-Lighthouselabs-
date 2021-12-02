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
                        "fl_num_avg_late_aircraft_delay",
                        'fl_num_avg_taxi_out',
                        'tail_num_avg_arr_delay', 
                        'tail_num_avg_dep_delay',
                        'tail_num_avg_taxi_out',
                        "tail_num_avg_late_aircraft_delay",
                        'carrier_avg_arr_delay', 
                        'carrier_avg_dep_delay',
                        'carrier_avg_carrier_delay', 
                        'dest_avg_arr_delay', 
                        'dest_avg_dep_delay',
                        'dest_avg_taxi_in', 
                        'origin_avg_arr_delay', 
                        'origin_avg_dep_delay',
                        'origin_avg_taxi_out', 
                        'distance',
                        'crs_elapsed_time',
                        'origin_cold', 
                        'origin_fog',
                        'origin_hail',
                        'origin_rain',
                        'origin_snow',
                        'origin_storm',
                        'dest_cold', 
                        'dest_fog',
                        'dest_hail',
                        'dest_rain',
                        'dest_snow',
                        'dest_storm' ] 

CATEGORICAL_FEATURES =[  "day_of_week"]                              

OTHER_FEATURES = [      'arr_time_sin',
                        'arr_time_cos',
                        'dep_time_sin',
                        'dep_time_cos',
                        'is_holiday']

def get_train_test_split(X:pd.DataFrame, y:pd.Series)-> list:
    """ Returns train_test_split using consntant values for test size and random state"""
    return train_test_split(X,y, test_size=TEST_SIZE, random_state=RANDOM_STATE)


def standardize_data(data_arr:list, scaler, 
        numeric_features:list = NUMERIC_FEATURES, 
        categorical_features:list = CATEGORICAL_FEATURES, 
        other_features:list = OTHER_FEATURES) -> list:
    """ Fits scaler to first dataframe on list, and returns 
        dataframes after transforming with scaler.
        Example: 
            standard_df_arr = standardize_data([df1,df2,df3], StandardScaler())"""
    ### Clean feature lists to not look for features that are absent
    numeric_features  = [f for f in numeric_features if f in data_arr[0].columns]
    categorical_features  = [f for f in categorical_features if f in data_arr[0].columns]
    other_features  = [f for f in other_features if f in data_arr[0].columns]
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
    fl_num = pd.read_csv('../data/preprocessing/averages_by_fl_num.csv')
    tail = pd.read_csv('../data/preprocessing/averages_by_tail_num.csv')
    carrier = pd.read_csv('../data/preprocessing/averages_by_carrier.csv')
    dest = pd.read_csv('../data/preprocessing/averages_by_dest.csv')
    origin = pd.read_csv('../data/preprocessing/averages_by_origin.csv')
    flight_data = flight_data.copy()
    all_features = NUMERIC_FEATURES.copy()
    all_features.append('op_carrier_fl_num')
    fl_num_features  = [f for f in all_features if f in fl_num.columns]
    flight_data = pd.merge(flight_data, fl_num[fl_num_features], on='op_carrier_fl_num')
    
    all_features.append('tail_num')
    tail_features  = [f for f in all_features if f in tail.columns]
    flight_data = pd.merge(flight_data, tail[tail_features], on='tail_num')
    
    all_features.append('op_unique_carrier')
    carrier_features  = [f for f in all_features if f in carrier.columns]
    flight_data = pd.merge(flight_data, carrier[carrier_features], on='op_unique_carrier')
    
    all_features.append('dest')
    dest_features  = [f for f in all_features if f in dest.columns]
    flight_data = pd.merge(flight_data, dest[dest_features], on='dest')
    
    all_features.append('origin')
    origin_features  = [f for f in all_features if f in origin.columns]
    flight_data = pd.merge(flight_data, origin[origin_features], on='origin')
    return flight_data

  

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
    """ Returns dataframe with added calendar features """
    #TODO: add "is_holiday" feature
    flight_data['day_of_week'] = pd.to_datetime(flight_data['fl_date']).dt.dayofweek
    return flight_data

def build_weather_features(flight_data: pd.DataFrame) -> pd.DataFrame:
    """ Returns dataframe with added weather features """
    flight_data = flight_data.copy()
    weather_table = pd.read_csv('../data/Weather_data/weather_all.csv')
    # Clean table
    weather_table = weather_table[weather_table['Type'].notna()]
    weather_table.drop('AirportCode', 1, inplace= True)
    weather_table.rename(columns={"StartTime(UTC)": 'fl_date', 
                            'iata_code': 'origin'}, inplace= True)
    # convert Severity to numeric scale
    weather_table = weather_table.replace({"Severity": { "Sunny": 0, 
                                                "Other": 1, 
                                                "Light": 2, 
                                                "Moderate": 3, 
                                                "Heavy": 4, 
                                                "Severe": 5, 
                                                "UNK": 1, 
                                                np.nan: 1   }} )
    ### Create 0-5 value for each weather type at origin and destination
    for weather in weather_table['Type'].unique():
        #Remove duplicates
        table = weather_table[weather_table['Type'] == weather].sort_values('Severity', ascending=False).drop_duplicates(['origin','fl_date','Type'])
        f1 = 'origin_'+weather.lower()
        f2 = 'dest_'+weather.lower()
        #Origin weather
        table.rename(columns={"Severity": f1}, inplace=True)
        flight_data = pd.merge(flight_data, table[[f1,'origin','fl_date']], how='left')
        flight_data[f1] = flight_data[f1].fillna(0)
        #Destination weather
        table.rename(columns={"origin": 'dest', f1: f2}, inplace=True)
        flight_data = pd.merge(flight_data, table[[f2,'dest','fl_date']], how='left')
        flight_data[f2] = flight_data[f2].fillna(0)
    return flight_data