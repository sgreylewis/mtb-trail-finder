
from flask import Flask, render_template, request, jsonify
import pickle
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from sklearn import preprocessing
from sklearn.preprocessing import StandardScaler
from geopy.geocoders import GoogleV3, Nominatim
from geopy.distance import vincenty, great_circle
import math


app = Flask(__name__)

def scale_columns(df):
    columns_to_scale = list(df.select_dtypes(exclude=['object']).columns.difference(['starVotes',
    'latitude','longitude'])) # 'stars', 'type_Featured Ride', 'type_Trail']))
    for col in columns_to_scale:
        df[col + "_scaled"] = preprocessing.scale(df[col])
    return df

def get_scaled_array(df):
    scaled_cols = [col for col in df.columns if 'scaled' in col]
    print (scaled_cols)
    array = df[scaled_cols].values
    return array

df = pd.read_csv('../data/US_trails_engineered.csv')

df = scale_columns(df)

X = get_scaled_array(df)

def euclidean_dist_recs(index, desired_state = None, desired_city_town= None):
    trail = X[index].reshape(1,-1)
    ed = euclidean_distances(trail, X)
    rec_index = np.argsort(ed)[0][1:]
    ordered_df = df.loc[rec_index]
    if desired_state is not None:
        ordered_df = ordered_df[ordered_df['state']== desired_state]
    if desired_city_town is not None:
        ordered_df = ordered_df[ordered_df['city/town']== desired_city_town]
    rec_df = ordered_df.head(20)
    rec_df = rec_df.reset_index(drop=True)
    rec_df.index = rec_df.index+1
    orig_row = df.loc[[index]].rename(lambda x: 'original')
    total = pd.concat([orig_row, rec_df])
    columns_to_output = ['location', 'difficulty', 'length', 'ascent', 'descent',
       'stars', 'category', 'summary', 'url', 'name']
    output = total[columns_to_output]
    output.columns = ['Location', 'Difficulty', 'Length', 'Ascent', 'Descent',
       'Rating', 'Category', 'Summary', 'Link', 'Name']
    return output

def cos_sim_recs(index, desired_state=None, desired_city_town=None):
    trail = X[index].reshape(1,-1)
    cs = cosine_similarity(trail, X)
    rec_index = np.argsort(cs)[0][::-1][1:]
    ordered_df = df.loc[rec_index]
    if desired_state is not None:
        ordered_df = ordered_df[ordered_df['state']== desired_state]
    if desired_city_town is not None:
        ordered_df = ordered_df[ordered_df['city/town']== desired_city_town]
    rec_df = ordered_df.head(20)
    rec_df = rec_df.reset_index(drop=True)
    rec_df.index = rec_df.index+1 #this makes it so that there's no index 0 shown
    orig_row = df.loc[[index]].rename(lambda x: 'original')
    total = pd.concat([orig_row, rec_df])
    columns_to_output = ['location', 'difficulty', 'length', 'ascent', 'descent',
       'stars', 'category', 'summary', 'url', 'name']
    output = total[columns_to_output]
    output.columns = ['Location', 'Difficulty', 'Length', 'Ascent', 'Descent',
       'Rating', 'Category', 'Summary', 'Link', 'Name']
    return output

def get_vincenty(row, *args):
    new_lat_lon = (row['latitude'], row['longitude'])
    return round(vincenty(args[0], new_lat_lon).miles,1)

def cold_start(start, miles, length_range = None, difficulty = None):
    earth_radius = 3960.0
    degrees_to_radians = math.pi/180.0
    radians_to_degrees = 180.0/math.pi

    #geolocator = GoogleV3()
    #geolocator = GoogleV3(api_key = 'XXXXX')

    loc = geolocator.geocode(start)
    loc_lat_lon = (loc.latitude, loc.longitude)
    #print (location.address)

    lat_diff = (miles/earth_radius)*radians_to_degrees
    r = earth_radius*math.cos(loc_lat_lon[0]*degrees_to_radians)
    lon_diff = (miles/r)*radians_to_degrees

    lat_range = (loc_lat_lon[0] - lat_diff, loc_lat_lon[0] + lat_diff)
    lon_range = (loc_lat_lon[1] - lon_diff, loc_lat_lon[1] + lon_diff)

    new_df = df[(df['latitude'] >= lat_range[0]) & (df['latitude'] <= lat_range[1])]
    new_df = new_df[(new_df['longitude'] >= lon_range[0]) & (new_df['longitude'] <= lon_range[1])]


    #MAKE THIS EASIER BY TAKING IN THE LENGTH_RANGE TUPLE(MIN,MAX) AND THEN FILTERING ROWS WHOSE 'LENGTH' IS IN THAT RANGE
    if length_range == '0-5':
        new_df = new_df[new_df['length_range'] == '0-5']
    if length_range == '5-10':
        new_df = new_df[new_df['length_range'] == '5-10']
    if length_range == '10-15':
        new_df = new_df[new_df['length_range'] == '10-15']
    if length_range == '15-20':
        new_df = new_df[new_df['length_range'] == '15-20']
    if length_range == '20-25':
        new_df = new_df[new_df['length_range'] == '20-25']
    if length_range == '25-30':
        new_df = new_df[new_df['length_range'] == '25-30']
    if length_range == '30+':
        new_df = new_df[new_df['length_range'] == '30+']
    '''
    if length_range == '30-50':
        new_df = new_df[new_df['length_range'] == '30-50']
    if length_range == '50-100':
        new_df = new_df[new_df['length_range'] == '50-100']
    if length_range == '100+':
        new_df = new_df[new_df['length_range'] == '100+']
    '''
    if difficulty == 'Green':
        difficulties = ['Green', 'Green/Blue']
        new_df = new_df[new_df['difficulty'].isin(difficulties)]
    if difficulty == 'Blue':
        difficulties = ['Green/Blue', 'Blue', 'Blue/Black']
        new_df = new_df[new_df['difficulty'].isin(difficulties)]
    if difficulty == 'Black':
        difficulties = ['Blue/Black', 'Black', 'Double Black']
        new_df = new_df[new_df['difficulty'].isin(difficulties)]

    if new_df.shape[0] == 0:
        return "There are no trails that meet your requirements. Try expanding your search."
    else:
        new_df['miles away'] = new_df.apply(get_vincenty, axis = 1, args = (loc_lat_lon,))
        columns_to_output = ['location', 'difficulty', 'length', 'ascent', 'descent',
           'stars', 'category', 'miles away', 'summary', 'url', 'name']
        new_df = new_df[columns_to_output]
        new_df.sort_values(by = 'miles away', inplace = True)
        new_df = new_df.reset_index(drop=True)
        new_df.index = new_df.index+1
        new_df.columns = ['Location', 'Difficulty', 'Length', 'Ascent', 'Descent',
           'Rating', 'Category', 'Miles Away', 'Summary', 'Link', 'Name']
        return new_df


