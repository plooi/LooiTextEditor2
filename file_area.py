import tkinter as tk

import os
import constants
import text_area
import pyautogui
import button_bar
import terminal


"""
Every listbox element consists of a single string
that displays the name of the file. But when you click
on the listbox element, i can only read what the 
element's text is, and if each element only had
the file name (not whole path) i cant open the file
because i don't know the whole path. Thus, my hack
is that after the file name, there will be a bunch
of spaces and then at a predetermined index in the
string (constants.file_area_path_index) the full file path
will be kept. gen_listbox_text takes a filename and
turns it into the specific string format which includes
the file name at the front as well as the full file
path later on

The full file path is not displayed because the file
area is not wide enough, thus only the file name is 
shown

extract_filepath_from_listbox_text is the opposite
of gen_listbox_text. extract_filepath_from_listbox_text
takes the listbox text and extracts the full file path
from it, so that when you click on it the computer can
then go and load the file taht you wanted
"""
def fix_length(string, length):
    if len(string) == length:
        return string
    elif len(string) <= length:
        return string + " " * (length - len(string))
    else:
        return string[0:length-3] + "..."
def gen_listbox_text(filename):
    
    #print(len(fix_length(os.path.basename(filename), constants.file_area_character_limit)))
    return fix_length(os.path.basename(filename), constants.file_area_character_limit) + (constants.file_area_path_index-constants.file_area_character_limit)*" " + filename
def extract_filepath_from_listbox_text(lbt):
    return lbt[constants.file_area_path_index:]

listbox = None
menu = None
right_click_index = None


file_information = {}


#creates the open file list and the containing frame
def create_file_area(parent):
    global listbox
    
    file_area_frame = tk.Frame(parent)
    
    file_scrollbar = tk.Scrollbar(file_area_frame)
    
    file_area = tk.Listbox(
        file_area_frame, 
        yscrollcommand = file_scrollbar.set, 
        width=constants.file_area_width,
        activestyle='none',
        selectforeground=constants.file_area_select_foreground,
        selectbackground=constants.file_area_select_background,
        foreground=constants.file_area_foreground,
        background=constants.file_area_background,
        font = constants.file_area_font, 
        )
    listbox = file_area
    file_area.bind("<<ListboxSelect>>", on_select)
    file_area.bind("<Button-3>", right_click)
    
    
    
    file_scrollbar.config(command = file_area.yview)
    file_area_frame.pack(side=tk.LEFT, fill=tk.BOTH)
    file_scrollbar.pack(side=tk.RIGHT, fill=tk.BOTH)
    file_area.pack(side=tk.LEFT, fill=tk.BOTH)
    
    
    #create the right click menu
    global menu
    menu = tk.Menu(parent, tearoff=0)
    menu.add_command(label = "Remove", command = remove_file)
    menu.add_command(label = "Browse From Here", command = browse_from_here)
    
    
        
    
    return file_area_frame
    
"""
when you right click a file and say remove
this is the code that runs
"""
def remove_file():
    listbox_text = listbox.get(right_click_index)
    if listbox_text.endswith(">"):
        file_name = listbox_text
    else:
        file_name = extract_filepath_from_listbox_text(listbox_text)
    listbox.delete(right_click_index)
    for ta in text_area.text_areas:
        
        if listbox_text.endswith(">") and ta.currently_open_file == file_name:
            terminal.delete_terminal_instance(file_name)
            ta.open_file(None)
        if (not listbox_text.endswith(">")) and (not ta.currently_open_file==None) and os.path.normpath(ta.currently_open_file) == os.path.normpath(file_name):
            ta.open_file(None)
    update_open_files() 
            
def browse_from_here():
    button_bar.open_file(os.path.dirname(extract_filepath_from_listbox_text(listbox.get(right_click_index))))
            
    
def right_click(event):
    global right_click_index
    right_click_index = listbox.index("@%s,%s" % (event.x, event.y))
    if right_click_index == -1:
        return
    listbox.selection_clear(0, tk.END)
    listbox.selection_set(first=right_click_index)
    on_select(event)  
    try:
        #menu.tk_popup(event.x + window.winfo_x(), event.y + window.winfo_y())
        pos = pyautogui.position()
        menu.tk_popup(*pos)
    finally:
        menu.grab_release()
        
      
        
def new_file_information():
    return {
        "file_scroll_position" : None,
        "undo_log" : [],
        "current_undo_frame" : None,
        
    
    }
        

#open a file to the file area/left panel
def open_file(filename, open_in_text_area=True, update_open_files_log=True):
    listbox.insert(0, gen_listbox_text(filename))
    file_information[filename] = new_file_information()
    
    if open_in_text_area: text_area.text_area.open_file(filename)
    if update_open_files_log: update_open_files()
    

    
def update_open_files():
    #rewrite the open files document
    f = open(constants.open_file_log, "w")
    for i in range(listbox.size()):
        f.write(extract_filepath_from_listbox_text(listbox.get(i)) + "\n")
        
#open all the files that are in the open files log
#so that if you close text editor next time you open it
#the same files will be there
def load_open_files_log():
    if not os.path.isfile(constants.open_file_log):
        return
    f = open(constants.open_file_log, "r")
    for line in f:
        if line.strip() != "":
            open_file(line.strip(), open_in_text_area=False, update_open_files_log=False)
        
        
    


#with listboxes, clicking on an element is actually technically
#selection, so this function is the callback when a file is 
#clicked on/selected
def on_select(event):
    selected_indices = listbox.curselection()
    
    if len(selected_indices) == 0: return
    
    entry_text = listbox.get(selected_indices[0])
    
    if entry_text.endswith(">"):
        text_area.text_area.open_terminal(entry_text)
    else:
        text_area.text_area.open_file(extract_filepath_from_listbox_text(entry_text))#debug
    
    
    #listbox.selection_clear(0, tk.END)
    #print(str(selected_indices) + ":" + listbox.get(selected_indices[0]) + " : " + listbox.get(selected_indices[0])[constants.file_area_path_index])

