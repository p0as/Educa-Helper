import os
import shutil
import re

def rename_images(source_dir, destination_dir):
    os.makedirs(destination_dir, exist_ok=True)
    
    # regex
    pattern = re.compile(r"([fst])([qa])(\d+)\.png")
    
    for filename in os.listdir(source_dir):
        filename_lower = filename.lower()
        match = pattern.match(filename_lower)
        if match:
            section, type_, number = match.groups()
            
            number = str(int(number))
            
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
            elif section == "t":  # Third section
                if type_ == "q":
                    target_name = f"sectionC_question{number}.png"
                elif type_ == "a":
                    target_name = f"sectionC_answersheet{number}.png"
            
            src_path = os.path.join(source_dir, filename)
            dst_path = os.path.join(destination_dir, target_name)
            
            try:
                shutil.copy(src_path, dst_path)
                print(f"Copied {filename} to {dst_path}")
            except Exception as e:
                print(f"Error copying {filename}: {e}")
        else:
            print(f"Error parsing {filename}: does not match expected pattern")

source_directory = "sample"  
destination_directory = "images/arithmetic1"  

rename_images(source_directory, destination_directory)