import json
import os
import pytest
import sys
import yt_dlp

from project import (
    ALL_DANCES,
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
from unittest.mock import patch


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

    clear_directories(["test_dance_2"])

    assert not os.path.exists("test_dance_2/song.mp3")
    assert not os.path.exists("test_dance_2/other_file.txt")
    assert os.path.exists("test_dance_2")

    os.rmdir("test_dance_2")


def test_construct_video_url():

    assert construct_video_url({"videoId": "abc123"}) == "https://www.youtube.com/watch?v=abc123"

    with pytest.raises(ValueError):
        construct_video_url("not_a_dict")
        construct_video_url(123)

    with pytest.raises(KeyError):
        construct_video_url({})
        construct_video_url({"videoId": 123})


def test_download_audio():

    with pytest.raises(ValueError):
        download_audio("not_a_url", "test_dir")
        download_audio("https://example.com/video", "test_dir")
        download_audio("https://www.youtube.com/watch?v=abc123", 123)

    with patch.object(yt_dlp.YoutubeDL, "download", return_value=None) as mock_download:
        download_audio("https://www.youtube.com/watch?v=abc123", "test_dir")
        mock_download.assert_called_once()


def test_download_yt_tracks():

    with pytest.raises(ValueError):
        download_yt_tracks("not_a_list", "slow_waltz")
        download_yt_tracks([{"videoId": "abc123"}], 123)
        download_yt_tracks([123, {"videoId": "abc123"}], "slow_waltz")

    tracks = [{"videoId": "abc123"}, {"videoId": "def456"}]

    with patch("project.construct_video_url", return_value="https://www.youtube.com/watch?v=abc123"), \
         patch("project.download_audio") as mock_download:

        download_yt_tracks(tracks, "slow_waltz")

        assert mock_download.call_count == 2


def test_extract_playlist_ids():

    assert extract_playlist_ids(["https://www.youtube.com/playlist?list=PL123"]) == ["PL123"]

    assert extract_playlist_ids([
        "https://www.youtube.com/playlist?list=PL123",
        "https://www.youtube.com/watch?v=xyz&list=PL456",
        "https://www.youtube.com/playlist?list=PL789&feature=share"
    ]) == ["PL123", "PL456", "PL789"]

    with pytest.raises(ValueError):
        extract_playlist_ids("not_a_list")
        extract_playlist_ids([123, "https://www.youtube.com/playlist?list=PL123"])
        extract_playlist_ids(["https://www.youtube.com/watch?v=xyz"])
        extract_playlist_ids(["https://www.example.com/not_youtube"])


def test_extract_song_list():

    with pytest.raises(ValueError):
        extract_song_list(123)

    with pytest.raises(FileNotFoundError):
        extract_song_list("non_existent_dir")

    os.makedirs("test_dir", exist_ok=True)
    valid_data = [{"title": "Song 1", "videoId": "abc123", "duration": 120}]
    with open("test_dir/tracks.json", "w") as f:
        json.dump(valid_data, f)

    assert extract_song_list("test_dir") == valid_data

    with open("test_dir/tracks.json", "w") as f:
        f.write("{invalid_json")

    with pytest.raises(ValueError):
        extract_song_list("test_dir")

    with open("test_dir/tracks.json", "w") as f:
        json.dump({"title": "Not a list"}, f)

    with pytest.raises(ValueError):
        extract_song_list("test_dir")

    os.remove("test_dir/tracks.json")
    os.rmdir("test_dir")


def test_generate_dir_path():

    assert generate_dir_path("slow_waltz") == os.path.join(os.getcwd(), "slow_waltz")

    with pytest.raises(ValueError):
        generate_dir_path(123)
        generate_dir_path("")
        generate_dir_path("   ")


def test_parse_arguments():

    with patch.object(sys, "argv", ["script.py"]):
        assert parse_arguments() == (False, "b", "normal", 30)

    with patch.object(sys, "argv", ["script.py", "--download"]):
        assert parse_arguments() == (True, "b", "normal", 30)

    with patch.object(sys, "argv", ["script.py", "--klasse", "c"]):
        assert parse_arguments() == (False, "c", "normal", 30)

    with patch.object(sys, "argv", ["script.py", "--length", "long"]):
        assert parse_arguments() == (False, "b", "long", 30)

    with patch.object(sys, "argv", ["script.py", "--pause", "45"]):
        assert parse_arguments() == (False, "b", "normal", 45)

    with patch.object(sys, "argv", ["script.py", "--download", "--klasse", "d", "--length", "long", "--pause", "60"]):
        assert parse_arguments() == (True, "d", "long", 60)

    with patch.object(sys, "argv", ["script.py", "--klasse", "x"]):
        assert parse_arguments() == (False, "b", "normal", 30)

    with patch.object(sys, "argv", ["script.py", "--length", "short"]):
        assert parse_arguments() == (False, "b", "normal", 30)

    with patch.object(sys, "argv", ["script.py", "--pause", "-5"]):
        assert parse_arguments() == (False, "b", "normal", 30)


def test_play_song():

    with pytest.raises(ValueError):
        play_song(123, "song")
        play_song("test_dir", 123)

    with pytest.raises(FileNotFoundError):
        play_song("non_existent_dir", "song")

    os.makedirs("test_dir", exist_ok=True)
    with open("test_dir/song.mp3", "w") as f:
        f.write("dummy data")

    with patch("subprocess.run") as mock_run:
        play_song("test_dir", "song")
        mock_run.assert_called_once_with(["mpv", "--no-terminal", "--quiet", "test_dir/song.mp3"], check=True)

    os.remove("test_dir/song.mp3")
    os.rmdir("test_dir")


def test_select_relevant_dances():

    assert select_relevant_dances("d") == ["slow_waltz", "tango", "quickstep"]
    assert select_relevant_dances("c") == ["slow_waltz", "tango", "slow_foxtrot", "quickstep"]
    assert select_relevant_dances("b") == ALL_DANCES 

    assert select_relevant_dances("D") == ["slow_waltz", "tango", "quickstep"]
    assert select_relevant_dances("C") == ["slow_waltz", "tango", "slow_foxtrot", "quickstep"]
    assert select_relevant_dances("B") == ALL_DANCES 

    with pytest.raises(ValueError):
        select_relevant_dances(123)
        select_relevant_dances("x")
        select_relevant_dances("")


def test_select_song():
    
    with pytest.raises(ValueError):
        select_song(123, "long")
        select_song("test_dir", "short")

    os.makedirs("test_dir", exist_ok=True)
    valid_data = [
        {"videoId": "abc123", "duration": 120},
        {"videoId": "def456", "duration": 95}
    ]
    with open("test_dir/tracks.json", "w") as f:
        json.dump(valid_data, f)

    with patch("random.choice", return_value="abc123"):
        assert select_song("test_dir", "long") == "abc123"

    with patch("random.choice", return_value="def456"):
        assert select_song("test_dir", "normal") == "def456"

    with open("test_dir/tracks.json", "w") as f:
        json.dump([{"videoId": "xyz789", "duration": 150}], f)

    with pytest.raises(ValueError):
        select_song("test_dir", "long")

    os.remove("test_dir/tracks.json")
    os.rmdir("test_dir")


