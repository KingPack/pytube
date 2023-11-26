import os

from pytube import Playlist, YouTube
from colorama import Fore, Style, init
from moviepy.editor import AudioFileClip
from pytube.exceptions import AgeRestrictedError
from pendrive import init_app, get_playlist_info


RED = Fore.RED
GREEN = Fore.GREEN
YELLOW = Fore.YELLOW
RESET = Style.RESET_ALL

init()


def colorize_text(text, color):
    return f'{color}{text}{RESET}'


def count_restricted_and_unrestricted(playlist):
    result = {
        'restricted': {},
        'unrestricted': {}
    }

    try:
        for video_url in playlist.video_urls:
            try:
                yt = YouTube(video_url, use_oauth=True, allow_oauth_cache=True)

                if yt.age_restricted:
                    yt.bypass_age_gate()
                    result['restricted'][yt.title] = video_url
                    print(colorize_text(f"Restricted: {yt.title}\n", RED))
                else:
                    result['unrestricted'][yt.title] = video_url
                    print(colorize_text(f"Unrestricted: {yt.title}\n", GREEN))

            except AgeRestrictedError:
                result['restricted'][f"AgeRestrictedError: {video_url}"] = video_url
                print(colorize_text(f"Restricted (AgeRestrictedError): {yt.title} | {video_url}\n", RED))
            except Exception as e:
                result['restricted'][f"Error: {str(e)}"] = video_url
                print(colorize_text(f"Error: {str(e)}", RED))

    except Exception as e:
        result['restricted'][f"Error: {str(e)}"] = 'Playlist Error'
        print(colorize_text(f"Error: {str(e)}", RED))

    print(colorize_text(f"Total Restricted videos: {len(result['restricted'])}\n", RED))
    print(colorize_text(f"Total Unrestricted videos: {len(result['unrestricted'])}\n", GREEN))

    return result


def filter_long_videos(playlist_url, max_duration=30):
    long_videos = {
        'count': 0,
        'links': []
    }

    try:
        playlist = Playlist(playlist_url)
        for video_url in playlist.video_urls:
            try:
                yt = YouTube(video_url, use_oauth=True, allow_oauth_cache=True)

                if yt.age_restricted:
                    yt.bypass_age_gate()
 
                duration_minutes = yt.length / 60

                if duration_minutes > max_duration:
                    long_videos['count'] += 1
                    long_videos['links'].append(video_url)
                    print(colorize_text(f"Discarding long video: {yt.title} ({duration_minutes} minutes)\n", RED))

            except AgeRestrictedError:
                # Age-restricted videos are already handled
                pass
            except Exception as e:
                print(colorize_text(f"Error: {str(e)}", RED))

    except Exception as e:
        print(colorize_text(f"Error: {str(e)}", RED))

    print(colorize_text(f"Total long videos discarded: {long_videos['count']}\n", RED))

    return long_videos


def download_video(video_url, output_path='music', max_duration=18):
    try:
        yt = YouTube(video_url, use_oauth=True, allow_oauth_cache=True)

        if yt.age_restricted:
            yt.bypass_age_gate()

        duration_seconds = yt.length
        duration_minutes = duration_seconds / 60

        if duration_minutes > max_duration:
            print(colorize_text(f"Discarding long video: {yt.title} ({duration_minutes} minutes)\n", RED))
            return

        audio_file_path = os.path.join(output_path, f"{yt.title}.mp4")

        if not os.path.exists(audio_file_path):
            audio_stream = yt.streams.filter(only_audio=True).first()
            audio_stream.download(output_path)
            print(colorize_text(f"Audio '{yt.title}' downloaded successfully to {audio_file_path}.\n", GREEN))
        else:
            print(colorize_text(f"Audio '{yt.title}' already exists at {audio_file_path}. Skipping.\n", YELLOW))

    except AgeRestrictedError as age_error:
        print(colorize_text(f"Error: {age_error}\n", RED))

    except Exception as e:
        print(colorize_text(f"Error: {str(e)}\n", RED))


def convert_folder_mp4_to_mp3(path_folder):
    try:
        folder_mp3 = os.path.join(path_folder, 'mp3')
        folder_mp4 = os.path.join(path_folder, 'mp4')

        os.makedirs(folder_mp3, exist_ok=True)

        converted_files = set()

        # Check for already converted files in mp3 folder
        for file_name in os.listdir(folder_mp3):
            if file_name.lower().endswith('.mp3'):
                converted_files.add(os.path.splitext(file_name)[0] + '.mp4')

        for file_name in os.listdir(folder_mp4):
            if file_name.lower().endswith('.mp4'):
                input_path = os.path.join(folder_mp4, file_name)
                output_path = os.path.join(folder_mp3, os.path.splitext(file_name)[0] + '.mp3')

                if file_name in converted_files:
                    print(colorize_text(f"Audio '{os.path.splitext(file_name)[0]}' already converted. Skipping conversion.\n", YELLOW))
                    continue

                try:
                    audio_clip = AudioFileClip(input_path)
                    audio_clip.write_audiofile(output_path, codec='mp3')
                    converted_files.add(file_name)
                    print(colorize_text(f"Conversion successful: {input_path} -> {output_path}\n", GREEN))
                except Exception as e:
                    print(colorize_text(f"Error during conversion: {str(e)}\n", RED))

    except Exception as e:
        print(colorize_text(f"Error: {str(e)}\n", RED))


def download_playlist(playlist_url):
    playlist = Playlist(playlist_url)

    count_restricted_and_unrestricted(playlist)
    get_playlist_info(playlist)

    for video_url in playlist.video_urls:
        download_video(video_url, output_path=f'playlist/{playlist.title}/mp4')
    convert_folder_mp4_to_mp3(f'playlist/{playlist.title}')


if __name__ == "__main__":
    url_playlist = init_app()
    download_playlist(url_playlist)
