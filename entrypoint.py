#!/usr/bin/env python3
import os
import shutil
import schedule
import subprocess


def main():
    # check all the env vars
    spotipy_client_id = os.environ["SPOTIPY_CLIENT_ID"]
    spotipy_client_secret = os.environ["SPOTIPY_CLIENT_SECRET"]
    spotipy_redirect_uri = os.environ["SPOTIPY_REDIRECT_URI"]
    spotify_username = os.environ["SPOTIFY_USERNAME"]
    spotify_password = os.environ["SPOTIFY_PASSWORD"]
    spotify_playlist_uri = os.environ["SPOTIFY_PLAYLIST_URI"]
    airsonic_username = os.environ["AIRSONIC_USERNAME"]
    airsonic_password = os.environ["AIRSONIC_PASSWORD"]

    # ensure we have the required directories
    airsonic_library_dir = "/airsonic"
    temp_import_dir = "/import"
    if not os.path.isdir(temp_import_dir):
        raise ValueError(f"import directory does not exist: {temp_import_dir}")
    if not os.path.isdir(airsonic_library_dir):
        raise ValueError(f"airsonic library directory does not exist: {airsonic_library_dir}")

    # ensure we have the required spotipy api cache
    #TODO we should provide a way for the user to generate this
    spotipy_cache = f"/.cache-{spotify_username}"
    if not os.path.isfile(spotipy_cache):
        raise ValueError(f"spotipy authentication cache file is not avilable at: {spotipy_cache}")

    def run_update_spotify_playlist():
        # will this run in the root dir? if not then the cache token won't be available
        script = ["/usr/bin/spotify-update-playlist.py"]
        # spotipy envars are provided by the caller
        args = ["--playlist_id", spotify_playlist_uri, "--username", spotify_username]
        proc = subprocess.run()

    def run_import_airsonic():
        script = ["/usr/bin/airsonic-import.py"]
        args = [""]
        # proc = subprocess.run()

    def run_tsar():
        script = ["/usr/bin/tsar.py"]
        args = [""]
        # proc = subprocess.run()



if __name__ == "__main__":
    main()
