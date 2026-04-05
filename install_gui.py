import os
import shutil
import sys
import tkinter as tk
from tkinter import messagebox, font, scrolledtext

def get_files_to_install():
    """Gets a list of (source_path, destination_path) tuples for all files."""
    files_to_install = []
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        appdata_dir = os.getenv('APPDATA')
        if not appdata_dir:
            raise EnvironmentError("Could not find APPDATA environment variable.")

        # 1. Python Plugin Directory
        py_source_dir_rel = os.path.join('pykrita', 'recent_color')
        py_source_dir_abs = os.path.join(script_dir, py_source_dir_rel)
        py_dest_dir = os.path.join(appdata_dir, 'krita', 'pykrita', 'recent_color') # Destination is the directory itself
        if os.path.isdir(py_source_dir_abs): # Check if source directory exists
             # Mark this as a directory copy operation
             files_to_install.append(('dir', py_source_dir_abs, py_dest_dir))
        else:
             print(f"Warning: Python source directory not found: {py_source_dir_abs}")


        # 2. Plugin desktop file
        desktop_source_abs = os.path.join(script_dir, 'pykrita', 'recent_color.desktop')
        desktop_dest_abs = os.path.join(appdata_dir, 'krita', 'pykrita', 'recent_color.desktop')
        if os.path.isfile(desktop_source_abs):
            files_to_install.append(('file', desktop_source_abs, desktop_dest_abs))
        else:
            print(f"Warning: Plugin desktop file not found: {desktop_source_abs}")

        # 3. Action Files
        actions_source_dir = os.path.join(script_dir, 'actions')
        actions_dest_dir = os.path.join(appdata_dir, 'krita', 'actions')

        if os.path.isdir(actions_source_dir):
            for filename in os.listdir(actions_source_dir):
                if filename.lower().endswith('.action'):
                    action_source_abs = os.path.join(actions_source_dir, filename)
                    action_dest_abs = os.path.join(actions_dest_dir, filename)
                    # Mark this as a file copy operation
                    files_to_install.append(('file', action_source_abs, action_dest_abs))
        else:
             print(f"Warning: Actions source directory not found: {actions_source_dir}")


        if not files_to_install:
             raise FileNotFoundError("No plugin or action files found to install. Ensure script is in project root.")

        return files_to_install

    except Exception as e:
        messagebox.showerror("Error Getting Paths", f"Could not determine file paths:\n{e}")
        sys.exit(1)

def install_plugin():
    """Handles the installation process for all files."""
    try:
        files_to_copy = get_files_to_install()
    except SystemExit:
        return # Error already shown by get_files_to_install

    # Confirmation message box removed as requested.
    # The preview in the text area serves as confirmation.

    dest_dirs = set()
    for op_type, src, dest in files_to_copy:
         if op_type == 'file':
              dest_dirs.add(os.path.dirname(dest)) # Collect unique destination directories for files
         # For 'dir' type, copytree handles directory creation, but we still need the parent dir for actions
         elif op_type == 'dir':
             # Ensure the parent of the destination directory exists if needed (e.g., %APPDATA%/krita/pykrita might not exist)
             parent_dest_dir = os.path.dirname(dest)
             if parent_dest_dir: # Avoid adding empty string if dest is top-level (unlikely here)
                 dest_dirs.add(parent_dest_dir)

    try:
        # Create all destination directories first
        for d_dir in dest_dirs:
             print(f"Ensuring directory exists: {d_dir}")
             os.makedirs(d_dir, exist_ok=True)

        # Copy all files
        copied_files = []
        errors = []
        for op_type, src, dest in files_to_copy:
            try:
                if op_type == 'dir':
                    print(f"Copying directory {src} to {dest}")
                    # Remove existing destination directory first to avoid merge issues or errors if it's not empty
                    if os.path.exists(dest):
                        print(f"Removing existing destination directory: {dest}")
                        shutil.rmtree(dest)
                    shutil.copytree(src, dest) # Using copytree for directories
                    copied_files.append(dest + " (directory)") # Mark as directory
                elif op_type == 'file':
                    print(f"Copying file {src} to {dest}")
                    shutil.copy2(src, dest) # copy2 preserves metadata
                    copied_files.append(dest)
            except Exception as copy_e:
                 item_name = os.path.basename(src)
                 item_type = "directory" if op_type == 'dir' else "file"
                 errors.append(f"Failed to copy {item_type} {item_name}: {copy_e}")

        if errors:
             messagebox.showwarning("Installation Issues", "Some files failed to copy:\n\n" + "\n".join(errors))
        elif copied_files:
             messagebox.showinfo("Success", f"Plugin files installed successfully.\n({len(copied_files)} files copied)\n\nPlease restart Krita.")
             # root.destroy() # Removed as GUI is no longer used
        else:
             messagebox.showinfo("No Files Copied", "No files were copied (perhaps source files are missing?).")


    except Exception as e:
        messagebox.showerror("Installation Failed", f"An error occurred during installation:\n{e}\n\nPlease check permissions or if Krita is running.")

# --- Direct Installation ---
# GUI removed, call install function directly.
if __name__ == "__main__":
    # Hide the dummy Tkinter root window that messagebox creates
    root = tk.Tk()
    root.withdraw()
    install_plugin()
