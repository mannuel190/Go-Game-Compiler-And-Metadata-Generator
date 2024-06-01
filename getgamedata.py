import os
import json
import shutil
from subprocess import PIPE, run
import sys

# Constants for the script
GAME_DIR_PATTERN = "game"
GAME_CODE_EXTEN = ".go"
GAME_COMPILE_COMMAND = ["go", "build"]

# Function to find all directories that match the specified pattern
def find_all_game_paths(source):
    game_paths = []
    
    for root, dirs, files in os.walk(source):
        for directory in dirs:
            if GAME_DIR_PATTERN in directory.lower():
                path = os.path.join(source, directory)
                game_paths.append(path)      
        
        break
    
    return game_paths

# Function to extract new directory names by stripping a specific substring
def get_name_from_paths(paths, to_strip):
    new_names = []
    for path in paths:
            _, dir_name = os.path.split(path)
            new_dir_name =  dir_name.replace(to_strip, "")
            new_names.append(new_dir_name)
            
    return new_names

# Function to create a directory if it doesn't exist
def create_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)

# Function to copy and overwrite a directory
def copy_and_overwrite(source, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(source, dest)

# Function to create a JSON metadata file
def make_json_metadata_file(path, game_dirs):
    data = {
        "gameNames": game_dirs,
        "numberOfGames": len(game_dirs)
    }
    with open(path, "w") as f:
        json.dump(data, f)

# Function to compile game code in a specified directory
def compile_game_code(path):
    code_file_name = None
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(GAME_CODE_EXTEN):
                code_file_name = file    
                break
            
        break

    if code_file_name is None:
        return

    command = GAME_COMPILE_COMMAND + [code_file_name]
    run_command(command, path)

# Function to run a command in a specified directory
def run_command(command, path):
    cwd = os.getcwd()
    os.chdir(path)
    
    result = run(command, stdout=PIPE, stdin=PIPE, universal_newlines=True)
    print("compile result", result)

    os.chdir(cwd)

# Main function that orchestrates the entire process
def main(source, target):
    cwd = os.getcwd()
    source_path = os.path.join(cwd, source)
    target_path = os.path.join(cwd, target)
    
    # Find game directories in the source path
    game_paths = find_all_game_paths(source_path)
    
    # Extract new game directory names
    new_game_dirs = get_name_from_paths(game_paths, "_game")
    
    # Create the target directory
    create_dir(target_path)
    
    # Copy, overwrite, and compile game code for each game directory
    for src, dest in zip(game_paths, new_game_dirs):
        dest_path = os.path.join(target_path, dest)
        copy_and_overwrite(src, dest_path)
        compile_game_code(dest_path)
        
    # Create a JSON metadata file in the target directory
    json_path = os.path.join(target_path, "metadata.json")
    make_json_metadata_file(json_path, new_game_dirs)

# Check if the script is run as the main program
if __name__ == "__main__":
    # Get command-line arguments
    args = sys.argv
    # Ensure that source and target directories are provided as arguments
    if len(args) != 3:
        raise Exception("You must pass a source and target directory only.")
    
    source, target = args[1:]
    # Call the main function with source and target directories
    main(source, target)
