import tkinter as tk
import file_area
import text_area
import terminal
import subprocess

def open_file(initial_dir):
    filename = tk.filedialog.askopenfilename(initialdir = initial_dir)
    if filename != "":
        file_area.open_file(filename)

def run_file():
    if text_area.text_area == None: return
    if text_area.text_area.currently_open_file == None: return
    if text_area.text_area.mode != "File": return
    terminal.execute(text_area.text_area.currently_open_file)
def run_in_external_terminal():
    if text_area.text_area == None: return
    if text_area.text_area.currently_open_file == None: return
    if text_area.text_area.mode != "File": return
    terminal.execute(text_area.text_area.currently_open_file, external=True)
    
    
