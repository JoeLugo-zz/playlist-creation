import requests
import json

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

    response = requests.get("https://api.spotify.com/v1/search", headers=headers, params=params)

    response_output = response.json()

    return(response_output)

def query_track(artist, album, track, token):
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer {0}".format(token),
    }

    params = (
        ("q", "artist:{0} album:{1} track:{2}".format(artist, album, track)),
        ("type", "track"),
        ("market", "US"),
        ("limit", "1")
    )

    response = requests.get("https://api.spotify.com/v1/search", headers=headers, params=params)

    response_output = response.json()

    return(response_output)

def query_track_2(artist, track, token):
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer {0}".format(token),
    }

    params = (
        ("q", "artist:{0} track:{1}".format(artist, track)),
        ("type", "track"),
        ("market", "US"),
        ("limit", "1")
    )

    response = requests.get("https://api.spotify.com/v1/search", headers=headers, params=params)

    response_output = response.json()

    return(response_output)

def query_track_3(track, token):
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer {0}".format(token),
    }

    params = (
        ("q", "track:{0}".format(track)),
        ("type", "track"),
        ("market", "US"),
        ("limit", "1")
    )

    response = requests.get("https://api.spotify.com/v1/search", headers=headers, params=params)

    response_output = response.json()

    return(response_output)

def create_playlist(user_id, token, name="New Playlist"):

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer {0}".format(token),
    }

    data = '{"name":"%s","description":"New playlist description","public":true}'%name

    response = requests.post("https://api.spotify.com/v1/users/{0}/playlists".format(user_id), headers=headers, data=data)

    if response.status_code != 201:
        print(response.text)

    return(response)

def add_tracks(playlist_id, track_list, token):
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer {0}".format(token),
    }

    params = (
        ("uris", ",".join(["spotify:track:{0}".format(val) for val in track_list])),
    )

    response = requests.post("https://api.spotify.com/v1/playlists/{0}/tracks".format(playlist_id), headers=headers, params=params)

    if response.status_code != 201:
        print(track_list)
        print(response.text)

    return(response)
