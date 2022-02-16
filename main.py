import tkinter as tk
from PIL import ImageTk, Image
import constants
from tkinter.filedialog import askopenfilename

import button_bar
import os
import file_area
import text_area
import time
import pyautogui

window = None










test_image = None
browse_icon = None
run_icon = None

#load images and icons
def load_resources():
    global test_image,browse_icon,run_icon
    test_image = Image.open("test.png").resize((constants.button_size, constants.button_size))
    test_image = ImageTk.PhotoImage(test_image)
    browse_icon = Image.open("icons/browse.png").resize((constants.button_size, constants.button_size))
    browse_icon = ImageTk.PhotoImage(browse_icon)
    run_icon = Image.open("icons/run.png").resize((constants.button_size, constants.button_size))
    run_icon = ImageTk.PhotoImage(run_icon)




#includes the file bar as well as thre buttons
def create_left_panel(parent):
    left_panel_frame = tk.Frame(parent)
    top_bar_frame = create_top_bar(left_panel_frame)
    file_area_frame = file_area.create_file_area(left_panel_frame)#create the file bar
    
    
    file_area_frame.pack(side=tk.BOTTOM, fill="both", expand=True)
    
    
    
    left_panel_frame.pack(side=tk.LEFT, fill="both")
    return left_panel_frame

#frame contains the buttons
def create_top_bar(parent):
    
    
    
    top_bar_frame = tk.Frame(parent)
    open_file = tk.Button(
        top_bar_frame, 
        command=lambda: button_bar.open_file(os.path.expanduser("~/Documents")), 
        image=browse_icon, 
        height = constants.button_size, 
        width = constants.button_size
        )
    run_file = tk.Button(
        top_bar_frame, 
        command=lambda: button_bar.run_file(), 
        image=run_icon, 
        height = constants.button_size, 
        width = constants.button_size
        )
        
    
    
    
    open_file.pack(side=tk.LEFT, padx = constants.button_padding, pady = constants.button_padding)
    
    
    run_file.pack(side=tk.LEFT, padx = constants.button_padding, pady = constants.button_padding)
    menu = tk.Menu(parent, tearoff=0)
    menu.add_command(label = "Run Separate", command = button_bar.run_in_external_terminal)
    run_file.bind("<Button-3>", lambda e: popup_menu_run(menu))
    
    top_bar_frame.pack(side=tk.TOP, fill="x")
    return top_bar_frame
    
def popup_menu_run(menu):
    pos = pyautogui.position()
    menu.tk_popup(*pos)

#WARNING: DO NOT RELY ON GAME LOOP OR GAME LOOP TIME FRAME AS A CLOCK
#tkinter schedules things for whenever it wants and is not very accurate
#Usually off by about 20% aka if i tell it to do 20 ticks per second
#it might do 16 ticks per second
counter = 0
def main_loop():    
    global counter
    counter += 1
    
    start = time.time()
    for ta in text_area.text_areas:
        ta.step(counter)
    
    
    window.after(constants.game_loop_frame_time, main_loop)
    
def on_closing():
    for ta in text_area.text_areas:
        ta.save()
    window.destroy()
def main():
    
    global window
    window = tk.Tk()
    
    load_resources()
    
    window.geometry("1500x800")
    
    left_panel_frame = create_left_panel(window)
    
    text_area_frame = text_area.create_text_area(window, window)
    
    
    window.protocol("WM_DELETE_WINDOW", on_closing)
    
    file_area.load_open_files_log()
    
    
    window.after(constants.game_loop_frame_time, main_loop)
    
    window.mainloop()
    

if __name__ == "__main__": main()
