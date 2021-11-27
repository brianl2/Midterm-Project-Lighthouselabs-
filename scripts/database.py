import psycopg2
import pandas as pd


DATABASE = {
            'host' : 'mid-term-project.ca2jkepgjpne.us-east-2.rds.amazonaws.com', 
            'port' : 5432, 
            'user' : 'lhl_student', 
            'password' : 'lhl_student', 
            'database' : 'mid_term_project'
            }


def _connect():
    """ 
    Connect to the PostgreSQL database server 
    """
    try:
        return psycopg2.connect(**DATABASE)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return None



def query(request:str) -> pd.DataFrame:
    """
    Queries the server and returns results in the form of a pandas dataframe. 
    """
    cursor = _connect().cursor()
    cursor.execute(request)
    data = cursor.fetchall()
    headers = [desc[0] for desc in cursor.description]
    results = pd.DataFrame(data, columns=headers)
    cursor.close()
    return results