

TODO
create a docker image that:

# part 1
use the spotipy api to automatically move all newly saved songs into the "NEW" playlist
- use the date/time added metadata to determine what the "new" saved songs are

# part 2
leverage https://github.com/SolidHal/tsar:
automatically download all songs from a specified playlist
  - with tags, album art, etc
  
# part 3
- place the songs into the airsonic library
- update the monthly playlist in airsonic
  - use py-sonic
  
 
 
TODO:
airsonic server is too old, migrate to airsonic-advanced
 
## requirements
- tsar
- py-sonic : https://github.com/crustymonkey/py-sonic
