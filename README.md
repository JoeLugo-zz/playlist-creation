# playlist-creation

## Description
So you know that Spotify Wrapped playlist that you get every year? They mix ALL the genres and artists in one playlist of your top songs. Yeah I never listen to that because I don't want to hear a Gunna track and then Elevation Worship right after. There's a time for both and it's definitely not right after each other. So I made this to get my top tracks and split them up by genre or artist.

## Steps
1. Get the listening history
2. Get the spotify ids for the tracks
3. Get the genres for the tracks
4. Create playlist

### Get the listening history
Using lastfm I was able to track the songs that I listen to on Spotify as Spotify doesn't provide this:
```
python get_track_logs.py common/config.yaml
```

### Get the spotify ids for the tracks
Using the Spotify API I was able to search for the corresponding song ids:
```
python spotify_ids.py common/config.yaml
```

### Get the genres for the tracks
Using the Spotify API again I was able to search for the corresponding genre as well:
```
python genres.py common/config.yaml
```

### Create playlist
Connected to the Spotify API again to create the playlist:
```
python make_playlist.py common/config.yaml
```

![alt text](saved_files/top_hip_hop.png)
