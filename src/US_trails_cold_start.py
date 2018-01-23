import pandas as pd
import numpy as np
from geopy.geocoders import GoogleV3, Nominatim
from geopy.distance import vincenty, great_circle
import math

def get_vincenty(row, *args):
    new_lat_lon = (row['latitude'], row['longitude'])
    return round(vincenty(args[0], new_lat_lon).miles,1)

def cold_start(start, miles, length_range = None, difficulty = None):

    earth_radius = 3960.0
    degrees_to_radians = math.pi/180.0
    radians_to_degrees = 180.0/math.pi

    geolocator = GoogleV3()
    location = geolocator.geocode(start)
    location_lat_lon = (location.latitude, location.longitude)
    #print (location.address)

    lat_diff = (miles/earth_radius)*radians_to_degrees
    r = earth_radius*math.cos(location_lat_lon[0]*degrees_to_radians)
    lon_diff = (miles/r)*radians_to_degrees

    lat_range = (location_lat_lon[0] - lat_diff, location_lat_lon[0] + lat_diff)
    lon_range = (location_lat_lon[1] - lon_diff, location_lat_lon[1] + lon_diff)

    df = US_trails[(US_trails['latitude'] >= lat_range[0]) & (US_trails['latitude'] <= lat_range[1])]
    df = df[(df['longitude'] >= lon_range[0]) & (df['longitude'] <= lon_range[1])]

    if length_range == '0-5':
        df = df[df['length_range'] == '0-5']
    if length_range == '5-10':
        df = df[df['length_range'] == '5-10']
    if length_range == '10-15':
        df = df[df['length_range'] == '10-15']
    if length_range == '15-20':
        df = df[df['length_range'] == '15-20']
    if length_range == '20-25':
        df = df[df['length_range'] == '20-25']
    if length_range == '25-30':
        df = df[df['length_range'] == '25-30']
    if length_range == '30-50':
        df = df[df['length_range'] == '30-50']
    if length_range == '50-100':
        df = df[df['length_range'] == '50-100']
    if length_range == '100+':
        df = df[df['length_range'] == '100+']

    if difficulty == 'Green':
        difficulties = ['Green', 'Green/Blue']
        df = df[df['difficulty'].isin(difficulties)]
    if difficulty == 'Blue':
        difficulties = ['Green/Blue', 'Blue', 'Blue/Black']
        df = df[df['difficulty'].isin(difficulties)]
    if difficulty == 'Black':
        difficulties = ['Blue/Black', 'Black', 'Double Black']
        df = df[df['difficulty'].isin(difficulties)]

    if df.shape[0] == 0:
        return "There are no trails that meet your requirements. Try expanding your search."
    else:
        #df['miles_away'] = df.index.map(get_vincenty)
        df['miles_away'] = df.apply(get_vincenty, axis = 1, args = (location_lat_lon,))
        columns_to_output = ['name', 'location', 'stars', 'difficulty', 'length', 'ascent', 'descent',
            'category', 'miles_away', 'summary', 'url']
        return df[columns_to_output].sort_values('miles_away')

if __name__ == '__main__':

    US_trails = pd.read_csv('../data/US_trails_engineered.csv')

    a = cold_start('2044 South Huron Street Denver', 15, length_range = '0-5', difficulty = 'Black')
    b = cold_start('1182 Shepherds Lane Atlanta', 10)
