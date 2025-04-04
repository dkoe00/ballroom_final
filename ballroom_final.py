import argparse
import time

from helpers import (
    extract_playlist_ids,
    generate_dir_path,
    play_song,
    select_relevant_dances,
    select_relevant_playlists,
    select_song,
    set_up_downloads
)


def main():
    
    # get environment variables, command line arguments and other setup
    download, level, song_length, pause_length, section = parse_arguments()
    playlists = select_relevant_playlists(section, level)

    if any(not playlist for playlist in playlists):
        raise ValueError("Please provide playlist URLs for each dance in .env file")

    playlist_ids = extract_playlist_ids(playlists)
    dances = select_relevant_dances(level, section)

    # download songs if the download flag is given or any dance directory was empty
    set_up_downloads(download, dances, playlist_ids)

    # select and play songs for the final
    for dance in dances:
        dir_path = generate_dir_path(dance)
        song = select_song(dir_path, song_length)
        print(f"Playing {dance}")
        play_song(dir_path, song)
        print(f"Waiting {pause_length} seconds...")
        take_break(dance, dances, pause_length)


def parse_arguments():
    """ Parse optional command line arguments and return default values if not given """
    
    # create a list of given arguments
    parser = argparse.ArgumentParser(description="Play ballroom final music")
    parser.add_argument("--download", "-d", help="Download all songs from playlists first", action="store_true")
    parser.add_argument("--klasse", "-k", help="Specify the class of the final (d, c, b for b and up)", 
                        type=str, default="b", choices=["b", "c", "d"])
    parser.add_argument("--length", "-l", help="Specify length of songs (long for 1:50-2:10, normal for 1:30-1:50)", 
                        type=str, default="normal", choices=["long", "normal"])
    parser.add_argument("--pause", "-p", help="Specify pause time between titles in seconds", 
                        type=int, default=30)
    parser.add_argument("section", help="Specify if you want a standard or latin final", 
                        type=str, choices=["standard", "latin"])

    args = parser.parse_args()

    # set defaults
    level = args.klasse if args.klasse in ["d", "c", "b"] else "b"
    song_length = args.length if args.length in ["long", "normal"] else "normal"
    pause_length = args.pause if args.pause is not None and args.pause >= 0 else 30
    section = args.section if args.section in ["standard", "latin"] else "standard"

    return args.download, level, song_length, pause_length, section


def take_break(dance, dances, pause_length):
    """ Wait the specified time if appropriate """
    
    if not isinstance(dance, str):
        raise ValueError("Invalid input: dance must be a string")

    if not isinstance(dances, list) or not all(isinstance(d, str) for d in dances):
        raise ValueError("Invalid input: dances must be a list of strings")

    if not isinstance(pause_length, (int, float)) or pause_length < 0:
        raise ValueError("Invalid input: pause_length must be a non-negative number")

    if 3 <= len(dances) <= 5 and dance not in ["quickstep", "jive"]:
        time.sleep(pause_length)


if __name__ == "__main__":
    main()
