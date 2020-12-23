import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
import requests
import json
from common import utils

def create_playlist(user_id, token, name='New Playlist'):

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {0}'.format(token),
    }

    data = '{"name":"%s","description":"New playlist description","public":true}'%name

    response = requests.post('https://api.spotify.com/v1/users/{0}/playlists'.format(user_id), headers=headers, data=data)

    if response.status_code != 201:
        print(response.text)

    return(response)

def add_tracks(playlist_id, track_list, token):
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {0}'.format(token),
    }

    params = (
        ('uris', ','.join(['spotify:track:{0}'.format(val) for val in track_list])),
    )

    response = requests.post('https://api.spotify.com/v1/playlists/{0}/tracks'.format(playlist_id), headers=headers, params=params)

    if response.status_code != 201:
        print(track_list)
        print(response.text)

    return(response)

def get_tracks(df,n,filter_object,contains,excludes=None):
    filtered_df = df.dropna()
    filtered_df['{0}_lower'.format(filter_object)] = filtered_df[filter_object].str.lower()
    contains = [val.lower() for val in contains]

    if excludes:
        excludes = [val.lower() for val in excludes]
        filtered_df = filtered_df[(filtered_df['{0}_lower'.format(filter_object)].str.contains('|'.join(contains))) & ~(filtered_df['{0}_lower'.format(filter_object)].str.contains('|'.join(excludes)))]
    else:
        filtered_df = filtered_df[(filtered_df['{0}_lower'.format(filter_object)].str.contains('|'.join(contains)))]

    grouped_df = filtered_df.groupby(['spotify_name','spotify_id']).count().sort_values('eastern_time', ascending=0).head(n=n).reset_index()

    return(grouped_df)

def main(config_path):

    config_dict = utils.read_yaml(config_path)
    num_of_tracks = config_dict["playlist_creation"]["params"]["num_of_tracks"]
    genres_to_include = config_dict["playlist_creation"]["params"]["genres_to_include"]
    genres_to_include_list = genres_to_include.replace(' ','').split(',')
    genres_to_exclude = config_dict["playlist_creation"]["params"]["genres_to_exclide"]
    genres_to_exclude_list = genres_to_exclude.replace(' ','').split(',')
    playlist_name = config_dict["playlist_creation"]["params"]["playlist_name"]
    filter_type = config_dict["playlist_creation"]["params"]["filter_type"]

    spotify_user = config_dict["spotify"]["credentials"]["spotify_user"]
    client_id = config_dict["spotify"]["credentials"]["client_id"]
    client_secret = config_dict["spotify"]["credentials"]["client_secret"]

    input_file = config_dict["file_output"]["input_file"]

    redirect_uri = config_dict["spotipy"]["params"]["redirect_uri"]

    client_credentials_manager = SpotifyClientCredentials(client_id=client_id,client_secret=client_secret)

    scope = 'playlist-modify-public'
    token = util.prompt_for_user_token(spotify_user, scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)

    # comes from spotify_ids.py
    listening_history_df = pd.read_csv(input_file)

    track_df = get_tracks(listening_history_df, num_of_tracks, filter_type, genres_to_include_list, genres_to_exclude_list)

    new_playlist = create_playlist(spotify_user, token, playlist_name)

    playlist_id = json.loads(new_playlist.text)['id']

    add_tracks(playlist_id, track_df['spotify_id'].tolist(), token)

if __name__== "__main__":
  main("/Users/josephlugo/Code/Joe/top-tracks/top_tracks/common/common.yaml")
