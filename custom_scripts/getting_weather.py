#Run these functions in order** Using the provided weather_all csv. 

# Run step 1, to get the dates of interest
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


#Run step 2 to merge the weather from the dates above, into the test set/train set
# Function for merging weather with other dataframes (Provided the other dataframe has "origin" and 'fl_date' features)
def merging_weather(df,df2):
    '''Merges weather dataframe of interest into features table based on dates and origin city (IATA CODE), 
    Where the first dataframe is weather, and the second is table of features.'''
    df = df.rename(columns = {'iata_code':'origin', 'StartTime(UTC)':'fl_date'})
    df = df.drop_duplicates(['origin','fl_date','Severity','Type'])
    df = pd.get_dummies(df,columns = ['Type'])
    final = df2.merge(df, how = 'left', on = ['origin', 'fl_date'])
    return final


# Run Step 3 to clean the data and make numerical values, removing NaN's. 
def cleaning_weather(df):
    ''' Cleans the weather data for the dataframe provided, replacing NaNs with Zeros for no weather, and no severity. '''
    severity_nums = {"Severity": {"Sunny": 0, "Other": 1, "Light": 2, "Moderate": 3, "Heavy": 4, "Severe": 5}} 
    df = df.replace(severity_nums)
    df['Type_Rain'] = df['Type_Rain'].fillna(0)
    df['Type_Hail'] = df['Type_Hail'].fillna(0)
    df['Type_Cold'] = df['Type_Cold'].fillna(0)
    df['Type_Fog'] = df['Type_Fog'].fillna(0)
    df['Type_Snow'] = df['Type_Snow'].fillna(0)
    df['Type_Storm'] = df['Type_Storm'].fillna(0)
    df['Type_Precipitation'] = df['Type_Precipitation'].fillna(0)
    df['Severity'] = df['Severity'].fillna(0)
    return df