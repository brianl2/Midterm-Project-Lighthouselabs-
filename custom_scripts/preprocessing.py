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




def get_test_flights():
    """ Returns dataframe of flights from the first week of january 2020"""
    return database.query(  """ 
                            SELECT * 
                                FROM flights_test
                                WHERE fl_date = ANY('{{2020-01-01, 2020-01-02, 2020-01-03, 2020-01-04, 2020-01-05, 2020-01-06, 2020-01-07}}')
                                ;
                            """)

def get_all_january_data(features:str=PRIMARY_FEATURES) -> pd.DataFrame:
    """ 
    Returns DataFrame of all flights across all years from the month of january
    
    Accepts an optional argument for specific features to query in string format
    
        Example: get_all_january_data("fl_date,tail_num,distance") 
    """
    return database.query(f"""SELECT {features}
                             FROM flights
                            WHERE SUBSTRING(fl_date,6,2) = '01'
                             """)
    ### Uncertain if data should be filtered at this point ###
    # #get tables
    # unique_carriers = pd.read_csv('../data/preprocessing/unique_carriers.csv')
    # flight_numbers = pd.read_csv('../data/preprocessing/test_flight_numbers.csv')  
    # #apply filters
    # flights = flights[flights['op_unique_carrier'].isin(unique_carriers['op_unique_carrier'].values)]
    # flights = flights[flights['op_carrier_fl_num'].isin(flight_numbers['op_carrier_fl_num'].values)]
    # flights = flights[flights['arr_delay'].notnull()]
    # return  flights


def get_2018_january_data(features:str=PRIMARY_FEATURES) -> pd.DataFrame:
    """ 
    Returns DataFrame of all flights from January 2018
    
    Accepts an optional argument for specific features to query in string format
    
        Example: get_2018_january_data("fl_date,tail_num,distance") 
    """
    return database.query(f"""SELECT {features}
                             FROM flights
                            WHERE SUBSTRING(fl_date,1,7) = '2018-01'
                             """)
    
def get_2019_january_data(features:str=PRIMARY_FEATURES) -> pd.DataFrame:
    """ 
    Returns DataFrame of all flights from January 2019
    
    Accepts an optional argument for specific features to query in string format
    
        Example: get_2019_january_data("fl_date,tail_num,distance") 
    """
    return database.query(f"""SELECT {features}
                             FROM flights
                            WHERE SUBSTRING(fl_date,1,7) = '2019-01'
                             """)
    
def get_1st_last_week(features:str=PRIMARY_FEATURES) -> pd.DataFrame:
    """ Returns DataFrame from the last week of the dataset
        Accepts an optional argument for specific features to query in string format
            Example: get_all_january_data("fl_date,tail_num,distance") """
    return database.query(f"""SELECT {features}
                             FROM flights
                            WHERE fl_date = ANY('{{2019-12-31, 2019-12-30, 2019-12-29, 2019-12-28, 2019-12-27, 2019-12-26, 2019-12-25}}')
                             """)  
def get_2nd_last_week(features:str=PRIMARY_FEATURES) -> pd.DataFrame:
    """ Returns DataFrame from the second last week of the dataset
        Accepts an optional argument for specific features to query in string format
            Example: get_all_january_data("fl_date,tail_num,distance") """
    return database.query(f"""SELECT {features}
                             FROM flights
                            WHERE fl_date = ANY('{{2019-12-24, 2019-12-23, 2019-12-22, 2019-12-21, 2019-12-20, 2019-12-19, 2019-12-18}}')
                             """)
def get_3rd_last_week(features:str=PRIMARY_FEATURES) -> pd.DataFrame:
    """ Returns DataFrame from the third last week of the dataset
        Accepts an optional argument for specific features to query in string format
            Example: get_all_january_data("fl_date,tail_num,distance") """
    return database.query(f"""SELECT {features}
                             FROM flights
                            WHERE fl_date = ANY('{{2019-12-17, 2019-12-16, 2019-12-15, 2019-12-14, 2019-12-13, 2019-12-12, 2019-12-11}}')
                             """)
def get_4th_last_week(features:str=PRIMARY_FEATURES) -> pd.DataFrame:
    """ Returns DataFrame from the fourth last week of the dataset
        Accepts an optional argument for specific features to query in string format
            Example: get_all_january_data("fl_date,tail_num,distance") """
    return database.query(f"""SELECT {features}
                             FROM flights
                            WHERE fl_date = ANY('{{2019-12-10, 2019-12-09, 2019-12-08, 2019-12-07, 2019-12-06, 2019-12-05, 2019-12-04}}')
                             """)
def get_5th_last_week(features:str=PRIMARY_FEATURES) -> pd.DataFrame:
    """ Returns DataFrame from the fifth last week of the dataset
        Accepts an optional argument for specific features to query in string format
            Example: get_all_january_data("fl_date,tail_num,distance") """
    return database.query(f"""SELECT {features}
                             FROM flights
                            WHERE fl_date = ANY('{{2019-12-03, 2019-12-02, 2019-12-01, 2019-11-30, 2019-11-29, 2019-11-28, 2019-11-27}}')
                             """)