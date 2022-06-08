

TODO
create a docker image that:

# part 1
use the spotipy api to automatically move all newly saved songs into the "NEW" playlist
- use the date/time added metadata to determine what the "new" saved songs are

# part 2
leverage https://github.com/SolidHal/tsar:
1) automatically download all songs from a specified playlist
  - with tags, album art, etc
2) place them in the airsonic library
3) update the monthly playlist in airsonic
