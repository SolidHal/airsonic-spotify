#!/usr/bin/env python3
import os
import shutil
import schedule
import subprocess
import time


def main():

    def get_envar(envar):
        val = os.environ[envar]
        if val == "":
            raise ValueError(f"envar may not be empty")
        return val

    # check all the env vars
    spotipy_client_id = get_envar("SPOTIPY_CLIENT_ID")
    spotipy_client_secret = get_envar("SPOTIPY_CLIENT_SECRET")
    spotipy_redirect_uri = get_envar("SPOTIPY_REDIRECT_URI")
    spotify_username = get_envar("SPOTIFY_USERNAME")
    spotify_password = get_envar("SPOTIFY_PASSWORD")
    spotify_playlist_uri = get_envar("SPOTIFY_PLAYLIST_URI")
    airsonic_username = get_envar("AIRSONIC_USERNAME")
    airsonic_password = get_envar("AIRSONIC_PASSWORD")
    airsonic_server = get_envar("AIRSONIC_SERVER")
    airsonic_port = get_envar("AIRSONIC_PORT")

    # ensure we have the required directories
    airsonic_library_dir = "/airsonic"
    temp_import_dir = "/import"
    if not os.path.isdir(temp_import_dir):
        raise ValueError(f"import directory does not exist: {temp_import_dir}")
    if not os.path.isdir(airsonic_library_dir):
        raise ValueError(f"airsonic library directory does not exist: {airsonic_library_dir}")

    # ensure we have the required spotipy api cache
    spotipy_cache = f"/.cache-{spotify_username}"
    if not os.path.isfile(spotipy_cache):
        raise ValueError(f"spotipy authentication cache file is not avilable at: {spotipy_cache}")

    def run_update_spotify_playlist():
        print("____ airsonic-spotify: START updating spotify playlist with new songs _____")
        # will this run in the root dir? if not then the cache token won't be available
        script = "/usr/bin/spotify_update_playlist.py"
        # spotipy envars are provided by the caller
        args = [script,
                "--playlist_id", spotify_playlist_uri,
                "--username", spotify_username]
        print(f"Running process {args}")
        subprocess.run(args)
        print("____ airsonic-spotify: FINISHED updating spotify playlist with new songs _____")

    def run_tsar_and_import():
        run_update_spotify_playlist()

        print("____ airsonic-spotify: START running tsar ____")
        script = "/usr/bin/tsar.py"
        args = [script,
                "--output_dir", temp_import_dir,
                "--playlist_id", spotify_playlist_uri,
                "--username", spotify_username,
                "--password", spotify_password,
                "--librespot_binary", "/usr/bin/librespot",
                "--empty_playlist"]
        print(f"Running process {args}")
        subprocess.run(args)
        print("____ airsonic-spotify: FINISHED running tsar ____")

        print("_____ airsonic-spotify: START importing new songs into airsonic ____")
        script = "/usr/bin/airsonic_import.py"
        args = [script,
                "--airsonic_username", airsonic_username,
                "--airsonic_password", airsonic_password,
                "--server", airsonic_server,
                "--port", airsonic_port,
                "--import_dir", temp_import_dir,
                "--airsonic_library_dir", airsonic_library_dir,
                "--empty_import_dir"]
        print(f"Running process {args}")
        subprocess.run(args)
        print("_____ airsonic-spotify: FINISHED importing new songs into airsonic ____")


    schedule.every().hour.do(run_update_spotify_playlist)
    schedule.every(1).day.at("04:03").do(run_tsar_and_import)

    print("____ Running airsonic-spotify ____")
    print(f"ENVARS: {os.environ}")
    print("waiting for scheduled tasks...")

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()
