import os
import shutil
import sys

# to use, make sure to call
# python move_folder.py path_to_source_folder path_to_destination_folder


def move_folder(source_dir, dest_dir):
    # Check if source directory exists
    if not os.path.exists(source_dir):
        print(f"Source directory {source_dir} does not exist.")
        return

    # Ensure the destination directory exists
    os.makedirs(dest_dir, exist_ok=True)

    # Define the destination path
    base_name = os.path.basename(source_dir.rstrip(os.sep))
    destination = os.path.join(dest_dir, base_name)

    # Move the directory
    try:
        shutil.move(source_dir, destination)
        print(f"Successfully moved {source_dir} to {destination}.")
    except Exception as e:
        print(f"An error occurred while moving the directory: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python move_folder.py <source_dir> <dest_dir>")
        sys.exit(1)

    source_dir = sys.argv[1]
    dest_dir = sys.argv[2]

    move_folder(source_dir, dest_dir)
