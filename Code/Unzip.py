import zipfile
import os
from time import sleep
from termcolor import colored

BASE_DIRECTORY = r"X:\HD\HD-Log-kunder"
MAX_CHILD_FOLDERS = 5
unzipped_count = 0  # Track the number of unzipped files
current_directory = ""  # Track the current directory
current_file = ""  # Track the current file being processed
status_initialized = False  # Track if the status lines have been initialized

def dir():
    os.system("cls")
    directories_input = input("Specify the directories containing zip files (if multiple, separated by '/')\nTo exit type 'exit'\n\nDirectories: ")
    if directories_input.lower() == 'exit':
        exit()
    directories = directories_input.split("/")

    for directory in directories:
        directory = directory.strip()
        if not os.path.isdir(directory):
            print_error(f"The specified directory '{directory}' does not exist.")
            dir()
        elif os.path.abspath(directory) == os.path.abspath(BASE_DIRECTORY):
            print_error(f"Cannot process the base directory '{directory}' directly. Please specify a subdirectory.")
            dir()
        elif os.path.commonpath([directory, BASE_DIRECTORY]) == BASE_DIRECTORY:
            process_directory(directory)
        else:
            process_directory(directory)

def print_error(message):
    print(colored("Error: ", 'light_red') + message, flush=True)
    sleep(2)

def initialize_status():
    """Initialize the status lines for dynamic updates."""
    global status_initialized
    if not status_initialized:
        print("\n" * 3, end="")  # Reserve space for the status updates
        status_initialized = True

def clear_lines(count):
    """Clear a specific number of lines above the current cursor position."""
    print("\033[F" * count + "\033[K" * count, end="")

def update_status():
    """Update the status output dynamically over three lines."""
    initialize_status()
    clear_lines(3)  # Move up three lines and clear them
    print(f"Unzipped files: {unzipped_count}")
    print(f"Processing dir: {current_directory}")
    print(f"File: {current_file}")

def process_directory(directory):
    global current_directory, unzipped_count
    current_directory = directory
    update_status()

    try:
        # Process zip files in the current directory
        for filename in os.listdir(directory):
            if filename.endswith(".zip"):
                global current_file
                current_file = filename
                unzipped_count += process_zip(directory, filename)
                update_status()

        # Get subdirectories and limit to MAX_CHILD_FOLDERS
        subfolders = [
            os.path.join(directory, d)
            for d in os.listdir(directory)
            if os.path.isdir(os.path.join(directory, d)) and d.lower() != "unzipped"
        ][:MAX_CHILD_FOLDERS]

        # Process subdirectories recursively
        for subfolder in subfolders:
            process_directory(subfolder)

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

            if len(items) == 1:  # Single-item zip
                zip_ref.extract(items[0], directory)
            else:  # Multi-item zip
                extract_dir = os.path.join(directory, filename[:-4])
                zip_ref.extractall(extract_dir)

        # Move the zip file to the "Unzipped" folder
        new_zip_path = os.path.join(unzipped_folder, filename)
        os.rename(zip_path, new_zip_path)
        
        # Return the count of unzipped files
        return len(items)

    except zipfile.BadZipFile:
        print(colored(f"\nError: Bad zip file - {filename}", 'red'))
        return 0
    except Exception as e:
        print(colored(f"\nError processing zip file: {filename}", 'red'))
        print(colored(str(e), 'red'))
        return 0

if __name__ == "__main__":
    while True:  # Keep looping back to the directory input
        dir()