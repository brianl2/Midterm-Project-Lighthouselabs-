#Script for assembling features prior to engineering and preparation
import sys
sys.path.append("..")

from custom_scripts import database
import pandas as pd


# Default features to select for when pulling samples from database
PRIMARY_FEATURES =  """ fl_date, 
                        op_unique_carrier, 
                        tail_num, 
                        op_carrier_fl_num, 
                        origin_airport_id, 
                        dest_airport_id, 
                        crs_dep_time,
                        crs_arr_time, 
                        crs_elapsed_time, 
                        dup, 
                        flights, 
                        distance,
                        arr_delay
                    """

### Dates to select from database. Value is a string in the format of yyyy-mm-dd 
###     See postgress documentation for how SUBSTRING works
DATE_RANGE = "SUBSTRING(fl_date,6,2) = '01'"


def get_training_flight_data(features:str=PRIMARY_FEATURES) -> pd.DataFrame:
    """ 
    Returns DataFrame of all relevant flight information
    
    Accepts an optional argument for specific features to query in string format
    
        Example: get_training_flight_data("fl_date,tail_num,distance") 
    """
    #query database
    flights = database.query(f"""SELECT {features}
                             FROM flights
                            WHERE {DATE_RANGE}
                             """)
    #get tables
    unique_carriers = pd.read_csv('../data/preprocessing/unique_carriers.csv')
    flight_numbers = pd.read_csv('../data/preprocessing/test_flight_numbers.csv')  
    #apply filters
    flights = flights[flights['op_unique_carrier'].isin(unique_carriers['op_unique_carrier'].values)]
    flights = flights[flights['op_carrier_fl_num'].isin(flight_numbers['op_carrier_fl_num'].values)]
    flights = flights[flights['arr_delay'].notnull()]
    return  flights


# def get_flights_test() -> pd.DataFrame:
#     return  database.query(FLIGHTS_TEST_QUERY)