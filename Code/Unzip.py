import zipfile
import os
import platform
from time import sleep

# To build a new .exe file, open cmd or PS1, navigate to the script's dir and use the following command (pip install pyinstller):
# Command: "pyinstaller .\Unzip.spec"

os.system("cls")

def dir():
    directories_input = input("Specify the directories containing zip files (if multiple, separated by '/')\nTo exit type 'exit'\n\nDirectories: ")
    if directories_input == 'exit':
        exit()
    directories = directories_input.split("/")

    for directory in directories:
        directory = directory.strip() 
        if not os.path.isdir(directory):
            os.system("cls")
            print(f"The specified directory '{directory}' does not exist. Please try again.", end='', flush=True)
            for i in range(8):
                print(".", end='', flush=True)
                sleep(0.5)
            os.system("cls")
            dir()

        else:
            zip_files = [filename for filename in os.listdir(directory) if filename.endswith(".zip")]

            if not zip_files:
                print(f"No zip files found in directory '{directory}'. Please try again.", end='', flush=True)
                for i in range(8):
                    print(".", end='', flush=True)
                    sleep(0.5)
                os.system("cls")
                dir()

            else:
                os.system("cls")
                print(f"Processing...")
                MDir(directories)


def MDir(directories):
    for directory in directories:
        for filename in os.listdir(directory):
            if filename.endswith(".zip"):
                zip_path = os.path.join(directory, filename)
                
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    item_count = len(zip_ref.namelist())
                    
                    if item_count > 1:
                        extract_dir = os.path.join(directory, filename[:-4])
                        zip_ref.extractall(extract_dir)
                        print(f"Extracted {item_count} items from '{filename}' to '{extract_dir}'")

                    else:
                        zip_ref.extractall(directory)
                        print(f"Extracted 1 item from '{filename}' to '{directory}'")
    print('\n\n')                
    dir()
dir()