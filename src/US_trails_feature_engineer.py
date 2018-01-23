'''
YOU MIGHT NEED TO KEEP THE LOCATION COLUMN AS IS AND MAKE A CITY/TOWN column
This file shows how I engineered the features of each trail to prepare them for
applying a distance metric to them.
'''

import numpy as np
import pandas as pd

def difficulty_encode(string):
    if string == 'green':
        return 1
    if string == 'greenBlue':
        return 2
    if string == 'blue':
        return 3
    if string == 'blueBlack':
        return 4
    if string == 'black':
        return 5
    if string == 'dblack':
        return 6

def get_difficulty(string):
    if string == 'greenBlue':
        return 'Green/Blue'
    if string == 'blueBlack':
        return 'Blue/Black'
    if string == 'dblack':
        return 'Double Black'
    else:
        return string.title()

def get_location(string):
    location_state = string.split(',')
    return location_state[0]

def capitalize_state(string):
    if string == 'dc':
        return string.upper()
    else:
        return string.title()

def bin_column(df, column, new_column, cut_points, label_names):
    df[new_column] = pd.cut(df[column],cut_points,labels=label_names)
    return df

if __name__ == '__main__':

    #US_trails = pd.read_csv('US_trails_1step.csv')
    US_trails = pd.read_csv('data/US_trails_half_step.csv')

    raw_columns = ['ascent', 'conditionDate', 'conditionDetails',
       'conditionStatus', 'descent', 'difficulty', 'high', 'id', 'imgMedium',
       'imgSmall', 'imgSmallMed', 'imgSqSmall', 'latitude', 'length',
       'location', 'longitude', 'low', 'name', 'starVotes', 'stars', 'summary',
       'type', 'url', 'State']

    #dropping trails that are unnecessary as they are image links and condition statuses
    #dropping low and high because I don't need the elevation points
    #dropping starVotes, summary, and url, though I'd like to include those as outputs on the website
    US_trails.drop(['conditionDate', 'conditionDetails', 'conditionStatus',
                'high', 'id', 'imgMedium', 'imgSmall', 'imgSmallMed', 'imgSqSmall', 'low',
               'starVotes'], axis = 1, inplace = True)

   #reordering the columns
    ordered_columns = ['name','location','State','type','difficulty','length','ascent',
                    'descent','stars','latitude','longitude','summary', 'url']
    US_trails = US_trails[ordered_columns]

    #this gets rid of the trails with missing difficulty ratings
    difficulty = ['dblack', 'black', 'greenBlue', 'blue', 'blueBlack', 'green']
    US_trails = US_trails[US_trails['difficulty'].isin(difficulty)].reset_index(drop=True)

    #this encodes the categorical difficulty values into integers
    US_trails['difficulty_encoded'] = US_trails['difficulty'].apply(difficulty_encode)

    #this gets rid of all Connectors(there are 6,000 of them and they aren't really trails)
    types = ['Trail', 'Featured Ride']
    US_trails = US_trails[US_trails['type'].isin(types)].reset_index(drop=True)

    #I'm creating another type column since it will get deleted when I create dummy variables
    US_trails['category'] = US_trails['type']

    #create dummy variables for type column(Connector, Trail, Featured Ride)
    US_trails = pd.get_dummies(US_trails, columns=['type'])

    #this rewrites the difficulty labels to be cleaner
    US_trails['difficulty'] = US_trails['difficulty'].apply(get_difficulty)

    #changing the location to just be the town/city with no state
    US_trails['city/town'] = US_trails['location'].apply(get_location)
    #I have to drop all trails that don't have a location since these locations won't populate on my Flask dropdown menu
    US_trails = US_trails[US_trails['city/town'] != ''].reset_index(drop=True)

    #capitalizing the first letter of each state and uppercasing DC
    US_trails['state'] = US_trails['State'].apply(capitalize_state)
    US_trails.drop(['State'], axis = 1, inplace = True)

    #creating a new column to show length ranges, generalized the function as we may need it again
    length_cuts = [-1.0,5.0,10.0,15.0,20.0,25.0,30.0,500]
    length_ranges = ['0-5','5-10','10-15','15-20','20-25','25-30','30+']
    #length_cuts = [-1.0,5.0,10.0,15.0,20.0,25.0,30.0,50.0,100,500]
    #length_ranges = ['0-5','5-10','10-15','15-20','20-25','25-30','30-50','50-100','100+']
    US_trails = bin_column(US_trails,'length','length_range',length_cuts,length_ranges)

    US_trails.to_csv('../data/US_trails_engineered.csv', index = False)

    #GOOD TO KNOW:
    raw_columns = ['ascent', 'conditionDate', 'conditionDetails',
       'conditionStatus', 'descent', 'difficulty', 'high', 'id', 'imgMedium',
       'imgSmall', 'imgSmallMed', 'imgSqSmall', 'latitude', 'length',
       'location', 'longitude', 'low', 'name', 'starVotes', 'stars', 'summary',
       'type', 'url', 'State']

    #as of right now:
    columns = ['name', 'location', 'difficulty', 'length', 'ascent', 'descent',
       'stars', 'latitude', 'longitude', 'summary', 'url',
       'difficulty_encoded', 'category', 'type_Connector',
       'type_Featured Ride', 'type_Trail', 'state', 'length_range']

    columns_to_output = ['name', 'state', 'location', 'difficulty', 'stars', 'length', 'ascent', 'descent',
       'category', 'summary', 'url']

    columns_to_measure = ['length', 'ascent', 'descent', 'stars', 'latitude', 'longitude',
       'difficulty_encoded', 'type_Connector', 'type_Featured Ride', 'type_Trail', 'length_range']
