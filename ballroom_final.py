import argparse
import json
import logging
import os
import random
import re
import subprocess
import sys
import time
import yt_dlp

from dotenv import load_dotenv
from helpers import
from ytmusicapi import YTMusic


def main():
    
    # get environment variables, command line arguments and other setup
    load_dotenv()
    playlists = [
        os.getenv("SLOW_WALTZ_URL"), 
        os.getenv("TANGO_URL"), 
        os.getenv("VIENNESE_WALTZ_URL"), 
        os.getenv("SLOW_FOXTROT_URL"), 
        os.getenv("QUICKSTEP_URL"), 
    ]
    if any(not playlist for playlist in playlists):
        sys.exit("Please provide playlist URLs for each dance in .env file")

    playlist_ids = extract_playlist_ids(playlists)
    download, level, song_length, pause_length, section = parse_arguments()
    dances = select_relevant_dances(level, section)

    # check for the presence of directories and songs for each dance
    songs_present = check_for_songs(dances)

    # download songs if the download flag is given or any dance directory was empty
    if download or any(not songs_present[dance] for dance in dances): 
        set_up_downloads(playlist_ids)

    # select and play songs for the final
    for dance in dances:
        dir_path = generate_dir_path(dance)
        song = select_song(dir_path, song_length)
        play_song(dir_path, song)
        take_break(dance, dances, pause_length)


def take_break(dance, dances, pause_length):
    """ Wait the specified time if appropriate """
    
    if not isinstance(dance, str):
        raise ValueError("Invalid input: dance must be a string")

    if not isinstance(dances, list) or not all(isinstance(d, str) for d in dances):
        raise ValueError("Invalid input: dances must be a list of strings")

    if not isinstance(pause_length, (int, float)) or pause_length < 0:
        raise ValueError("Invalid input: pause_length must be a non-negative number")

    if 3 <= len(dances) <= 5 and dance != "quickstep":
        time.sleep(pause_length)


