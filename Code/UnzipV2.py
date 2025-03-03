import os
import sys
import shutil
from concurrent.futures import ThreadPoolExecutor
from time import sleep
from termcolor import colored

BASE_DIRECTORY = r"X:\HD\HD-Log-kunder"
MAX_CHILD_FOLDERS = 5
unzipped_count = 0
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

        is_within_base = is_subdirectory(start_directory, BASE_DIRECTORY)
        if is_within_base:
            process_directory_recursive(start_directory)
        else:
            process_directory_flat(start_directory)

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

    directories_input = input("Specify directories (separated by '/') or type 'exit': ")
    if directories_input.lower() == 'exit':
        if unzipped_count > 0:
            print_summary()
        sys.exit()

    directories = [d.strip() for d in directories_input.split("/")]

    for directory in directories:
        if not os.path.isdir(directory):
            print_error(f"The specified directory '{directory}' does not exist.")
            continue

        is_within_base = is_subdirectory(directory, BASE_DIRECTORY)
        if is_within_base:
            process_directory_recursive(directory)
        else:
            process_directory_flat(directory)

    if unzipped_count > 0:
        print_summary()

def process_directory_flat(directory):
    process_zips_in_directory(directory)

def process_directory_recursive(directory):
    process_zips_in_directory(directory)

    subfolders = [
        os.path.join(directory, d)
        for d in os.listdir(directory)
        if os.path.isdir(os.path.join(directory, d)) and d.lower() != "unzipped"
    ][:MAX_CHILD_FOLDERS]

    for subfolder in subfolders:
        process_directory_recursive(subfolder)

def process_zips_in_directory(directory):
    global unzipped_count

    zip_files = [
        filename for filename in os.listdir(directory)
        if filename.endswith(".zip")
    ]

    with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as executor:
        results = executor.map(lambda f: process_zip(directory, f), zip_files)

    unzipped_count += sum(results)

def process_zip(directory, filename):
    zip_path = os.path.join(directory, filename)
    unzipped_folder = os.path.join(directory, "Unzipped")

    if not os.path.exists(unzipped_folder):
        os.makedirs(unzipped_folder)

    already_unzipped_path = os.path.join(unzipped_folder, filename)
    if os.path.exists(already_unzipped_path):
        # Skip if the file has already been processed
        return 0

    try:
        extract_dir = os.path.join(directory, filename[:-4])

        if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir)  # Clean up leftover dir if rerun

        shutil.unpack_archive(zip_path, extract_dir)

        os.rename(zip_path, already_unzipped_path)
        return 1  # 1 zip processed successfully

    except Exception as e:
        print(colored(f"Failed to process '{filename}': {e}", "red"))
        return 0

def print_error(message):
    print(colored("Error: ", 'light_red') + message, flush=True)
    sleep(2)

def print_summary():
    global unzipped_count
    print("\n" + "-" * 40)
    print(f"Finished processing. Total zip files unzipped: {unzipped_count}")
    print("-" * 40 + "\n")

if __name__ == "__main__":
    main()
