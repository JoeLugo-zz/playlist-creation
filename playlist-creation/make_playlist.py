import sys
import pandas as pd
import spotipy.util as util
import requests
import json
from common import utils
from common.api_calls import create_playlist, add_tracks

arg = sys.argv[1]
print(arg[::-1])

def get_tracks(df,n,filter_object,contains,excludes=None):
    filtered_df = df.dropna()
    filtered_df["{0}_lower".format(filter_object)] = filtered_df[filter_object].str.lower()
    contains = [val.lower() for val in contains]

    if excludes:
        excludes = [val.lower() for val in excludes]
        filtered_df = filtered_df[(filtered_df["{0}_lower".format(filter_object)].str.contains("|".join(contains))) & ~(filtered_df["{0}_lower".format(filter_object)].str.contains("|".join(excludes)))]
    else:
        filtered_df = filtered_df[(filtered_df["{0}_lower".format(filter_object)].str.contains("|".join(contains)))]

    grouped_df = filtered_df.groupby(["spotify_name","spotify_id"]).count().sort_values("eastern_time", ascending=0).head(n=n).reset_index()

    return(grouped_df)

def main(config_path):

    config_dict = utils.read_yaml(config_path)
    num_of_tracks = config_dict["playlist_creation"]["params"]["num_of_tracks"]
    include = config_dict["playlist_creation"]["params"]["include"]
    include_list = include.replace(" ","").split(",")
    exclude = config_dict["playlist_creation"]["params"]["exclude"]

    if exclude:
        if ((len(exclude) == 1) & (exclude[0] == "")):
            exclude_list = None
        else:
            exclude_list = exclude.replace(" ","").split(",")
    else:
        exclude_list = None

    playlist_name = config_dict["playlist_creation"]["params"]["playlist_name"]
    filter_type = config_dict["playlist_creation"]["params"]["filter_type"]

    spotify_user = config_dict["spotify"]["credentials"]["spotify_user"]
    client_id = config_dict["spotify"]["credentials"]["client_id"]
    client_secret = config_dict["spotify"]["credentials"]["client_secret"]

    input_file = config_dict["playlist_creation"]["params"]["input_file"]

    redirect_uri = config_dict["spotipy"]["params"]["redirect_uri"]

    scope = "playlist-modify-public"
    token = util.prompt_for_user_token(spotify_user, scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)

    print("Reading in {0}".format(input_file))
    listening_history_df = pd.read_csv(input_file)

    track_df = get_tracks(listening_history_df, num_of_tracks, filter_type, include_list, exclude_list)

    print("Creating playlist {0}".format(playlist_name))
    new_playlist = create_playlist(spotify_user, token, playlist_name)

    playlist_id = json.loads(new_playlist.text)["id"]

    print("Adding tracks to playlist")
    add_tracks(playlist_id, track_df["spotify_id"].tolist(), token)

if __name__== "__main__":
  main(arg)
