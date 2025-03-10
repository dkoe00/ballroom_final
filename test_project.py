import os
import pytest

from project import (
    check_for_songs,
    clear_directories, 
    construct_video_url, 
    download_audio, 
    download_yt_tracks, 
    extract_playlist_ids, 
    extract_song_list, 
    generate_dir_path, 
    parse_arguments,
    play_song, 
    select_relevant_dances, 
    select_song, 
    set_up_downloads, 
    take_break
)


def test_check_for_songs():
    
    with pytest.raises(ValueError):
        check_for_songs("not_a_list")
        check_for_songs([123, "valid_dance"])

    dances = ["nonexistent_dance"]
    results = check_for_songs(dances)
    assert results == {"nonexistent_dance": False}

    os.makedirs("test_dance_1", exist_ok=True)
    results = check_for_songs(["test_dance_1"])
    assert results == {"test_dance_1": False}

    with open("test_dance_1/song.mp3", "w") as f:
        f.write("dummy data")
    results = check_for_songs(["test_dance_1"])
    assert results == {"test_dance_1": True}

    os.remove("test_dance_1/song.mp3")
    os.rmdir("test_dance_1")


def test_clear_directories():

    with pytest.raises(ValueError):
        clear_directories("not_a_list")
        clear_directories([123, "valid_dance"])

    os.makedirs("test_dance_2", exist_ok=True)
    with open("test_dance_2/song.mp3", "w") as f:
        f.write("dummy data")

    with open("test_dance_2/other_file.txt", "w") as f:
        f.write("dummy data")

    assert os.path.exists("test_dance_2/song.mp3")
    assert os.path.exists("test_dance_2/other_file.txt")

    clear_directories(["test)dance)2"])

    assert not os.path.exists("test_dance_2/song.mp3")
    assert not os.path.exists("test_dance_2/other_file.txt")
    assert os.path.exists("test_dance_2")

    os.rmdir("test_dance_2")











