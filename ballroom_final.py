import argparse
import json
import os
import random
import re
import sys
import yt_dlp

from dotenv import load_dotenv
from ytmusicapi import YTMusic


ALL_DANCES = [
        "slow_waltz",
        "tango",
        "viennese_waltz",
        "slow_foxtrot",
        "quickstep"
    ]

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
    download, level, song_length, pause_length = parse_arguments()
    dances = select_relevant_dances(level)

    # check for the presence of directories and songs for each dance
    songs_present = check_for_songs(dances)

    # download songs if the download flag is given or any dance directory was empty
    if download or any(not songs_present[dance] for dance in dances): 
        set_up_downloads(playlist_ids)

    # select and play songs for the final
    for dance in dances:
        song = select_song(dance, song_length)
        play_song(song)
        take_break(dance, dances, pause_length)


def check_for_songs(dances):
    """ Check if downloaded songs are present for each dance and return a dict with boolean values """
    songs_present = {}
    for dance in dances:
        dir_path = generate_dir_path(dance)
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


def clear_directories(dances):
    """ Delete all files from the directories of each dance """
    for dance in dances:
        dir_path = generate_dir_path(dance)
        files = os.listdir(dir_path)
        if files:
            for file in files:
                file_path = os.path.join(dir_path, file)
                if os.path.isfile(file_path):
                    try:
                        os.remove(file_path)
                    except FileNotFoundError:
                        pass
    return


def construct_video_url(track):
    """ Return the YouTube video URL for a given track as a string """
    return f"https://www.youtube.com/watch?v={track["videoId"]}"

    
def download_audio(url, dir_path):
    """ Download a YouTube video as a .mp3 audio file """
    # save file with video id as file name to find it later
    video_id = url.split("v=")[-1].split("&")[0]
    output_template = os.path.join(dir_path, video_id)
    ydl_opts = {
        "format": "bestaudio",
        "outtmpl": output_template,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192"
        }]
    }
    with yt_dlp.YoutubeDL(ydl_opts) as video:
        video.download([url])
    return


def download_yt_tracks(tracks, dance):
    """ Download the specified tracks into the relevant folder """
    dir_path = generate_dir_path(dance)
    for track in tracks:
        url = construct_video_url(track)
        download_audio(url, dir_path)
    return


def extract_playlist_ids(playlists):
    """ Extract YouTube Playlist IDs from URLs """
    playlist_ids = []
    for playlist in playlists:
        match = re.search(r"[?&]list=([^&]+)", playlist)
        if match:
            playlist_ids.append(match.group(1))
        else:
            sys.exit(f"Invalid playlist URL: {playlist}")
    return playlist_ids


def extract_song_list(dir_path):
    """ Returns the list of tracks stored in JSON in the given directory """
    #TODO
    return tracks


def generate_dir_path(dance):
    """ Return the path to the directory of a given dance """
    this_dir = os.getcwd()
    dir_name = dance
    return os.path.join(this_dir, dir_name)


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


def play_song(song):
    #TODO
    return


def select_relevant_dances(level):
    """ Return a list of the relevant dances for the given level """
    if level == "d":
        return ["slow_waltz", "tango", "quickstep"]
    elif level == "c":
        return ["slow_waltz", "tango", "slow_foxtrot", "quickstep"]
    else:
        return ALL_DANCES


def select_song(dance, song_length):
    """ Return video ID of a randomly selected song """
    # get list of tracks and metadata from tracks.json
    dir_path = generate_dir_path(dance)
    tracks = extract_song_list(dir_path)
    # filter the tracks of correct length
    applicable_tracks = []
    if song_length == "long":
        min_length, max_length = 115, 130
    else:
        min_length, max_length = 90, 115
    for track in tracks:
        if min_length <= track["duration"] <= max_length:
            applicable_tracks.append(track["videoId"]) 
    # randomly select a song out of the applicable tracks
    return random.choice(applicable_tracks)

    
def set_up_downloads(playlist_ids):
    """ Clear dance style directories and fill them with current content of playlists """    
    clear_directories(ALL_DANCES)
    for index, dance in enumerate(ALL_DANCES):
        # select correct playlist and retrieve information about its tracks
        playlist_id = playlist_ids[index]
        ytmusic = YTMusic()
        playlist = ytmusic.get_playlist(playlistId=playlist_id, limit=None)
        # save a metadata.json file with track title, videoId, and duration in seconds for all tracks
        tracks = [
            {
                "title": track["title"],
                "index": i, 
                "videoId": track["videoId"],
                "duration": track["duration_seconds"]
            }
            for i, track in enumerate(playlist["tracks"])
        ]
        with open(f"{dance}/tracks.json", "w") as f:
            json.dump(tracks, f)
        # download the tracks
        download_yt_tracks(tracks, dance)


def take_break(dance, dances, pause_length):
    #TODO
    return


if __name__ == "__main__":
    main()
