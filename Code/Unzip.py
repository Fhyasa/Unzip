import zipfile
import os
from time import sleep
from termcolor import colored

BASE_DIRECTORY = r"X:\HD\HD-Log-kunder"
MAX_CHILD_FOLDERS = 5

os.system("cls")

def dir():
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
    os.system("cls")
    print(colored("Error: ", 'light_red') + message, flush=True)
    sleep(2)

def process_directory(directory):
    try:
        print(f"Processing directory: {directory}")

        # Process zip files in the current directory
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            if filename.endswith(".zip"):
                process_zip(directory, filename)

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
        print(colored("Error processing directory: ", 'red') + directory)
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
                extracted_path = os.path.join(directory, items[0])
                zip_ref.extract(items[0], directory)
                print(f"Extracted single item '{items[0]}' from '{filename}' to '{directory}'")
            else:  # Multi-item zip
                extract_dir = os.path.join(directory, filename[:-4])
                zip_ref.extractall(extract_dir)
                print(f"Extracted {len(items)} items from '{filename}' to '{extract_dir}'")

        new_zip_path = os.path.join(unzipped_folder, filename)
        os.rename(zip_path, new_zip_path)
        print(f"Moved '{filename}' to '{unzipped_folder}'")

    except zipfile.BadZipFile:
        print(colored("Error: Bad zip file - ", 'red') + filename)
    except Exception as e:
        print(colored("Error processing zip file: ", 'red') + filename)
        print(colored(str(e), 'red'))

if __name__ == "__main__":
    dir()