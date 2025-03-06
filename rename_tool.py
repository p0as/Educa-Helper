import os
import shutil
import re

def rename_images(source_dir, destination_dir):
    """
    Renames and copies image files from the source directory to the destination directory based on a shorthand
    naming convention.

    :param source_dir: Directory containing shorthand-named image files (e.g., 'sample').
    :param destination_dir: Directory where renamed files will be copied (e.g., 'images/processed').
    """
    # Create the destination directory if it doesn't exist
    os.makedirs(destination_dir, exist_ok=True)
    
    # Define regex pattern to match shorthand names: [fs][qa][number].png
    # e.g., 'fa1.png' -> section 'f' (first), type 'a' (answer), number '1'
    pattern = re.compile(r"([fs])([qa])(\d+)\.png")
    
    # Iterate over all files in the source directory
    for filename in os.listdir(source_dir):
        # Convert filename to lowercase for consistent matching
        filename_lower = filename.lower()
        match = pattern.match(filename_lower)
        if match:
            section, type_, number = match.groups()
            
            # Remove leading zeros from the number by converting to int and back to str
            number = str(int(number))
            
            # Determine the target filename based on section and type
            if section == "f":  # First section
                if type_ == "q":
                    target_name = f"question{number}.png"
                elif type_ == "a":
                    target_name = f"answersheet{number}.png"
            elif section == "s":  # Second section
                if type_ == "q":
                    target_name = f"sectionB_question{number}.png"
                elif type_ == "a":
                    target_name = f"sectionB_answersheet{number}.png"
            
            # Construct full source and destination paths
            src_path = os.path.join(source_dir, filename)
            dst_path = os.path.join(destination_dir, target_name)
            
            try:
                # Copy the file to the destination directory with the new name
                shutil.copy(src_path, dst_path)
                print(f"Copied {filename} to {dst_path}")
            except Exception as e:
                print(f"Error copying {filename}: {e}")
        else:
            print(f"Error parsing {filename}: does not match expected pattern")

# Define directories
source_directory = "sample"  # Source directory with shorthand-named images
destination_directory = "images/geometry1"  # Change this to your desired destination directory

# Run the renaming function
rename_images(source_directory, destination_directory)