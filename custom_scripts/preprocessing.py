#Script for assembling features prior to engineering and preparation
import sys
sys.path.append("..")

from custom_scripts import database
import pandas as pd


# Default features to select for when pulling samples from database
PRIMARY_TEST_FEATURES = """ fl_date, 
                        op_unique_carrier, 
                        op_carrier_fl_num, 
                        origin, 
                        dest, 
                        crs_dep_time,
                        crs_arr_time, 
                        crs_elapsed_time, 
                        distance
                    """
PRIMARY_FEATURES =  PRIMARY_TEST_FEATURES+',arr_delay'

def create_average_table(feature:str,prefix:str, min_arr_delay:float, max_arr_delay:float) -> pd.DataFrame:
    """Create a table of average features from database"""
    table = database.query(f"""
                            SELECT  {feature},
                                    AVG(dep_delay) AS "{prefix}_avg_dep_delay", 
                                    AVG(taxi_out) AS "{prefix}_avg_taxi_out",
                                    AVG(wheels_off) AS "{prefix}_avg_wheels_off", 
                                    AVG(wheels_on) AS "{prefix}_avg_wheels_on", 
                                    AVG(taxi_in) AS "{prefix}_avg_taxi_in", 
                                    AVG(arr_delay) AS "{prefix}_avg_arr_delay",
                                    AVG(crs_elapsed_time) AS "{prefix}_avg_crs_elapsed_time",
                                    AVG(actual_elapsed_time) AS "{prefix}_avg_actual_elapsed_time",
                                    AVG(air_time) AS "{prefix}_avg_air_time",
                                    AVG(carrier_delay) AS "{prefix}_avg_carrier_delay",
                                    AVG(weather_delay) AS "{prefix}_avg_weather_delay",
                                    AVG(nas_delay) AS "{prefix}_avg_nas_delay", 
                                    AVG(security_delay) AS "{prefix}_avg_security_delay",
                                    AVG(late_aircraft_delay) AS "{prefix}_avg_late_aircraft_delay",
                                    AVG(total_add_gtime) AS "{prefix}_avg_total_add_gtime",
                                    AVG(longest_add_gtime) AS "{prefix}_avg_longest_add_gtime"                                      
                                FROM flights
                                WHERE arr_delay <= {max_arr_delay}
                                AND arr_delay >= {min_arr_delay}
                                GROUP BY {feature};
                            """)
    return table

def get_test_flights(features:str=PRIMARY_TEST_FEATURES) -> pd.DataFrame:
    """ Returns dataframe of flights from the first week of january 2020"""
    return database.query(f""" 
                            SELECT {features}
                                FROM flights_test
                                WHERE fl_date = ANY('{{2020-01-01, 2020-01-02, 2020-01-03, 2020-01-04, 2020-01-05, 2020-01-06, 2020-01-07}}')
                                ;
                            """)
def get_train_flights(features:str=PRIMARY_FEATURES) -> pd.DataFrame:
    """ 
    Returns DataFrame of all flights from first week of January 2019
    
    Accepts an optional argument for specific features to query in string format
    
        Example: get_train_flights("fl_date,tail_num,distance") 
    """
    flights = database.query(f"""SELECT {features}
                             FROM flights
                                WHERE fl_date = ANY('{{2019-01-01, 2019-01-02, 2019-01-03, 2019-01-04, 2019-01-05, 2019-01-06, 2019-01-07}}')
                             """)
    flight_numbers = pd.read_csv('../data/preprocessing/test_flight_numbers.csv')  
    #apply filters
    flights = flights[flights['op_carrier_fl_num'].isin(flight_numbers['op_carrier_fl_num'].values)]
    flights = flights[flights['arr_delay'].notnull()]
    return  flights