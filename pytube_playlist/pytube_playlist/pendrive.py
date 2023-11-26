import subprocess

from pytube import Playlist


def get_playlist_info(playlist):
    try:
        playlist_info = {
            'name': playlist.title,
            'video_count': playlist.length,
            'creator': playlist.owner_url,
            'views': playlist.views,
            'url': playlist.playlist_url
        }
    except Exception as e:
        print(f"Error fetching information for playlist {playlist.playlist_url}: {str(e)}")
    return playlist_info


def confirm_choice():
    while True:
        choice = input("\nDo you want to continue? (y/n): \n").lower()
        if choice == 'y':
            return True
        elif choice == 'n':
            return False
        else:
            print("Invalid choice. Please enter 'y' or 'n'.")


def detect_pendrives():
    pendrives_info = []

    # Command to list storage devices
    command = "lsblk -o KNAME,MOUNTPOINT,FSTYPE,SIZE,MODEL -l -n -p -I 8,9,11,65,66,67,68,69,70,71,128"

    try:
        output = subprocess.check_output(command, shell=True)
        output = output.decode('utf-8').strip().split('\n')

        for line in output:
            parts = line.split()
            if len(parts) >= 4 and parts[1].startswith('/media/'):
                device = parts[0]
                mountpoint = parts[1]
                fstype = parts[2]
                size = parts[3]
                model = parts[4] if len(parts) == 5 else None
                pendrives_info.append((device, mountpoint, fstype, size, model))

    except subprocess.CalledProcessError as e:
        print(f"Error detecting pendrives: {e}")

    return pendrives_info


def get_disk_usage(mountpoint):
    # Command to get disk usage information
    command = f"df -h --output=used,size,avail {mountpoint} | tail -n 1"
    
    try:
        output = subprocess.check_output(command, shell=True)
        output = output.decode('utf-8').strip().split()
        used, size, avail = output

        return used, size, avail

    except subprocess.CalledProcessError as e:
        print(f"Error getting disk usage: {e}")
        return None


def get_directory_info(directory):
    # Command to get information about the directory
    command = f"du -sh {directory}"
    file_count_command = f"find {directory} -type f | wc -l"

    try:
        # Getting directory size
        size_output = subprocess.check_output(command, shell=True)
        size_output = size_output.decode('utf-8').strip().split()
        size = size_output[0]

        # Getting file count
        file_count_output = subprocess.check_output(file_count_command, shell=True)
        file_count = int(file_count_output.decode('utf-8').strip())

        return size, file_count

    except subprocess.CalledProcessError as e:
        print(f"Error getting directory info: {e}")
        return None, None


def select_pendrive(pendrives_info):


    def detect_pendrive():
        if not pendrives_info:
            print("No pendrives detected.")
            return None

        print("\nDetected Pendrives:\n")

        for i, (device, mountpoint, fstype, size, model) in enumerate(pendrives_info, start=1):
            print(f"{i}. {model} - {device} - {mountpoint} ({fstype}) - Total Size: {size}")


    def info_pendrive():

        print(f"\nSelected Pendrive: \nModel: {pendrives_info[index][4]} \nDevice: {pendrives_info[index][0]} \nMount Point: {pendrives_info[index][1]} \nFile System Type: {pendrives_info[index][2]} \nTotal Size: {pendrives_info[index][3]}")

    detect_pendrive()

    while True:

        choice = input("\nChoose the number of the desired pendrive (or 'q' to quit): ").lower()

        if choice == 'q':
            return None

        try:
            index = int(choice) - 1
            if 0 <= index < len(pendrives_info):
                info_pendrive()
                
                if confirm_choice():
                    return pendrives_info[index]
                else:
                    print("Select another pendrive.")
                    detect_pendrive()
            else:
                print("Invalid index.")
                detect_pendrive()
        except ValueError:
            print("Invalid input. Use numbers or 'q' to quit.")
            detect_pendrive()


def select_playlist_option():
    playlists = [
        'PLgOTmTz9Gp0hAdnZ4B1QmQfhRgTq_62jF',
        'PLgOTmTz9Gp0j-sDID4H5MXVSb8-rDNXWq',
        'PLVgpqzJL0lBZejBh7KJ2tKyliU8-DCM_o'
    ]

    while True:
        print("\nChoose an option:")
        print("1. Last playlist links used")
        print("2. Enter new playlist")
        print("3. Quit")

        choice = input("Enter the number of your choice:").lower()

        if choice == '1':
            playlist_info = {}

            for index, playlist_url in enumerate(playlists, start=1):
                main_url = f'https://www.youtube.com/playlist?list={playlist_url}'
                playlist = Playlist(main_url)

                info = get_playlist_info(playlist)
                playlist_info[index] = info

                print(f'{index}. {playlist.title} - Total Musics {playlist.length} - Views {playlist.views} - URL {main_url}.\n')

            playlist_choice = int(input("Enter the number of your playlist choice: "))
            try:
                if 1 <= playlist_choice <= len(playlists):
                    return playlist_info[playlist_choice]
                else:
                    print("Invalid playlist choice.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        elif choice == '2':
            return input("Enter the direct link to the video: ")
        elif choice == '3':
            return None
        else:
            print("Invalid choice. Please enter a number (1, 2, or 3).")


def init_app():
    detected_pendrives_info = detect_pendrives()
    selected_pendrive_info = select_pendrive(detected_pendrives_info)

    if selected_pendrive_info:
        while True:
            playlist_option = select_playlist_option()

            if playlist_option is None:
                print("Quitting.")
                break
            print(f"\nSelected Option: {playlist_option}")
            if confirm_choice():
                return playlist_option['url']
            else:
                print("Select another option.")
    else:
        print("No pendrive selected.")
