import sys
sys.path.append("..")

from scripts import database
import pandas as pd


FLIGHTS_QUERY =  """
                SELECT * 
                    FROM flights
                    LIMIT 10;
                """
FLIGHTS_TEST_QUERY =  """
                SELECT * 
                    FROM flights
                    LIMIT 10;
                """


def get_flights() -> pd.DataFrame:
    return  database.query(FLIGHTS_QUERY)


def get_flights_test() -> pd.DataFrame:
    return  database.query(FLIGHTS_TEST_QUERY)