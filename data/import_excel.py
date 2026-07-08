#!/usr/bin/env python3
"""
Excel to PostgreSQL Import Tool for NSSF Searchbot

This script provides a user-friendly way to import Excel data into the PostgreSQL database
for the NSSF Voice & Text AI Searchbot. It includes a simple GUI for selecting the Excel file
and configuring database connection parameters.
"""

import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import subprocess
from pathlib import Path

class ExcelImportApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NSSF Excel Import Tool")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Set icon (placeholder)
        # self.root.iconbitmap('icon.ico')
        
        # Configure style
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f5f7f9')
        self.style.configure('TButton', font=('Arial', 11))
        self.style.configure('TLabel', font=('Arial', 11), background='#f5f7f9')
        self.style.configure('Header.TLabel', font=('Arial', 14, 'bold'), background='#f5f7f9')
        
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="20 20 20 20", style='TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_label = ttk.Label(self.main_frame, 
                                text="NSSF Excel Import Tool", 
                                style='Header.TLabel')
        header_label.grid(row=0, column=0, columnspan=3, pady=(0, 20), sticky="w")
        
        # Excel file selection
        ttk.Label(self.main_frame, text="Excel File:", style='TLabel').grid(row=1, column=0, sticky="w", pady=5)
        
        self.file_frame = ttk.Frame(self.main_frame, style='TFrame')
        self.file_frame.grid(row=1, column=1, sticky="ew", pady=5)
        self.file_frame.columnconfigure(0, weight=1)
        
        self.file_path = tk.StringVar()
        self.file_entry = ttk.Entry(self.file_frame, textvariable=self.file_path, width=40)
        self.file_entry.grid(row=0, column=0, sticky="ew")
        
        self.browse_button = ttk.Button(self.file_frame, text="Browse", command=self.browse_file)
        self.browse_button.grid(row=0, column=1, padx=(5, 0))
        
        # Database connection settings
        ttk.Label(self.main_frame, text="Database Settings", style='Header.TLabel').grid(row=2, column=0, columnspan=3, pady=(20, 10), sticky="w")
        
        # Host
        ttk.Label(self.main_frame, text="Host:", style='TLabel').grid(row=3, column=0, sticky="w", pady=5)
        self.host_var = tk.StringVar(value="localhost")
        ttk.Entry(self.main_frame, textvariable=self.host_var, width=30).grid(row=3, column=1, sticky="w", pady=5)
        
        # Port
        ttk.Label(self.main_frame, text="Port:", style='TLabel').grid(row=4, column=0, sticky="w", pady=5)
        self.port_var = tk.StringVar(value="5432")
        ttk.Entry(self.main_frame, textvariable=self.port_var, width=30).grid(row=4, column=1, sticky="w", pady=5)
        
        # Database name
        ttk.Label(self.main_frame, text="Database:", style='TLabel').grid(row=5, column=0, sticky="w", pady=5)
        self.db_var = tk.StringVar(value="nssf_db")
        ttk.Entry(self.main_frame, textvariable=self.db_var, width=30).grid(row=5, column=1, sticky="w", pady=5)
        
        # Username
        ttk.Label(self.main_frame, text="Username:", style='TLabel').grid(row=6, column=0, sticky="w", pady=5)
        self.user_var = tk.StringVar(value="nssf_user")
        ttk.Entry(self.main_frame, textvariable=self.user_var, width=30).grid(row=6, column=1, sticky="w", pady=5)
        
        # Password
        ttk.Label(self.main_frame, text="Password:", style='TLabel').grid(row=7, column=0, sticky="w", pady=5)
        self.password_var = tk.StringVar(value="nssf_password")
        password_entry = ttk.Entry(self.main_frame, textvariable=self.password_var, width=30, show="*")
        password_entry.grid(row=7, column=1, sticky="w", pady=5)
        
        # Docker mode checkbox
        self.docker_mode = tk.BooleanVar(value=False)
        docker_check = ttk.Checkbutton(self.main_frame, text="Docker Mode", variable=self.docker_mode, 
                                      command=self.toggle_docker_mode)
        docker_check.grid(row=8, column=0, columnspan=2, sticky="w", pady=(10, 5))
        
        # Help text
        help_text = "Enable Docker Mode if you're running the database in a Docker container."
        ttk.Label(self.main_frame, text=help_text, font=("Arial", 9), foreground="gray").grid(row=9, column=0, columnspan=3, sticky="w")
        
        # Progress bar
        self.progress = ttk.Progressbar(self.main_frame, orient=tk.HORIZONTAL, length=100, mode='indeterminate')
        self.progress.grid(row=10, column=0, columnspan=3, sticky="ew", pady=(20, 5))
        
        # Status label
        self.status_var = tk.StringVar(value="Ready to import data")
        status_label = ttk.Label(self.main_frame, textvariable=self.status_var, font=("Arial", 10))
        status_label.grid(row=11, column=0, columnspan=3, sticky="w", pady=(0, 10))
        
        # Buttons frame
        button_frame = ttk.Frame(self.main_frame, style='TFrame')
        button_frame.grid(row=12, column=0, columnspan=3, sticky="ew", pady=(10, 0))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        
        # Import button
        self.import_button = ttk.Button(button_frame, text="Import Data", command=self.import_data)
        self.import_button.grid(row=0, column=0, padx=5, sticky="e")
        
        # Exit button
        exit_button = ttk.Button(button_frame, text="Exit", command=self.root.destroy)
        exit_button.grid(row=0, column=1, padx=5, sticky="w")
        
        # Configure grid weights
        self.main_frame.columnconfigure(1, weight=1)
    
    def browse_file(self):
        """Open file dialog to select Excel file"""
        filetypes = [
            ("Excel files", "*.xlsx *.xls"),
            ("All files", "*.*")
        ]
        filename = filedialog.askopenfilename(title="Select Excel File", filetypes=filetypes)
        if filename:
            self.file_path.set(filename)
    
    def toggle_docker_mode(self):
        """Toggle between Docker and local mode"""
        if self.docker_mode.get():
            self.host_var.set("postgres")
        else:
            self.host_var.set("localhost")
    
    def import_data(self):
        """Import data from Excel to PostgreSQL"""
        # Validate inputs
        if not self.file_path.get():
            messagebox.showerror("Error", "Please select an Excel file")
            return
        
        if not os.path.exists(self.file_path.get()):
            messagebox.showerror("Error", "Selected file does not exist")
            return
        
        # Start progress bar
        self.progress.start()
        self.status_var.set("Importing data...")
        self.import_button.config(state="disabled")
        self.root.update()
        
        try:
            # Get the path to the import script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            import_script = os.path.join(script_dir, "data", "import_script.py")
            
            # Build command
            if self.docker_mode.get():
                # Docker mode - use docker exec
                cmd = [
                    "docker", "exec", "nssf_postgres",
                    "python", "/app/data/import_script.py",
                    "--excel-file", "/app/data/" + os.path.basename(self.file_path.get()),
                    "--db-host", self.host_var.get(),
                    "--db-port", self.port_var.get(),
                    "--db-name", self.db_var.get(),
                    "--db-user", self.user_var.get(),
                    "--db-password", self.password_var.get()
                ]
                
                # First, copy the Excel file to the data directory
                data_dir = os.path.join(script_dir, "data")
                dest_path = os.path.join(data_dir, os.path.basename(self.file_path.get()))
                if self.file_path.get() != dest_path:
                    self.status_var.set("Copying Excel file...")
                    self.root.update()
                    import shutil
                    shutil.copy2(self.file_path.get(), dest_path)
            else:
                # Local mode - run Python script directly
                cmd = [
                    sys.executable, import_script,
                    "--excel-file", self.file_path.get(),
                    "--db-host", self.host_var.get(),
                    "--db-port", self.port_var.get(),
                    "--db-name", self.db_var.get(),
                    "--db-user", self.user_var.get(),
                    "--db-password", self.password_var.get()
                ]
            
            # Run the command
            self.status_var.set("Running import script...")
            self.root.update()
            
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                self.status_var.set("Import completed successfully!")
                messagebox.showinfo("Success", "Data imported successfully!\n\n" + stdout)
            else:
                self.status_var.set("Import failed!")
                messagebox.showerror("Error", f"Failed to import data:\n\n{stderr}")
        
        except Exception as e:
            self.status_var.set("Import failed!")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        
        finally:
            # Stop progress bar and re-enable button
            self.progress.stop()
            self.import_button.config(state="normal")


def main():
    root = tk.Tk()
    app = ExcelImportApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()