import pandas as pd
import pylast
import re
from datetime import datetime, date
import pytz
import numpy as np
import time
import math
from common import utils

def parse_track_json(track_dict, a_track):

    try:
        track_dict["playback_date"].append(a_track.playback_date)
    except:
        track_dict["playback_date"].append(np.nan)
    try:
        track_dict["unix_timestamp"].append(a_track.timestamp)
    except:
        track_dict["unix_timestamp"].append(np.nan)
    try:
        track_dict["title"].append(a_track.track.title)
    except:
        track_dict["title"].append(np.nan)
    try:
        track_dict["artist"].append(str(a_track.track.artist)) # make str to get the right output
    except:
        track_dict["artist"].append(np.nan)
    try:
        track_dict["album"].append(a_track.album)
    except:
        track_dict["album"].append(np.nan)
    try:
        track_dict["duration"].append(a_track.track.get_duration())
    except:
        track_dict["duration"].append(np.nan)

    return(track_dict)

def query_track_data(config_path):

    config_dict = utils.read_yaml("common/config.yaml")

    username = config_dict["pylast"]["credentials"]["username"]
    password = config_dict["pylast"]["credentials"]["password"]
    api_key = config_dict["pylast"]["credentials"]["api_key"]
    api_secret = config_dict["pylast"]["credentials"]["api_secret"]

    start_date = config_dict["pylast"]["params"]["start_date"]
    end_date = config_dict["pylast"]["params"]["end_date"]
    print(start_date)
    print(end_date)

    track_logs_file = config_dict["file_output"]["track_logs_file"]

    password_hash = pylast.md5(password)

    network = pylast.LastFMNetwork(api_key=api_key, api_secret=api_secret, username=username, password_hash=password_hash)
    user = network.get_authenticated_user()

    start_date = utils.str_to_date(start_date)
    end_date = utils.str_to_date(end_date)

    unixtime_start = time.mktime(start_date.timetuple())
    unixtime_end = time.mktime(end_date.timetuple())

    print("Getting recent tracks")
    tracks = user.get_recent_tracks(time_from=unixtime_start, time_to=unixtime_end, limit=200, cacheable=True)
    print("Done getting recent tracks")

    # How can we speed this up ? Taking forever

    track_dict = {}
    track_dict["playback_date"] = []
    track_dict["unix_timestamp"] = []
    track_dict["title"] = []
    track_dict["artist"] = []
    track_dict["album"] = []
    track_dict["duration"] = []

    amount_of_tracks = len(tracks)
    print("Getting {0} tracks".format(amount_of_tracks))
    for index, a_track in enumerate(tracks):
        track_dict = parse_track_json(track_dict, a_track)

    df = pd.DataFrame.from_dict(track_dict)

    print("Writing to {0}".format(track_logs_file))
    df.to_csv(track_logs_file, index=False)

    return(df)