@app.route('/', methods =['GET','POST'])
def index():
    return render_template('home.html')

@app.route('/trails', methods=['GET','POST'])
def trails():
    return render_template('index.html',df=df)

#CHANGE THESE TWO FOR YOUR COLD START
@app.route('/location', methods=['GET','POST'])
def get_location():
    return render_template('location_index.html',df=df)

@app.route('/location_recommendations', methods=['GET','POST'])
def location_recommendations():
    location = str(request.form.get('location'))
    radius = float(request.form.get('radius'))
    length_range = None
    #length_range = str(request.form.get('length_range'))
    difficulty = None

    if location == '' or radius == '':
        return 'You must give your current location and desired radius from your location.'

    else:
        if request.form.get('0-5'):
            length_range = '0-5'
        if request.form.get('5-10'):
            length_range = '5-10'
        if request.form.get('10-15'):
            length_range = '10-15'
        if request.form.get('15-20'):
            length_range = '15-20'
        if request.form.get('20-25'):
            length_range = '20-25'
        if request.form.get('25-30'):
            length_range = '25-30'
        if request.form.get('30+'):
            length_range = '30+'

        #if length_range == '':
        #    length_range = None

        if request.form.get('Green'):
            difficulty = 'Green'
        if request.form.get('Blue'):
            difficulty = 'Blue'
        if request.form.get('Black'):
            difficulty = 'Black'

        rec_df = cold_start(location, radius, length_range, difficulty)

        if isinstance(rec_df, str):
            return rec_df
        else:
            return render_template('location_recommendations.html',rec_df=rec_df)

@app.route('/recommendations', methods=['GET','POST'])
def recommendations():
    state = request.form.get('state')
    #name_city_town = request.form.get('name_city_town')
    name_city_town = request.form.get('name_city_town')
    dest_state = request.form.get('dest_state') #desired state, also need to do desired location in that state
    dest_city_town = request.form.get('dest_city_town')
    print (dest_state)
    print (dest_city_town)
    if state == '':
        return 'You must select a state you have ridden in.'
    #if city_town == 'Select a city or town...':
    #    return 'You must select a city or town you have ridden in from the state you chose.'
    #if name_city_town == '':
    #    return 'You must select a trail.'
    else: #if trail != '':
        index = int(name_city_town) #WHY INT OF TRAIL? trail is the index of the trail

        if dest_state == '':
            dest_state = None
            dest_city_town = None
        #elif dest_state != '' and dest_location == '':
        elif dest_state != '' and dest_city_town == 'Select a city or town...':
            dest_city_town = None

        rec_df = cos_sim_recs(index, dest_state, dest_city_town)
        #rec_df = euclidean_dist_recs(index, dest_state, dest_city_town)
        return render_template('recommendations.html',rec_df=rec_df)

@app.route('/get_city_towns')
def get_city_towns(): #this makes the dropdown for the trails
    state = request.args.get('state') #pulls in whatever state returned
    if state:
        sub_df = df[df['state'] == state]
        city_towns = list(sub_df['city/town'].unique())
        city_towns.sort()
        id_city_town = [("", "Select a city or town...")] + [(ind,val) for ind,val in enumerate(city_towns)]
        data = [{"id": str(x[0]), "city_town": x[1]} for x in id_city_town]
    return jsonify(data) #turns it into json, like a dictionary

#THIS IS THE DROPDOWN FOR THE TRAILS;
@app.route('/get_trails')
def get_trail_names(): #this makes the dropdown for the trails
    state = request.args.get('state') #pulls in whatever state returned, this will require the state and the location
    #city_town = request.args.get('city_town') #pulls in the text for location since I set the item.value as the text
    #print (type(city_town))
    if state:
        sub_df = df[df['state'] == state]
        #print(sub_df)
        #sub_df = sub_df[sub_df['city/town'] == city_town]
        sub_df.sort_values(by='name',inplace=True) #sorted alphabetically
        id_name = [("","Select a Trail...")] + list(zip(list(sub_df.index),list(sub_df['name_city/town']))) #gets the id, the trail name, and difficulty level(), get the colors so you can color it that color in the dropdown
        trail_data = [{"id": str(x[0]), "name": x[1]} for x in id_name] #id is a string so trail that it returns is a string of an id, color goes into the color class to choose a background color
        return jsonify(trail_data) #turns it into json, like a dictionary
    else:
        return "You must enter a state that you've ridden in."

if  __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True, threaded=True)
