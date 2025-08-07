import zipfile
import os
import sys
import time
from time import sleep
from termcolor import colored

BASE_DIRECTORY = r"X:\HD\HD-Log-kunder"
MAX_CHILD_FOLDERS = 5
unzipped_count = 0
current_directory = ""
current_file = ""
status_initialized = False

def main():
    if len(sys.argv) > 1:
        directory_arg = sys.argv[1]
        if directory_arg == ".":
            start_directory = os.getcwd()
        else:
            start_directory = directory_arg

        if not os.path.isdir(start_directory):
            print_error(f"The specified directory '{start_directory}' does not exist.")
            return

        start_time = time.time()
        is_within_base = is_subdirectory(start_directory, BASE_DIRECTORY)

        if is_within_base:
            process_directory_recursive(start_directory)
        else:
            process_directory_flat(start_directory)

        end_time = time.time()
        print_summary(end_time - start_time)
    else:
        interactive_mode()

def is_subdirectory(directory, base_directory):
    drive_directory, _ = os.path.splitdrive(directory)
    drive_base, _ = os.path.splitdrive(base_directory)

    if drive_directory.lower() != drive_base.lower():
        return False

    return os.path.commonpath([os.path.abspath(directory), os.path.abspath(base_directory)]) == os.path.abspath(base_directory)

def interactive_mode():
    os.system("cls")
    if unzipped_count > 0:
        print_summary()

    directories_input = input("Specify the directories containing zip files (if multiple, separated by '/')\nTo exit type 'exit'\n\nDirectories: ")
    if directories_input.lower() == 'exit':
        print_summary()
        exit()

    directories = directories_input.split("/")

    start_time = time.time()
    for directory in directories:
        directory = directory.strip()
        if not os.path.isdir(directory):
            print_error(f"The specified directory '{directory}' does not exist.")
            interactive_mode()
        is_within_base = is_subdirectory(directory, BASE_DIRECTORY)

        if is_within_base:
            process_directory_recursive(directory)
        else:
            process_directory_flat(directory)

    end_time = time.time()
    print_summary(end_time - start_time)

def print_error(message):
    print(colored("Error: ", 'light_red') + message, flush=True)
    sleep(2)

def initialize_status():
    global status_initialized
    if not status_initialized:
        print("\n" * 3, end="")
        status_initialized = True

def clear_lines(count):
    print("\033[F" * count + "\033[K" * count, end="")

def update_status():
    initialize_status()
    clear_lines(3)
    print(f"Unzipped files: {unzipped_count}")
    print(f"Processing dir: {current_directory}")
    print(f"File: {current_file}")

def process_directory_flat(directory):
    global current_directory, unzipped_count
    current_directory = directory
    update_status()

    try:
        for filename in os.listdir(directory):
            if filename.endswith(".zip"):
                global current_file
                current_file = filename
                unzipped_count += process_zip(directory, filename)
                update_status()
    except Exception as e:
        print(colored("\nError processing directory: ", 'red') + directory)
        print(colored(str(e), 'red'))

def process_directory_recursive(directory):
    global current_directory, unzipped_count
    current_directory = directory
    update_status()

    try:
        for filename in os.listdir(directory):
            if filename.endswith(".zip"):
                global current_file
                current_file = filename
                unzipped_count += process_zip(directory, filename)
                update_status()

        subfolders = [
            os.path.join(directory, d)
            for d in os.listdir(directory)
            if os.path.isdir(os.path.join(directory, d)) and d.lower() != "unzipped"
        ][:MAX_CHILD_FOLDERS]

        for subfolder in subfolders:
            process_directory_recursive(subfolder)

    except Exception as e:
        print(colored("\nError processing directory: ", 'red') + directory)
        print(colored(str(e), 'red'))

def process_zip(directory, filename):
    try:
        zip_path = os.path.join(directory, filename)
        unzipped_folder = os.path.join(directory, "Unzipped")
        if not os.path.exists(unzipped_folder):
            os.makedirs(unzipped_folder)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            items = zip_ref.namelist()

            if len(items) == 1:
                zip_ref.extract(items[0], directory)
            else:
                extract_dir = os.path.join(directory, filename[:-4])
                zip_ref.extractall(extract_dir)

        new_zip_path = os.path.join(unzipped_folder, filename)
        os.rename(zip_path, new_zip_path)
        
        return len(items)

    except zipfile.BadZipFile:
        print(colored(f"\nError: Bad zip file - {filename}", 'red'))
        return 0
    except Exception as e:
        print(colored(f"\nError processing zip file: {filename}", 'red'))
        print(colored(str(e), 'red'))
        return 0

def print_summary(duration_seconds=0):
    global unzipped_count
    print("\n" + "-" * 40)
    print(f"Finished processing. Total zip files unzipped: {unzipped_count}")
    if duration_seconds:
        print(f"Total time: {duration_seconds:.2f} seconds")
    print("-" * 40 + "\n")

if __name__ == "__main__":
    main()