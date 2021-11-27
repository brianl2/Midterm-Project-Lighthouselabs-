import sys
sys.path.append("..")

from scripts import database
import pandas as pd
import csv


### This is a placeholder untill we begin building a preprocessing pipeline


UNIQUE_CARRIERS = """ 
                    SELECT mkt_unique_carrier FROM flights_test
                        GROUP BY mkt_unique_carrier;
                  """
FLIGHT_NUMBERS = """
                SELECT op_carrier_fl_num FROM flights_test
                GROUP BY op_carrier_fl_num;
                """

FLIGHTS_QUERY =  """
                SELECT * FROM flights
                    WHERE SUBSTRING(fl_date,6,2) = '01'
                    ;
                """
FLIGHTS_TEST_QUERY =  """
                SELECT * 
                    FROM flights
                    LIMIT 10;
                """



# def get_raw_flight_data() -> pd.DataFrame:
#     flights = database.query(FLIGHTS_QUERY)
#     flight_numbers = pd.read_csv('../data/preprocessing/flight_numbers.csv')
#     unique_carriers = pd.read_csv('../data/preprocessing/unique_carriers.csv')
    
#     flights - flights[flights['']]
#     return  database.query(FLIGHTS_QUERY)


# def get_flights_test() -> pd.DataFrame:
#     return  database.query(FLIGHTS_TEST_QUERY)