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

        # 1. Python Plugin File
        py_source_rel = os.path.join('pykrita', 'recent_color', 'recent_color.py')
        py_source_abs = os.path.join(script_dir, py_source_rel)
        py_dest_dir = os.path.join(appdata_dir, 'krita', 'pykrita', 'recent_color')
        py_dest_abs = os.path.join(py_dest_dir, 'recent_color.py')
        if os.path.exists(py_source_abs): # Only add if source exists
             files_to_install.append((py_source_abs, py_dest_abs))
        else:
             print(f"Warning: Python source file not found: {py_source_abs}")


        # 2. Action Files
        actions_source_dir = os.path.join(script_dir, 'actions')
        actions_dest_dir = os.path.join(appdata_dir, 'krita', 'actions')

        if os.path.isdir(actions_source_dir):
            for filename in os.listdir(actions_source_dir):
                if filename.lower().endswith('.action'):
                    action_source_abs = os.path.join(actions_source_dir, filename)
                    action_dest_abs = os.path.join(actions_dest_dir, filename)
                    files_to_install.append((action_source_abs, action_dest_abs))
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

    # Build confirmation message
    confirmation_message = "This will copy the following files:\n\n"
    dest_dirs = set()
    for src, dest in files_to_copy:
         confirmation_message += f"FROM: {src}\n  TO: {dest}\n\n"
         dest_dirs.add(os.path.dirname(dest)) # Collect unique destination directories
    confirmation_message += "Existing files will be overwritten. Continue?"

    confirm = messagebox.askyesno("Confirm Installation", confirmation_message)

    if not confirm:
        messagebox.showinfo("Cancelled", "Installation cancelled.")
        return

    try:
        # Create all destination directories first
        for d_dir in dest_dirs:
             print(f"Ensuring directory exists: {d_dir}")
             os.makedirs(d_dir, exist_ok=True)

        # Copy all files
        copied_files = []
        errors = []
        for src, dest in files_to_copy:
            try:
                print(f"Copying {src} to {dest}")
                shutil.copy2(src, dest) # copy2 preserves metadata
                copied_files.append(dest)
            except Exception as copy_e:
                errors.append(f"Failed to copy {os.path.basename(src)}: {copy_e}")

        if errors:
             messagebox.showwarning("Installation Issues", "Some files failed to copy:\n\n" + "\n".join(errors))
        elif copied_files:
             messagebox.showinfo("Success", f"Plugin files installed successfully.\n({len(copied_files)} files copied)\n\nPlease restart Krita.")
             root.destroy() # Close the window after successful installation
        else:
             messagebox.showinfo("No Files Copied", "No files were copied (perhaps source files are missing?).")


    except Exception as e:
        messagebox.showerror("Installation Failed", f"An error occurred during installation:\n{e}\n\nPlease check permissions or if Krita is running.")

# --- GUI Setup ---
root = tk.Tk()
root.title("KritaColorPlus Installer")

# Set a slightly larger default font
default_font = font.nametofont("TkDefaultFont")
default_font.configure(size=10)
root.option_add("*Font", default_font)

# Get file list for display
try:
    files_display_list = get_files_to_install()
    display_text = "Files to be installed:\n\n"
    for src, dest in files_display_list:
        display_text += f"FROM: {src}\n  TO: {dest}\n\n"

except SystemExit: # Exit if get_files_to_install failed early
    sys.exit(1)
except FileNotFoundError as e:
     display_text = f"Error: {e}"
     files_display_list = [] # Ensure list is empty if no files found


main_frame = tk.Frame(root, padx=15, pady=15)
main_frame.pack(fill=tk.BOTH, expand=True)

label_info = tk.Label(main_frame, text="This script will install/update the KritaColorPlus plugin and its actions.", justify=tk.LEFT)
label_info.pack(pady=(0, 10), anchor='w')

# Use ScrolledText widget to display the list of files
text_area = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=15, width=80)
text_area.insert(tk.INSERT, display_text)
text_area.config(state='disabled') # Make it read-only
text_area.pack(pady=(0, 15), fill=tk.BOTH, expand=True)


# Only enable button if files were found
install_button = tk.Button(main_frame, text="Install Files", command=install_plugin, width=15, height=2)
if not files_display_list:
     install_button.config(state='disabled')
install_button.pack(pady=(5, 0))

# Center the window
root.update_idletasks()
# Try to make window slightly larger
window_width = max(root.winfo_width(), 600) # Min width 600
window_height = max(root.winfo_height(), 400) # Min height 400
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = int((screen_width / 2) - (window_width / 2))
y = int((screen_height / 2) - (window_height / 2))
root.geometry(f'{window_width}x{window_height}+{x}+{y}')


root.mainloop()