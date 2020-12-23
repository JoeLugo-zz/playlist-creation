import sys

arg = sys.argv[1]
print(arg[::-1])

import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
from common import utils
import pandas as pd

def query_track(artist, album, track, token):
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {0}'.format(token),
    }

    params = (
        ('q', 'artist:{0} album:{1} track:{2}'.format(artist, album, track)),
        ('type', 'track'),
        ('market', 'US'),
        ('limit', '1')
    )

    response = requests.get('https://api.spotify.com/v1/search', headers=headers, params=params).json()

    return(response)

def query_track_2(artist, track, token):
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {0}'.format(token),
    }

    params = (
        ("q", "artist:{0} track:{1}".format(artist, track)),
        ('type', 'track'),
        ('market', 'US'),
        ('limit', '1')
    )

    response = requests.get("https://api.spotify.com/v1/search", headers=headers, params=params).json()

    return(response)

def query_track_3(track, token):
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {0}'.format(token),
    }

    params = (
        ("q", "track:{0}".format(track)),
        ('type', 'track'),
        ('market', 'US'),
        ('limit', '1')
    )

    response = requests.get("https://api.spotify.com/v1/search", headers=headers, params=params).json()

    return(response)

def get_spotify_ids(config_path):

    config_dict = utils.read_yaml("common/config.yaml")

    spotify_user = config_dict["spotify"]["credentials"]["spotify_user"]
    client_id = config_dict["spotify"]["credentials"]["client_id"]
    client_secret = config_dict["spotify"]["credentials"]["client_secret"]

    redirect_uri = config_dict["spotipy"]["params"]["redirect_uri"]

    track_logs_file = config_dict["file_output"]["track_logs_file"]
    track_ids_file = config_dict["file_output"]["track_ids_file"]

    scope = "user-top-read"
    token = util.prompt_for_user_token(spotify_user, scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)

    print("Reading in {0}".format(track_logs_file))

    df = pd.read_csv(track_logs_file)

    filtered_df = df[['artist','album','title']].drop_duplicates()

    # Getting the spotify ids
    ids = []
    names = []
    artists = []
    albums = []
    wrong_names = []
    wrong_artists = []

    print("Getting spotify ids")

    for i, row in filtered_df.iterrows():
        try:
            try:
                track_object = query_track(row['artist'], row['album'], row['title'], token)['tracks']['items'][0]
            except:
                try:
                    track_object = query_track(row['artist'], row['album'], row['title'].replace("'",""), token)['tracks']['items'][0]
                except:
                    try:
                        track_object = query_track(row['artist'], row['album'].replace("'",""), row['title'].replace("'",""), token)['tracks']['items'][0]
                    except:
                        try:
                            track_object = query_track_2(row['artist'], row['title'], token)['tracks']['items'][0]
                        except:
                            try:
                                track_object = query_track(row['artist'], row['album'], row['title'].split('[')[0], token)['tracks']['items'][0]
                            except:
                                try:
                                    track_object = query_track(row['artist'], row['album'], row['title'].split('(')[0], token)['tracks']['items'][0]
                                except:
                                    try:
                                        track_object = query_track(row['artist'], row['album'], row['title'].split(' - ')[0], token)['tracks']['items'][0]
                                    except:
                                        track_object = query_track_3(row['title'], token)['tracks']['items'][0]

        except:
            print(row)
            wrong_names.append(row['title'])
            wrong_artists.append(row['artist'])
            wrong_artists.append(row['album'])

        id = track_object['id']
        name = track_object['name']
        artist = track_object['artists'][0]['name']
        album = track_object['album']['name']

        ids.append(id)
        names.append(name)
        artists.append(artist)
        albums.append(album)

    filtered_df['spotify_id'] = ids
    filtered_df['spotify_name'] = names
    filtered_df['spotify_artist'] = artists
    filtered_df['spotify_album'] = albums

    print("Writing to {0}".format(track_ids_file))

    filtered_df.to_csv(track_ids_file, index=False)

    return(filtered_df)

if __name__== "__main__":
  get_spotify_ids(arg)
