import argparse
import json
import logging
import os
import random
import re
import subprocess
import yt_dlp

from dotenv import load_dotenv
from ytmusicapi import YTMusic


STANDARD_DANCES = [
        "slow_waltz",
        "tango",
        "viennese_waltz",
        "slow_foxtrot",
        "quickstep"
    ]

LATIN_DANCES = [
        "samba",
        "chacha",
        "rumba",
        "paso",
        "jive"
    ]


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

    return os.path.expanduser(os.path.join("~/Projects/ballroom", dance))


def play_song(dir_path, song):
    """ Plays the given song with mpv """

    if not isinstance(dir_path, str) or not isinstance(song, str):
        raise ValueError("Invalid input: dir_path and song must be strings")

    path_to_mp3 = os.path.expanduser(os.path.join(dir_path, f"{song}.mp3"))

    if not os.path.exists(path_to_mp3):
        raise FileNotFoundError(f"File not found: {path_to_mp3}")

    try:    
        subprocess.run(["mpv", "--no-terminal", "--quiet", path_to_mp3], check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error playing song: {e}")


def refresh_downloads(playlist_ids, dances):
    """ Clear dance style directories and fill them with current content of playlists """    

    if not isinstance(playlist_ids, list) or not all(isinstance(pid, str) for pid in playlist_ids):
        raise ValueError("Invalid input: playlist_ids must be a list of strings")
    
    if not isinstance(dances, list) or not all(isinstance(d, str) for d in dances):
        raise ValueError("Invalid input: dances must be a list of strings")

    if len(playlist_ids) != len(dances):
        raise ValueError(f"Mismatch: Expected {len(dances)} playlist IDs but got {len(playlist_ids)}")

    clear_directories(dances)

    for index, dance in enumerate(dances):
        try:

            # select correct playlist and retrieve information about its tracks
            playlist_id = playlist_ids[index]
            ytmusic = YTMusic()
            playlist = ytmusic.get_playlist(playlistId=playlist_id, limit=None)

            if not playlist or "tracks" not in playlist:
                raise ValueError(f"Playlist {playlist_id} does not contain track data")
    
            # save a metadata.json file with track title, videoId, and duration in seconds for all tracks
            tracks = [
                {
                    "title": track["title"],
                    "index": i, 
                    "videoId": track["videoId"],
                    "duration": track["duration_seconds"]
                }
                for i, track in enumerate(playlist["tracks"])
                if "videoId" in track and isinstance(track.get("duration_seconds"), (int, float))
            ]

            if not tracks:
                raise ValueError(f"No valid tracks found in playlist {playlist_id}")

            dir_path = generate_dir_path(dance)
            os.makedirs(dir_path, exist_ok=True)
            with open(os.path.join(dir_path, "tracks.json"), "w") as f:
                json.dump(tracks, f)
        
            # download the tracks
            download_yt_tracks(tracks, dance)

        except Exception as e:
            logging.error(f"Error processing playlist {playlist_id} for dance {dance}: {e}")


def select_relevant_dances(level, section):
    """ Return a list of the relevant dances for the given level and section """
    
    if not isinstance(level, str):
        raise ValueError("Invalid input: level must be a string")
    if not isinstance(section, str):
        raise ValueError("Invalid input: section must be a string")
    
    if section == "standard":
        if level == "d":
            return ["slow_waltz", "tango", "quickstep"]
        elif level == "c":
            return ["slow_waltz", "tango", "slow_foxtrot", "quickstep"]
        elif level == "b":
            return STANDARD_DANCES
        else:
            raise ValueError(f"Invalid level: {level}. Must be d, c, or b.")
    elif section == "latin":
        if level == "d":
            return ["chacha", "rumba", "jive"]
        elif level == "c":
            return ["samba", "chacha", "rumba", "jive"]
        elif level == "b":
            return LATIN_DANCES
        else:
            raise ValueError(f"Invalid level: {level}. Must be d, c, or b.")
    else:
        raise ValueError(f"Invalic section: {section}. Must be standard or latin.")


def select_relevant_playlists(scope, level):
    """ Return a list with either a specific url or a list of urls """
    
    if not isinstance(scope, str):
        raise ValueError("Invalid input: scope must be a string")
    if not isinstance(level, str) and level is not None:
        raise ValueError("Invalid input: level must be a string or None")

    load_dotenv()

    if level == "b":    
        if scope == "standard":
            return [
                os.getenv("SLOW_WALTZ_URL"), 
                os.getenv("TANGO_URL"), 
                os.getenv("VIENNESE_WALTZ_URL"), 
                os.getenv("SLOW_FOXTROT_URL"), 
                os.getenv("QUICKSTEP_URL"), 
            ]
        elif scope == "latin":
            return [
                os.getenv("SAMBA_URL"),
                os.getenv("CHACHA_URL"),
                os.getenv("RUMBA_URL"),
                os.getenv("PASO_URL"),
                os.getenv("JIVE_URL")
            ]
    elif level == "c":    
        if scope == "standard":
            return [
                os.getenv("SLOW_WALTZ_URL"), 
                os.getenv("TANGO_URL"), 
                os.getenv("SLOW_FOXTROT_URL"), 
                os.getenv("QUICKSTEP_URL"), 
            ]
        elif scope == "latin":
            return [
                os.getenv("SAMBA_URL"),
                os.getenv("CHACHA_URL"),
                os.getenv("RUMBA_URL"),
                os.getenv("JIVE_URL")
            ]
    elif level == "d":    
        if scope == "standard":
            return [
                os.getenv("SLOW_WALTZ_URL"), 
                os.getenv("TANGO_URL"), 
                os.getenv("QUICKSTEP_URL"), 
            ]
        elif scope == "latin":
            return [
                os.getenv("CHACHA_URL"),
                os.getenv("RUMBA_URL"),
                os.getenv("JIVE_URL")
            ]
    elif scope == "slow_waltz":
        return [os.getenv("SLOW_WALTZ_URL")]
    elif scope == "tango":
        return [os.getenv("TANGO_URL")]
    elif scope == "viennese_waltz":
        return [os.getenv("VIENNESE_WALTZ_URL")]
    elif scope == "slow_foxtrot":
        return [os.getenv("SLOW_FOXTROT_URL")]
    elif scope == "quickstep":
        return [os.getenv("QUICKSTEP_URL")]
    elif scope == "samba":
        return [os.getenv("SAMBA_URL")]
    elif scope == "chacha":
        return [os.getenv("CHACHA_URL")]
    elif scope == "rumba":
        return [os.getenv("RUMBA_URL")]
    elif scope == "paso":
        return [os.getenv("PASO_URL")]
    elif scope == "jive":
        return [os.getenv("JIVE_URL")]
    else:
        raise ValueError("Invalid input: scope must be a section or dance style, level b, c, or d")


def select_song(dir_path, song_length):
    """ Return video ID of a randomly selected song """
    
    if not isinstance(dir_path, str):
        raise ValueError("Invalid input: dir_path must be a string")

    if song_length not in ["long", "normal", "any"]:
        raise ValueError("Invalid input: song_length must be any, long, or normal")
    
    # get list of tracks and metadata from tracks.json
    tracks = extract_song_list(dir_path)

    if not isinstance(tracks, list):
        raise ValueError("Invalid track data: Expected a list of tracks")

    # filter the tracks of correct length
    if song_length == "long":
        min_length, max_length = 115, 130
    elif song_length == "normal":
        min_length, max_length = 80, 115
    else:
        min_length, max_length = 60, 600

    applicable_tracks = [
        track["videoId"] for track in tracks
        if isinstance(track, dict) and "videoId" in track and "duration" in track and 
        isinstance(track["duration"], (int, float)) and  min_length <= track["duration"] <= max_length
    ]

    if not applicable_tracks:
        raise ValueError("No applicable tracks found for the given song length")

    # randomly select a song out of the applicable tracks
    return random.choice(applicable_tracks)

    
def set_up_downloads(download, dances, playlist_ids):
    """ Download songs if necessary """
    
    if not isinstance(dances, list) or not all(isinstance(d, str) for d in dances):
        raise ValueError("Invalid input: dances must be a list of strings")

    songs_present = check_for_songs(dances)
    if download or any(not songs_present[dance] for dance in dances):
        refresh_downloads(playlist_ids, dances)



