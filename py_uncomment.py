import sys
import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox

def remove_comment_lines(file_path):
    # Check if the file exists
    if not os.path.isfile(file_path):
        print(f"Error: The file '{file_path}' does not exist.")
        sys.exit(1)
    
    # Determine the backup filename
    backup_path = generate_backup_filename(file_path)
    
    # Create the backup
    try:
        shutil.copyfile(file_path, backup_path)
        print(f"Backup created: '{backup_path}'")
    except IOError as e:
        print(f"Error creating backup: {e}")
        sys.exit(1)
    
    # Read the original script
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except IOError as e:
        print(f"Error reading the file: {e}")
        sys.exit(1)
    
    # Remove comment lines
    cleaned_lines = []
    comment_lines = 0
    for line in lines:
        stripped_line = line.lstrip()
        if stripped_line.startswith("#") or stripped_line == "\n":
            comment_lines += 1
            continue
        cleaned_lines.append(line)
    
    # Write the cleaned script
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(cleaned_lines)
        print(f"Comment lines removed: {comment_lines}")
        print(f"Cleaned script saved as: '{file_path}'")
    except IOError as e:
        print(f"Error writing the cleaned file: {e}")
        sys.exit(1)

def generate_backup_filename(original_path):
    directory, filename = os.path.split(original_path)
    backup_filename = f"{filename}.backup.py"
    backup_path = os.path.join(directory, backup_filename)
    
    if not os.path.exists(backup_path):
        return backup_path
    
    # If backup exists, add a numerical suffix
    base, ext = os.path.splitext(backup_filename)
    counter = 2
    while True:
        new_backup_filename = f"{base}({counter}){ext}"
        new_backup_path = os.path.join(directory, new_backup_filename)
        if not os.path.exists(new_backup_path):
            return new_backup_path
        counter += 1

def print_usage(script_name):
    print(f"Usage: python {script_name} [scriptname].py")
    sys.exit(1)

def select_file_via_dialog():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    root.update()
    file_path = filedialog.askopenfilename(
        title="Select Python Script",
        filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
    )
    root.destroy()
    if not file_path:
        print("No file selected. Exiting.")
        sys.exit(0)
    return file_path

def main():
    if len(sys.argv) > 2:
        print("Error: Too many arguments provided.")
        print_usage(os.path.basename(sys.argv[0]))
    elif len(sys.argv) == 2:
        target_script = sys.argv[1]
    else:
        target_script = select_file_via_dialog()
    
    remove_comment_lines(target_script)

if __name__ == "__main__":
    main()
