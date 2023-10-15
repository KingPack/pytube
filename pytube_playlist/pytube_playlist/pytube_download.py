from pytube import Playlist, YouTube
from colorama import Fore, Style, init
from moviepy.editor import AudioFileClip
import os

playlist_url = 'PLgOTmTz9Gp0hAdnZ4B1QmQfhRgTq_62jF'
playlist_url_2 = 'PLgOTmTz9Gp0j-sDID4H5MXVSb8-rDNXWq'
playlist_url_3 = 'PLgOTmTz9Gp0joP1E9-gy4UjCchdTB6teR'

# Color codes using colorama
RED = Fore.RED
GREEN = Fore.GREEN
YELLOW = Fore.YELLOW
RESET = Style.RESET_ALL

init()


def convert_mp4_to_mp3(input_path, output_path):
    try:
        audio_clip = AudioFileClip(input_path)
        audio_clip.write_audiofile(output_path, codec='mp3')
    except Exception as e:
        print(f"Error during conversion: {str(e)}")


def does_audio_exist(file_path):
    return os.path.isfile(file_path)


def colorize_text(text, color):
    return f'{color}{text}{RESET}'


def download_audio(youtube_url, output_path='music'):
    try:
        yt = YouTube(youtube_url)
        audio_file_path = os.path.join(output_path, f"{yt.title}.mp4")

        if not does_audio_exist(audio_file_path):
            audio_stream = yt.streams.filter(only_audio=True).first()
            audio_stream.download(output_path)
            video_file_path = os.path.join(output_path, f"{yt.title}.{audio_stream.subtype}")
            convert_mp4_to_mp3(video_file_path, audio_file_path)
            print(colorize_text(f"Audio '{yt.title}' downloaded and converted successfully to {audio_file_path}.\n", GREEN))
        else:
            print(colorize_text(f"Audio '{yt.title}' already exists at {audio_file_path}. Skipping.\n", YELLOW))

    except Exception as e:
        print(colorize_text(f"Error: {str(e)}", RED))


def download_playlist(playlist_url):
    main_url = f'https://www.youtube.com/playlist?list={playlist_url}'
    playlist = Playlist(main_url)

    for video_url in playlist.video_urls:
        download_audio(video_url, playlist.title)


download_playlist(playlist_url)
