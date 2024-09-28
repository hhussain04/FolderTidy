import os
import shutil
import re
import tkinter as tk
from tkinter import filedialog, ttk, simpledialog

class FolderRenamerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Folder Renamer")

        # Allow the window to be resized
        self.master.geometry("600x500")
        self.master.resizable(True, True)

        self.directory_path = tk.StringVar()
        self.last_folders = []  # List to store last folders
        self.remove_prefix_option = tk.BooleanVar()  # Checkbox to remove number prefix

        # Set the default directory to the current working directory
        self.directory_path.set(os.getcwd())

        self.build_interface()
        self.center_dialog()

    def center_dialog(self):
        ''' Center the dialog on the screen '''
        window_width = 600  # Fixed width
        window_height = 500  # Fixed height
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()

        # Calculate x and y coordinates for the center
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)

        # Update the position of the window
        self.master.geometry(f'{window_width}x{window_height}+{x}+{y}')

        # Bind resizing event to update watermark position
        self.master.bind("<Configure>", self.update_watermark_position)

    def build_interface(self):
        ''' Set up the GUI components '''
        # Create a canvas for the gradient background
        self.canvas = tk.Canvas(self.master, width=600, height=500)
        self.canvas.pack(fill="both", expand=True)

        # Create gradient effect
        self.background_gradient()

        # Frame to hold widgets
        self.frame = tk.Frame(self.master, bg='#2c2f33')
        self.frame.place(relwidth=1, relheight=1)

        # Configure grid layout for responsive resizing
        self.frame.grid_rowconfigure(5, weight=1)  # Make row 5 expandable
        self.frame.grid_columnconfigure(1, weight=1)  # Make column 1 expandable

        # Directory selection
        tk.Label(self.frame, text="Directory:", bg='#2c2f33', fg='white').grid(row=0, column=0, padx=5, pady=5, sticky="w")
        tk.Entry(self.frame, textvariable=self.directory_path, width=50, bg='#23272a', fg='white').grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        tk.Button(self.frame, text="Browse", command=self.select_directory, bg='#7289da', fg='white').grid(row=0, column=2, padx=5, pady=5)

        # Last folder selection
        tk.Label(self.frame, text="Folders to place last:", bg='#2c2f33', fg='white').grid(row=1, column=0, padx=5, pady=5, sticky="w")
        tk.Button(self.frame, text="Select Folders", command=self.select_last_folders, bg='#7289da', fg='white').grid(row=1, column=1, padx=5, pady=5, sticky="w")
        tk.Button(self.frame, text="Remove Folder", command=self.remove_last_folder, bg='#7289da', fg='white').grid(row=1, column=2, padx=5, pady=5, sticky="w")

        # Checkbox to remove prefix
        tk.Checkbutton(self.frame, text="Remove number prefix from existing folders", variable=self.remove_prefix_option, bg='#2c2f33', fg='white', selectcolor='#7289da').grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # Button to start renaming
        tk.Button(self.frame, text="Process Folders", command=self.process_folders, bg='#7289da', fg='white').grid(row=3, column=1, pady=10)

        # Progress display
        self.progress_text = tk.Text(self.frame, height=15, width=70, bg='#23272a', fg='white', insertbackground='white')
        self.progress_text.grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")

        # Scrollbar for progress display
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.progress_text.yview)
        scrollbar.grid(row=4, column=3, sticky="ns")
        self.progress_text.configure(yscrollcommand=scrollbar.set)

        # Watermark
        self.watermark = tk.Label(self.frame, text="Made by Grid!", bg='#2c2f33', fg='Green', font= ('Comic Sans MS', 12, 'bold'))
        self.watermark.place(relx=0.5, rely=0.95, anchor='center')

    def background_gradient(self):
        ''' Create a vertical gradient for the window background '''
        gradient_colors = ["#23272a", "#2c2f33", "#99aab5"]
        height = 500  # Height of the window
        steps = 100   # Number of gradient steps

        # Draw the gradient
        for i in range(steps):
            color = self.interpolate_color(gradient_colors, i / steps)
            self.canvas.create_rectangle(0, i * (height // steps), 600, (i + 1) * (height // steps), fill=color, outline=color)

    def interpolate_color(self, colors, t):
        ''' Interpolate between multiple colors '''
        n = len(colors) - 1
        i = int(t * n)
        f = t * n - i
        c1 = self.hex_to_rgb(colors[i])
        c2 = self.hex_to_rgb(colors[i + 1])
        return self.rgb_to_hex(tuple(int(c1[j] + (c2[j] - c1[j]) * f) for j in range(3)))

    def hex_to_rgb(self, hex):
        ''' Convert hex color to RGB tuple '''
        hex = hex.lstrip('#')
        return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))

    def rgb_to_hex(self, rgb):
        ''' Convert RGB tuple to hex color '''
        return '#{:02x}{:02x}{:02x}'.format(*rgb)

    def update_watermark_position(self, event):
        ''' Handle window resizing and adjust watermark position dynamically '''
        self.watermark.place_configure(relx=0.5, rely=0.95, anchor='center')

    def select_directory(self):
        ''' Open a file dialog for the user to select a directory '''
        directory = filedialog.askdirectory(title="Select Directory")
        if directory:
            self.directory_path.set(directory)

    def select_last_folders(self):
        ''' Open a file dialog for the user to select folders '''
        directory = self.directory_path.get()
        if not directory or not os.path.isdir(directory):
            self.update_progress("Please select a valid directory first.")
            return

        folder = filedialog.askdirectory(title="Select Folder", initialdir=directory)
        if folder:
            folder_name = os.path.basename(folder)
            if folder_name not in self.last_folders:
                self.last_folders.append(folder_name)
                self.update_progress(f"Selected folder: {folder_name}")

    def remove_last_folder(self):
        directory = self.directory_path.get()
        if not directory or not os.path.isdir(directory):
            self.update_progress("Please select a valid directory first.")
            return

        folder = filedialog.askdirectory(title="Select Folder to Remove", initialdir=directory)
        if folder:
            folder_name = os.path.basename(folder)
            try:
                # Remove the actual folder
                shutil.rmtree(folder)
                self.update_progress(f"Removed folder: {folder_name}")
                # Adjust the order of remaining folders
                self.adjust_folder_order(directory)
            except Exception as e:
                self.update_progress(f"Error removing folder {folder_name}: {str(e)}")

    def adjust_folder_order(self, directory):
        folders = [f for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f))]
        
        # Sort folders based on their existing numeric prefixes
        folders.sort(key=lambda x: int(x.split('_')[0]) if x[0:2].isdigit() else float('inf'))

        # Rename folders to ensure continuous numbering
        for index, folder in enumerate(folders, start=1):
            old_path = os.path.join(directory, folder)
            if re.match(r'^\d+_', folder):
                new_name = f"{index:02d}_{folder.split('_', 1)[1]}"
            else:
                new_name = f"{index:02d}_{folder}"
            new_path = os.path.join(directory, new_name)

            if old_path != new_path:
                try:
                    os.rename(old_path, new_path)
                    self.update_progress(f"Renamed: {folder} -> {new_name}")
                except Exception as e:
                    self.update_progress(f"Error renaming {folder}: {str(e)}")

    def process_folders(self):
        ''' Start renaming or removing prefixes based on user input '''
        directory = self.directory_path.get()
        remove_prefix = self.remove_prefix_option.get()  # Get checkbox value

        # Ensure the directory is valid
        if not directory or not os.path.isdir(directory):
            self.update_progress("Please select a valid directory.")
            return

        self.progress_text.delete(1.0, tk.END)

        # Remove prefixes if the option is selected
        if remove_prefix:
            self.update_progress("Removing prefixes from folders with number prefixes...")
            self.remove_number_prefix(directory)
        else:
            self.update_progress("Renaming and reordering folders...")
            self.reorder_folders(directory)

        self.update_progress("Process complete.")

    def remove_number_prefix(self, directory):
        ''' Remove numeric prefixes from existing folders '''
        folders = [f for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f))]

        for folder in folders:
            if re.match(r"^\d{2}_", folder):
                new_name = re.sub(r"^\d{2}_", "", folder)
                old_path = os.path.join(directory, folder)
                new_path = os.path.join(directory, new_name)

                try:
                    os.rename(old_path, new_path)
                    self.update_progress(f"Removed prefix: {folder} -> {new_name}")
                except Exception as e:
                    self.update_progress(f"Error removing prefix from {folder}: {str(e)}")

    def reorder_folders(self, directory):
        ''' Reorder folders and place selected ones last '''
        folders = [f for f in os.listdir(directory) if os.path.isdir(os.path.join(directory, f))]
        
        # Place selected folders last
        regular_folders = [f for f in folders if f not in self.last_folders]
        sorted_folders = regular_folders + self.last_folders

        for index, folder in enumerate(sorted_folders, start=1):
            new_name = f"{index:02d}_{folder}"
            old_path = os.path.join(directory, folder)
            new_path = os.path.join(directory, new_name)

            if old_path != new_path:
                try:
                    os.rename(old_path, new_path)
                    self.update_progress(f"Renamed: {folder} -> {new_name}")
                except Exception as e:
                    self.update_progress(f"Error renaming {folder}: {str(e)}")

    def update_progress(self, message):
        ''' Display progress messages in the Text widget '''
        self.progress_text.insert(tk.END, message + '\n')
        self.progress_text.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = FolderRenamerApp(root)
    root.mainloop()
