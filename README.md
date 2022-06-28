

TODO
create a docker image that:

# part 1
use the spotipy api to automatically move all newly saved songs into the "NEW" playlist
- use the date/time added metadata to determine what the "new" saved songs are

- spotify-playlist-update.py

# part 2
leverage https://github.com/SolidHal/tsar:
automatically download all songs from a specified playlist
  - with tags, album art, etc
  
# part 3
- place the songs into the airsonic library
- update the monthly playlist in airsonic

- airsonic-import.py
  
 
 
TODO:
-  wrap it all into a single docker image which takes
  - spotipy env vars
  - spotify username/pass
  - airsonic username/pass
  - airsonic server/port
  - airsonic library directory
  - import directory
  - spotify playlist_id

and runs the 3 parts intermittently, nightly

## requirements
- tsar
- py-sonic : https://github.com/crustymonkey/py-sonic
- eyed3
- click
- spotify premium
- an airsonic(advanced) server or similar


## build the docker image

```
docker build -t solidhal/airsonic-spotify .
```
