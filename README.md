# ballroom_final

## Overview
This Python-based application is designed to automate the music selection process for ballroom dance finals. It ensures that the correct sequence of dance music is played with appropriate breaks, allowing dancers and organizers to focus on the competition or training rather than managing music manually.

The system supports five standard ballroom dances:
- Slow Waltz
- Tango
- Viennese Waltz
- Slow Foxtrot
- Quickstep

## Features
- **Automated Song Selection**: Randomly selects a song from pre-defined YouTube Music playlists for each dance.
- **Customizable Timing**: Adjust song length and pause times as needed.
- **Download & Play Modes**: Download songs in advance or play directly from stored tracks.
- **Reliable Playback**: Uses `mpv` for seamless playback without interruptions.
- **Error Handling & Logging**: Ensures robust error management and logging for troubleshooting.

#### Video Demo: [YouTube](https://youtu.be/QbHGec2kiUE)
## Installation
### Prerequisites
Ensure the following system dependencies are installed:
- Python 3.8+
- `mpv` for audio playback
- `ffmpeg` for audio conversion

On macOS, install them using:
```bash
brew install python mpv ffmpeg
```

Install the required Python dependencies:
```bash
pip install -r requirements.txt
```

### Setting Up
1. **Clone the repository:**
   ```bash
   git clone git@github.com:dkoe00/ballroom_final
   cd ballroom_final
   ```
2. **Set Up Environment Variables:**
   - Create a `.env` file in the project root.
   - Add YouTube Music playlist URLs for each dance in the following format:
     ```env
     SLOW_WALTZ_URL=https://music.youtube.com/playlist?list=...
     TANGO_URL=https://music.youtube.com/playlist?list=...
     VIENNESE_WALTZ_URL=https://music.youtube.com/playlist?list=...
     SLOW_FOXTROT_URL=https://music.youtube.com/playlist?list=...
     QUICKSTEP_URL=https://music.youtube.com/playlist?list=...
     ```
3. **Run the Program:**
   ```bash
   python ballroom_final.py
   ```

## Usage
### Command-Line Options
The program provides various arguments for customization:
```bash
python ballroom_final.py [OPTIONS]
```
- `-d`, `--download` : Clear stored songs and download the songs currently in the YouTube playlists. Default: False, not required on first use.
- `-k`, `--klasse` : Specify competition level (`d`, `c`, `b`). Default: `b` for all five dance styles.
- `-l`, `--length` : Choose song length (`long` for 1:50-2:10, `normal` for 1:30-1:50). Default: `normal`.
- `-p`, `--pause` : Specify pause duration in seconds between songs. Default: `30` seconds.

**Example:**
```bash
python ballroom_final.py -d -k c -l long -p 45 
```
This redownloads all songs, plays for class `C`, selects long songs, and introduces a 45-second pause between tracks.

## Technical Documentation
### Error Handling
- Missing `.env` variables cause an immediate program exit.
- Invalid URLs or download failures trigger logged error messages.
- Ensures `mpv` is available for playback; otherwise, an error is raised.

## For Dancers and Event Organizers
- **Minimal Technical Knowledge Required**: Once set up, the system runs automatically.
- **Pre-Download Songs**: Ensures smooth playback without internet dependency during events.
- **Customizable Timing**: Adjust pause length and song duration according to competition requirements.
- **One-Time Setup**: After playlists are added, the system requires little maintenance.

## Troubleshooting
### Common Issues
1. **Songs not playing?**
   - Ensure `mpv` is installed and accessible from the command line.
   - Check if downloaded MP3 files exist in the correct directories.

2. **Error: `Please provide playlist URLs`?**
   - Ensure the `.env` file is correctly configured with valid YouTube Music playlist URLs.

3. **Download Issues?**
   - Ensure `yt-dlp` and `ffmpeg` are installed.
   - Check for internet connectivity.

## License
This project is licensed under the MIT License.

## Contributing
We welcome contributions! Feel free to open issues or submit pull requests to improve the application.


