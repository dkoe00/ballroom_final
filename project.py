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
        dir_path = generate_dir_path(dance)
        song = select_song(dir_path, song_length)
        play_song(dir_path, song)
        take_break(dance, dances, pause_length)


def check_for_songs(dances):
    """ Check if downloaded songs are present for each dance and return a dict with boolean values """

    if not isinstance(dances, list) or not all(isinstance(d, str) for d in dances):
        raise ValueError("Invalid input: dances must be a list of strings")

    songs_present = {}

    for dance in dances:
        try:
            dir_path = generate_dir_path(dance)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                songs_present[dance] = False
            else:
                try:
                    matching_files = [f for f in os.listdir(dir_path) if f.endswith(".mp3")]
                    songs_present[dance] = bool(matching_files)
                except OSError as e:
                    logging.error(f"Error accessing files in {dir_path}: {e}")
                    songs_present[dance] = False
        except OSError as e:
            logging.error(f"Error handling directory {dance}: {e}")
            songs_present[dance] = False

    return songs_present


def clear_directories(dances):
    """ Delete all files from the directories of each dance """

    if not isinstance(dances, list) or not all(isinstance(d, str) for d in dances):
        raise ValueError("Invalid input: dances must be a list of strings")

    for dance in dances:
        try:
            dir_path = generate_dir_path(dance)

            if not os.path.exists(dir_path):
                logging.warning(f"Directory {dir_path} does not exist, skipping.")
                continue

            files = os.listdir(dir_path)

            for file in files:
                file_path = os.path.join(dir_path, file)
                if os.path.isfile(file_path):
                    try:
                        os.remove(file_path)
                    except OSError as e:
                        logging.error(f"Failed to delete {file_path}: {e}")
                    except FileNotFoundError:
                        pass
        except OSError as e:
            logging.error(f"Error accessing directory {dir_path}: {e}")



def construct_video_url(track):
    """ Return the YouTube video URL for a given track as a string """
    
    if not isinstance(track, dict):
        raise ValueError("Invalid input: track must be a dictionary")

    if "videoId" not in track or not isinstance(track["videoId"], str):
        raise KeyError("Invalid track data: 'videoId' key missing or not a string")

    return f"https://www.youtube.com/watch?v={track["videoId"]}"

    
def download_audio(url, dir_path):
    """ Download a YouTube video as a .mp3 audio file """

    if not isinstance(url, str) or "youtube.com/watch?v=" not in url:
        raise ValueError("Invalid URL: Must be a valid YouTube video link")

    if not isinstance(dir_path, str):
        raise ValueError("Invalid directory path: Must be a string")

    if not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path)
        except OSError as e:
            logging.error(f"Error creating directory {dir_path}: {e}")
            raise
    
    # save file with video id as file name to find it later
    try:
        video_id = url.split("v=")[-1].split("&")[0]
        if not video_id:
            raise ValueError("Invalid URL: Unable to extract video ID")
    except Exception as e:
        logging.error(f"Error extracting video ID from URL {url}: {e}")
        raise

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
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as video:
            video.download([url])
    except yt_dlp.utils.DownloadError as e:
        logging.error(f"Download failed for {url}: {e}")
        raise


def download_yt_tracks(tracks, dance):
    """ Download the specified tracks into the relevant folder """

    if not isinstance(tracks, list) or not all(isinstance(track, dict) for track in tracks):
        raise ValueError("Invalid input: tracks must be a list of dictionaries")

    if not isinstance(dance, str):
        raise ValueError("Invalid input: dance must be a string")

    dir_path = generate_dir_path(dance)
    
    for track in tracks:
        try:
            url = construct_video_url(track)
            download_audio(url, dir_path)
        except Exception as e:
            logging.error(f"Failed to download {track}: {e}")


def extract_playlist_ids(playlists):
    """ Extract YouTube Playlist IDs from URLs """

    if not isinstance(playlists, list) or not all(isinstance(p, str) for p in playlists):
        raise ValueError("Invalid input: playlists must be a list of strings")

    playlist_ids = []
    for playlist in playlists:
        match = re.search(r"[?&]list=([^&]+)", playlist)
        if match:
            playlist_ids.append(match.group(1))
        else:
            raise ValueError(f"Invalid playlist URL: {playlist}")
        
    return playlist_ids


def extract_song_list(dir_path):
    """ Returns the list of tracks stored in JSON in the given directory """

    if not isinstance(dir_path, str):
        raise ValueError("Invalid input: dir_path must be a string")

    json_path = os.path.join(dir_path, "tracks.json")

    if not os.path.exists(json_path):
        raise FileNotFoundError(f"File not found: {json_path}")

    try:
        with open(json_path, "r") as f:
            tracks = json.load(f)

        if not isinstance(tracks, list) or not all(isinstance(t, dict) for t in tracks):
            raise ValueError(f"Invalid file format: Expected a list of dictionaries, got {type(tracks).__name__}")
    
        return tracks
    
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON format in file: {json_path}")


def generate_dir_path(dance):
    """ Return the path to the directory of a given dance """

    if not isinstance(dance, str) or not dance.strip():
        raise ValueError("Invalid input: dance must be a non-empty string")

    return os.path.join(os.getcwd(), dance)


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


def play_song(dir_path, song):
    """ Plays the given song with mpv """
    path_to_mp3 = f"{dir_path}/{song}.mp3"
    subprocess.run(["mpv", "--no-terminal", "--quiet", path_to_mp3])


def select_relevant_dances(level):
    """ Return a list of the relevant dances for the given level """
    if level == "d":
        return ["slow_waltz", "tango", "quickstep"]
    elif level == "c":
        return ["slow_waltz", "tango", "slow_foxtrot", "quickstep"]
    else:
        return ALL_DANCES


def select_song(dir_path, song_length):
    """ Return video ID of a randomly selected song """
    # get list of tracks and metadata from tracks.json
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
    """ Wait the specified time if appropriate """
    if 3 <= len(dances) <= 5 and dance != "quickstep":
        time.sleep(pause_length)


if __name__ == "__main__":
    main()
