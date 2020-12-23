import sys

arg = sys.argv[1]
print(arg[::-1])

import re
import pandas as pd
from datetime import date, datetime
import pytz
from common import utils
import numpy as np

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
from common.artist_mapping import artist_dictionary
import requests

def query_artist(artist, token):
    headers = {
        "Accept": "application/json"
        , "Content-Type": "application/json"
        , "Authorization": "Bearer {0}".format(token)
    }

    params = (
        ("q", "artist:{0}".format(artist))
        , ("type", "artist")
        , ("market", "US")
        , ("limit", "15")
    )

    response = requests.get("https://api.spotify.com/v1/search", headers=headers, params=params).json()

    return(response)

def remove_special_characters(string_value):
    new_string = re.sub("[^A-Za-z0-9]+", "", string_value)

    return(new_string)

def get_genres(config_path):

    config_dict = utils.read_yaml("common/config.yaml")

    spotify_user = config_dict["spotify"]["credentials"]["spotify_user"]
    client_id = config_dict["spotify"]["credentials"]["client_id"]
    client_secret = config_dict["spotify"]["credentials"]["client_secret"]

    track_logs_file = config_dict["file_output"]["track_logs_file"]
    track_ids_file = config_dict["file_output"]["track_ids_file"]
    genre_file = config_dict["file_output"]["genre_file"]

    redirect_uri = config_dict["spotipy"]["params"]["redirect_uri"]

    track_ids_df = pd.read_csv(track_ids_file)
    track_logs_df = pd.read_csv(track_logs_file)

    joined_ids_df = pd.merge(track_logs_df, track_ids_df, on=['title','artist','album'], how='left')

    scope = "user-top-read"
    token = util.prompt_for_user_token(spotify_user, scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)

    artist_to_match_list = []
    artist_name_list = []
    track_name_list = []
    popularity_list = []
    track_id_list = []
    artist_id_list = []
    genres_list = []
    artist_original_list = []

    print("Getting genres for artists")
    artist_list = list(set(joined_ids_df["artist"]))

    for i in artist_list:
        artist_to_match_value = i
        artist_query_value = np.nan
        popularity_value = np.nan
        artist_id_value = np.nan
        genres_value = np.nan
        artist_value = i
        artist_original_value = i

        if i in artist_dictionary.keys():
            artist_value = artist_dictionary[i]

        try:
            try:
                track_results = query_artist(artist_value, token)
                artist_results = track_results["artists"]["items"][0]
            except:
                track_results = query_artist(artist_value.replace("'",""), token)
                artist_results = track_results["artists"]["items"][0]
        except:
            print(artist_value)
            artist_to_match_list.append(artist_to_match_value)
            artist_name_list.append(artist_query_value)
            popularity_list.append(popularity_value)
            artist_id_list.append(artist_id_value)
            genres_list.append(genres_value)
            artist_original_list.append(artist_original_value)

            continue

        if (artist_results["name"].lower() == artist_value.lower()) | (remove_special_characters(artist_results["name"].lower()) == remove_special_characters(artist_value.lower())):
            artist_to_match_value = artist_value
            artist_query_value = artist_results["name"]
            popularity_value = artist_results["popularity"]
            artist_id_value = artist_results["id"]
            genres_value = artist_results["genres"]
        else:
            for val in track_results["artists"]["items"]:

                if remove_special_characters(val["name"].lower()) == remove_special_characters(artist_value.lower()):
                    artist_to_match_value = artist_value
                    artist_query_value = val["name"]
                    popularity_value = val["popularity"]
                    artist_id_value = val["id"]
                    genres_value = val["genres"]

                    break

        artist_to_match_list.append(artist_to_match_value)
        artist_name_list.append(artist_query_value)
        popularity_list.append(popularity_value)
        artist_id_list.append(artist_id_value)
        genres_list.append(genres_value)
        artist_original_list.append(artist_original_value)

    artist_id_df = pd.DataFrame({
        'artist_to_match': artist_name_list
        , 'artist_query': artist_to_match_list
        , 'artist_original': artist_original_list
        , 'popularity': popularity_list
        , 'artist_id': artist_id_list
        , 'genres': genres_list
    })

    print("Getting joined table ready ")

    joined_df = pd.merge(joined_ids_df, artist_id_df, left_on=['artist'], right_on=['artist_original'], how='left')

    local_format = '%d %b %Y, %H:%M'
    gmt = pytz.timezone('GMT')
    eastern = pytz.timezone('US/Eastern')

    joined_df['playback_date_new'] = [datetime.strptime(val, local_format) for val in joined_df['playback_date']]
    joined_df['eastern_time'] = [gmt.localize(val).astimezone(eastern) for val in joined_df['playback_date_new']]
    joined_df['weekday'] = [val.weekday() for val in joined_df['eastern_time'].tolist()]

    joined_df_sorted = joined_df.sort_values('eastern_time')
    joined_df_sorted['lag_date'] = joined_df_sorted['eastern_time'].shift(1)
    joined_df_sorted['diff'] = joined_df_sorted['eastern_time'] - joined_df_sorted['lag_date']
    joined_df_sorted['diff_new'] = [(val.seconds)/60 for val in joined_df_sorted['diff']]

    joined_df_sorted_filtered = joined_df_sorted[joined_df_sorted['diff_new'] > 0]

    print("Writing to {0}".format(genre_file))
    joined_df_sorted_filtered.to_csv(genre_file, index=False)

    return(joined_df_sorted_filtered)

if __name__== "__main__":
  get_genres(arg)
