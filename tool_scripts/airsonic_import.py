#!/usr/bin/env python3
import libsonic
import datetime
import time
import click
import eyed3
import os
import re
import shutil

def remove_file(filename):
    try:
        os.remove(filename)
    except FileNotFoundError:
        pass

def sanitize_filename(filename):
    """Takes only a filename, not a full path"""
    return re.sub('/', ' ', filename).strip()


class Song:
    def __init__(self, name, artist, album, original_file, airsonic_library_file):
        self._name = name
        self._artist  = artist
        self._album = album
        self._original_file = original_file
        self._airsonic_library_file = airsonic_library_file
        self._airsonic_song_id = None

    @property
    def name(self):
        return self._name
    @property
    def artist(self):
        return self._artist

    @property
    def album(self):
        return self._album

    @property
    def original_file(self):
        return self._original_file

    @property
    def airsonic_library_file(self):
        return self._airsonic_library_file

    @property
    def airsonic_song_id(self):
        return self._airsonic_song_id

    @airsonic_song_id.setter
    def airsonic_song_id(self, value):
        self._airsonic_song_id = value

    def __str__(self):
        return f"name: {self._name}, artist: {self._artist}, album: {self._album}, library_file: {self._airsonic_library_file}, original_file: {self._original_file}, airsonic_song_id: {self._airsonic_song_id}"


def canonical_artist(audiofile):
    track_artist = sanitize_filename(audiofile.tag.artist.split(";")[0])
    album_artist = sanitize_filename(audiofile.tag.album_artist.split(";")[0])

    # track_artist may be malformed and not split correctly. album_artist is more reliable
    if album_artist not in track_artist:
        raise ValueError(f"could not determine canonical artist, track_artist = {track_artist}, album_artist = {album_artist}")

    return album_artist

# connect to the specified server, returns a libsonic.Connection
def connect_airsonic(server, port, username, password):
    # We pass in the base url, the username, password, and port number
    # Be sure to use https:// if this is an ssl connection!
    conn = libsonic.Connection(baseUrl=server, username=username,
                               password=password , port=port, apiVersion="1.15")

    reply = conn.ping()
    if reply:
        print("Successfully connected to server")
    else:
        raise ValueError("Could not contact server, ensure the information in the config is correct and the server includes http:// or https://")

    return conn

# prompts a scan of the media folder, waits for the scan to complete to return
def scan_media_folders(airsonic_api):
    def scanning():
        status = airsonic_api.getScanStatus()
        return status.get("scanStatus").get("scanning")

    print("initiating airsonic media scan")
    airsonic_api.startScan()
    while(scanning()):
        print("scanning...")
        time.sleep(2)

def import_songs_airsonic(import_dir, airsonic_library_dir):
    _, _, song_files = next(os.walk(import_dir), (None, None, []))

    songs = []

    print(f"importing {len(song_files)} songs...")

    for song_file in song_files:
        audiofile = eyed3.load(f"{import_dir}/{song_file}")

        # multiple artists will look like artist1;artist2;artist3
        artist_dir = canonical_artist(audiofile)
        album_dir = sanitize_filename(audiofile.tag.album)
        song_dir = f"{airsonic_library_dir}/{artist_dir}/{album_dir}"
        os.makedirs(song_dir, exist_ok=True)
        shutil.copy2(f"{import_dir}/{song_file}", song_dir)

        #TODO which provides better airsonic search results, straight id3 tags or sanitized canonical versions?
        # id3 tags seems to be good
        song = Song(name=audiofile.tag.title,
                    artist=audiofile.tag.artist,
                    album=audiofile.tag.album,
                    original_file=f"{import_dir}/{song_file}",
                    airsonic_library_file=f"{song_dir}/{song_file}")

        songs.append(song)

    return songs

def get_airsonic_song_ids(airsonic_api, songs):
    def get_songid(airsonic_api, song):
        print(f"Looking for song {song}")
        searchQuery = song.name + " " + song.artist
        reply = airsonic_api.search3(searchQuery, artistCount=1, albumCount=1, songCount=1)

        #peel back the artist and album layers to get the song id
        searchResult = reply.get("searchResult3")
        res = searchResult.get("song")
        res = res[0] #peel back the list, since we only expect one result

        print(f"Found song       name: {res.get('title')}, artist: {res.get('artist')}, album: {res.get('album')}, library_file: {res.get('path')}, id: {res.get('id')}")

        song.airsonic_song_id = res.get("id")
        return

    for song in songs:
        get_songid(airsonic_api, song)

