import pandas as pd
import numpy as np
from sklearn import preprocessing
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
import warnings
warnings.filterwarnings('ignore')
#MIGHT HAVE TO ENCODE THE BINNING OF THE LENGTHS SO THIS CAN BE A
#PARAMETER FOR A COLD START

def scale_columns(df):
    columns_to_scale = list(df.select_dtypes(exclude=['object']).columns.difference(['latitude', 'longitude']))
    for col in columns_to_scale:
        df[col + "_scaled"] = preprocessing.scale(df[col])
    return df

def get_scaled_array(df):
    scaled_cols = [col for col in df.columns if 'scaled' in col]
    array = df[scaled_cols].values
    return array

#used in app.py
def cos_sim_recs(index, desired_state=None, desired_city_town=None):
    trail = X[index].reshape(1,-1)
    cs = cosine_similarity(trail, X)
    rec_index = np.argsort(cs)[0][::-1][1:]
    ordered_df = df.loc[rec_index]
    if desired_state is not None:
        ordered_df = ordered_df[ordered_df['state']== desired_state]
    if desired_city_town is not None:
        ordered_df = ordered_df[ordered_df['city/town']== desired_city_town]
    #rec_df = ordered_df.head(n)
    rec_df = ordered_df.head(20)
    rec_df = rec_df.reset_index(drop=True)
    rec_df.index = rec_df.index+1 #this makes it so that there's no index 0 shown
    orig_row = df.loc[[index]].rename(lambda x: 'original')
    total = pd.concat([orig_row, rec_df])
    columns_to_output = ['name', 'location', 'difficulty', 'stars', 'length', 'ascent', 'descent',
       'category', 'summary', 'url']
    output = total[columns_to_output]
    return output

def cos_sim_recommendations(trail_name, state_name, scaled_features, n=5, desired_state=None, desired_location=None):
    index = US_trails.index[(US_trails['name'] == trail_name) & (US_trails['state']==state_name)][0]
    trail = scaled_features[index].reshape(1,-1)
    cs = cosine_similarity(trail, scaled_features)
    rec_index = np.argsort(cs)[0][::-1][1:]
    ordered_df = US_trails.loc[rec_index]
    if desired_state:
        ordered_df = ordered_df[ordered_df['state']== desired_state]
    if desired_location:
        ordered_df = ordered_df[ordered_df['location']== desired_location]
    rec_df = ordered_df.head(n)
    orig_row = US_trails.loc[[index]].rename(lambda x: 'original')
    total = pd.concat([orig_row, rec_df])
    columns_to_output = ['name', 'state', 'location', 'difficulty', 'stars', 'length', 'ascent', 'descent',
       'category', 'summary', 'url']
    output = total[columns_to_output]
    return output

def euclidean_dist_recommendations(trail_name, state_name, scaled_features, n = 5, desired_state = None, desired_location= None):
    index = US_trails.index[(US_trails['name'] == trail_name) & (US_trails['state']==state_name)][0]
    trail = scaled_features[index].reshape(1,-1)
    cs = euclidean_distances(trail, scaled_features)
    rec_index = np.argsort(cs)[0][::-1][1:]
    ordered_df = US_trails.loc[rec_index]
    if desired_state:
        ordered_df = ordered_df[ordered_df['state']== desired_state]
    if desired_location:
        ordered_df = ordered_df[ordered_df['location']== desired_location]
    rec_df = ordered_df.head(n)
    orig_row = US_trails.loc[[index]].rename(lambda x: 'original')
    total = pd.concat([orig_row, rec_df])
    return total

if __name__ == '__main__':
    US_trails = pd.read_csv('../data/US_trails_engineered.csv')

    US_trails = scale_columns(US_trails)

    Big_X = get_scaled_array(US_trails)

    columns_to_output = ['name', 'state', 'location', 'difficulty', 'stars', 'length', 'ascent', 'descent',
       'category', 'summary', 'url']

    columns_to_measure = ['length', 'ascent', 'descent', 'stars', 'latitude', 'longitude',
       'difficulty_encoded', 'type_Connector', 'type_Featured Ride', 'type_Trail']


    a = cos_sim_recommendations("Mount Falcon and Lair O' the Bear Loop", 'Colorado', Big_X, n = 5, desired_state = 'Colorado', desired_location = 'Durango')
    b = cos_sim_recommendations("Mount Falcon and Lair O' the Bear Loop", 'Colorado', Big_X, n = 5, desired_state = 'Colorado', desired_location = 'Salida')
    #EUCLIDEAN DISTANCE IS SOOOO MUCH WORSE!!!!! WHY????
    c = euclidean_dist_recommendations("Mount Falcon and Lair O' the Bear Loop", 'Colorado', Big_X, n = 5, desired_state = 'Colorado', desired_location = 'Salida')
    d = cos_sim_recommendations("Mount Falcon and Lair O' the Bear Loop", 'Colorado', Big_X, n = 5, desired_state = 'Utah', desired_location = 'Moab')
    e = cos_sim_recommendations("Mount Falcon and Lair O' the Bear Loop", 'Colorado', Big_X, n = 5, desired_state = 'Virginia')
    f = cos_sim_recommendations("The Whole Enchilada", 'Utah', Big_X, n = 15)
