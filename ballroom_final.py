import argparse
import os
import re

from dotenv import load_dotenv
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
    playlist_ids = extract_playlist_ids(playlists)
    ytmusic = YTMusic()
    download, level, song_length, pause_length = parse_arguments()
    dances = [
        "slow_waltz",
        "tango",
        "viennese_waltz",
        "slow_foxtrot",
        "quickstep"
    ]

    # check for the presence of directories and songs for each dance
    songs_present = check_for_songs(dances)

    # download songs if the download flag is given or any dance directory was empty
    if download or any(not songs_present[dance] for dance in dances): 
        for index, dance in enumerate(dances):
            # select correct playlist and 
            playlist = playlists[index]


def check_for_songs(dances)
    """ Check if downloaded songs are present for each dance and return a dict with boolean values """
    songs_present = {}
    this_dir = os.path.dirname(os.path.abspath(__file__))
    for dance in dances:
        dir_name = dance
        dir_path = os.path.join(this_dir, dir_name)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            songs_present[dance] = False
        else:
            matching_files = [f for f in os.listdir(dir_path) if f.endswith((".mp3", ".mp4"))]
            if matching_files:
                songs_present[dance] = True
            else:
                songs_present[dance] = False
    return songs_present

def extract_playlist_ids(playlists):
    """ Extract YouTube Playlist IDs from URLs """
    playlist_ids = []
    for playlist in playlists:
        id = re.search(r"^.*playlist?list=(.*)$", playlist)
        playlist_id = id[0]
        if not playlist_id:
            sys.exit("Invalid playlist URL")
        playlist_ids.append(playlist_id)
    return playlist_ids


def parse_arguments():
    """ Parse optional command line arguments and return default values if not given """
    
    # create a list of given arguments
    parser = argparse.ArgumentParser(description="Play ballroom final music")
    parser.add_argument("--download", "-d", help="Download all songs from playlists first", action="store_true")
    parser.add_argument("--klasse", "-k", help="Specify the class of the final (d, c, b for b and up)", type=str)
    parser.add_argument("--length", "-l", help="Specify length of songs (long for 1:50-2:10, normal for 1:30-1:50)", type=str)
    parser.add_argument("--pause", "-p", help="Specify pause time between titles in seconds", type=int)

    args = parser.parse_args()

    # handle optional arguments
    download = args.download
    level = args.klasse if args.klasse else "b"
    song_length = args.length if args.length else "normal"
    pause_length = args.pause if args.pause else 30

    return download, level, song_length, pause_length


if __name__ == "__main__":
    main()
