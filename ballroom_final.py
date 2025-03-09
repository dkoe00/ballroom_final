import argparse


def main():
   level, song_length, pause_length = parse_arguments()


def parse_arguments():
    """ Parse optional command line arguments and return default values if not given """
    
    # create a list of given arguments
    parser = argparse.ArgumentParser(description="Play ballroom final music")
    parser.add_argument("--klasse", "-k", help="Specify the class of the final (d, c, b for b and up)", type=str)
    parser.add_argument("--length", "-l", help="Specify length of songs (long for 1:50-2:10, normal for 1:30-1:50)", type=str)
    parser.add_argument("--pause", "-p", help="Specify pause time between titles in seconds", type=int)

    args = parser.parse_args()

    # handle optional arguments
    level = args.klasse if args.klasse else "b"
    song_length = args.length if args.length else "normal"
    pause_length = args.pause if args.pause else 30

    return level, song_length, pause_length


if __name__ == "__main__":
    main()