def get_create_playlist(airsonic_api):

    def find_playlist(name):
        reply = airsonic_api.getPlaylists()
        if not reply:
            raise ValueError("Could not contact server, ensure the information in the config is correct and the server includes http:// or https://")

        playlists = reply.get("playlists").get("playlist")
        for playlist in playlists:
            if (playlist.get("name") == name):
                playlistId = playlist.get("id")
                return playlistId

        return None

    def create_playlist(name):
# def createPlaylist(self, playlistId=None, name=None, songIds=[]):
#         """
#         since: 1.2.0
#         Creates OR updates a playlist.  If updating the list, the
#         playlistId is required.  If creating a list, the name is required.
#         playlistId:str      The ID of the playlist to UPDATE
#         name:str            The name of the playlist to CREATE
#         songIds:list        The list of songIds to populate the list with in
#                             either create or update mode.  Note that this
#                             list will replace the existing list if updating
#         Returns a dict like the following:
#         {u'status': u'ok',
#          u'version': u'1.5.0',
#          u'xmlns': u'http://subsonic.org/restapi'}
#         """
        reply = airsonic_api.createPlaylist(playlistId=None, name=curr_name)
        if not reply:
            raise ValueError("Could not contact server, ensure the information in the config is correct and the server includes http:// or https://")


    date = datetime.datetime.now()
    curr_name = date.strftime("%Y") + " " + date.strftime("%m") + " " + date.strftime("%B")
    playlist_id = find_playlist(curr_name)
    if playlist_id:
        return playlist_id

    # not found, lets make it
    create_playlist(curr_name)
    playlist_id = find_playlist(curr_name)
    if not playlist_id:
        raise ValueError("Unable to find the playlist after creating it, name: {curr_name}")

    return playlist_id


def update_playlist(airsonic_api, playlist_id, songs):
    ids = [song.airsonic_song_id for song in songs]

# def createPlaylist(self, playlistId=None, name=None, songIds=[]):
#         """
#         since: 1.2.0
#         Creates OR updates a playlist.  If updating the list, the
#         playlistId is required.  If creating a list, the name is required.
#         playlistId:str      The ID of the playlist to UPDATE
#         name:str            The name of the playlist to CREATE
#         songIds:list        The list of songIds to populate the list with in
#                             either create or update mode.  Note that this
#                             list will replace the existing list if updating
#         Returns a dict like the following:
#         {u'status': u'ok',
#          u'version': u'1.5.0',
#          u'xmlns': u'http://subsonic.org/restapi'}
#         """
    reply = airsonic_api.createPlaylist(playlistId=playlist_id, name=None, songIds=ids)
    if not reply:
        raise ValueError("Could not contact server, ensure the information in the config is correct and the server includes http:// or https://")

    print(f"Added {len(ids)} songs to playlist {playlist_id}")

@click.command()
@click.option("--airsonic_username", type=str, required=True, help="username of the user to login as")
@click.option("--airsonic_password", type=str, required=True, help="password of the user to login as")
@click.option("--server", type=str, required=True, help="server url")
@click.option("--port", type=str, required=True, help="server port")
@click.option("--import_dir", type=str, required=True, help="directory to import music from")
@click.option("--airsonic_library_dir", type=str, required=True, help="directory to import music to")
@click.option("--empty_import_dir", is_flag=True, default=False, help="remove all songs from the import_dir when complete")
def main(airsonic_username, airsonic_password, server, port, import_dir, airsonic_library_dir, empty_import_dir):

    if not os.path.isdir(import_dir):
        raise ValueError(f"import directory does not exist: {import_dir}")
    if not os.path.isdir(airsonic_library_dir):
        raise ValueError(f"airsonic library directory does not exist: {airsonic_library_dir}")

    airsonic_api = connect_airsonic(server, port, airsonic_username, airsonic_password)
    songs = import_songs_airsonic(import_dir, airsonic_library_dir)
    scan_media_folders(airsonic_api)
    get_airsonic_song_ids(airsonic_api, songs)
    playlist_id = get_create_playlist(airsonic_api)
    update_playlist(airsonic_api, playlist_id, songs)

    if empty_import_dir:
        for song in songs:
            os.remove(song.original_file)






if __name__ == "__main__":
    main()
