import os
import sys
import time
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
        start_directory = os.getcwd() if directory_arg == "." else directory_arg

        if not os.path.isdir(start_directory):
            print_error(f"The specified directory '{start_directory}' does not exist.")
            return

        # Prevent processing too high-level folders
        if os.path.abspath(start_directory).lower() in [
            os.path.abspath(BASE_DIRECTORY).lower(),
            os.path.abspath(r"X:\HD").lower(),
            os.path.abspath(r"X:\\").lower()
        ]:
            print_error(f"Refusing to process '{start_directory}' recursively — too high-level.")
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
    directories_input = input("Specify directories (separated by '/') or type 'exit': ")
    if directories_input.lower() == 'exit':
        if unzipped_count > 0:
            print_summary()
        sys.exit()

    directories = [d.strip() for d in directories_input.split("/")]

    start_time = time.time()

    for directory in directories:
        if not os.path.isdir(directory):
            print_error(f"The specified directory '{directory}' does not exist.")
            continue

        # Prevent processing too high-level folders
        if os.path.abspath(directory).lower() in [
            os.path.abspath(BASE_DIRECTORY).lower(),
            os.path.abspath(r"X:\HD").lower(),
            os.path.abspath(r"X:\\").lower()
        ]:
            print_error(f"Refusing to process '{directory}' recursively — too high-level.")
            continue

        is_within_base = is_subdirectory(directory, BASE_DIRECTORY)
        if is_within_base:
            process_directory_recursive(directory)
        else:
            process_directory_flat(directory)

    end_time = time.time()
    if unzipped_count > 0:
        print_summary(end_time - start_time)

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

    unzipped_folder = os.path.join(directory, "Unzipped")
    os.makedirs(unzipped_folder, exist_ok=True)

    with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as executor:
        results = executor.map(lambda f: process_zip(directory, f), zip_files)

    unzipped_count += sum(results)

def process_zip(directory, filename):
    import zipfile

    zip_path = os.path.join(directory, filename)
    unzipped_folder = os.path.join(directory, "Unzipped")

    already_unzipped_path = os.path.join(unzipped_folder, filename)
    if os.path.exists(already_unzipped_path):
        return 0

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            items = zip_ref.namelist()
            if not items:
                print(colored(f"Warning: Zip file '{filename}' is empty.", "yellow"))
                return 0

            if len(items) == 1:
                extract_target = directory
            else:
                extract_target = os.path.join(directory, filename[:-4])
                if os.path.exists(extract_target):
                    shutil.rmtree(extract_target)
                os.makedirs(extract_target, exist_ok=True)

            zip_ref.extractall(extract_target)

        os.rename(zip_path, already_unzipped_path)
        return 1

    except zipfile.BadZipFile:
        print(colored(f"Bad ZIP file: '{filename}'", "red"))
        return 0
    except Exception as e:
        print(colored(f"Failed to process '{filename}': {e}", "red"))
        return 0

def print_error(message):
    print(colored("Error: ", 'light_red') + message, flush=True)
    sleep(2)

def print_summary(duration_seconds=0):
    global unzipped_count
    print("\n" + "-" * 40)
    print(f"Finished processing. Total zip files unzipped: {unzipped_count}")
    if duration_seconds:
        print(f"Total time: {duration_seconds:.2f} seconds")
    print("-" * 40 + "\n")

if __name__ == "__main__":
    main()