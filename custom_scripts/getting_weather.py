# import Modules
import pandas as pd
#Function for getting weather. 
def getting_weather(df,start_date,end_date):
    '''Given the weather dataframe and string of dates of interest (YYYY-MM-DD), provides weather data for dates provided and airport code.  '''
    filter1 = (df['StartTime(UTC)'] > start_date) & (df['StartTime(UTC)'] <= end_date)
    df = df.loc[filter1]
    df2 = df[['Type','Severity','StartTime(UTC)','iata_code']]
    return df2
# Read the relevant weather_all.csv into a dataframe
weather = pd.read_csv('../data/Weather_data/weather_all.csv')
#Plug and play example, changing dates
getting_weather(weather,'2016-01-06','2019-01-31')