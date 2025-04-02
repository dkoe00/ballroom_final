import argparse

from helpers import (
    #TODO
    select_relevant_playlists,
    set_up_downloads
)


VALID_STYLES = [
    "slow_waltz", "tango", "viennese_waltz", "slow_foxtrot", "quickstep",
    "samba", "chacha", "rumba", "paso", "jive"
]


def main():

    download, length, number, style = parse_arguments()
    
    playlist = select_relevant_playlists(style, None)
    set_up_downloads(download, [style], playlist)



def parse_arguments():
    """ Parse optional command line argumenmts and return default values if not given """

    parser = argparse.ArgumentParser(description="Play music for a specific dance style")
    parser.add_argument("--download", "-d", help="Download all songs from playlist first", action="store_true")
    parser.add_argument("--length", "-l", help="Specify length of songs: long, normal, or any", 
                        type=str, default="any", choices=["long", "normal", "any")
    parser.add_argument("--number", "-n", help="Specify number of songs", 
                        type=int, default=10)
    parser.add_argument("style", help="Specify dance style", 
                        type=str, choices=VALID_STYLES)

    args = parser.parse_args()

    return args.download, args.length, args.number, args.style


if __name__ == "__main__":
    main()
