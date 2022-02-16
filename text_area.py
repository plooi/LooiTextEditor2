import tkinter as tk

import os
import constants

import time

import hotkey_manager
import tkinter.messagebox as mb
import tkinter.colorchooser as cc
import main
import file_area
import pyautogui
import tkinter.simpledialog as sd
import terminal
import util
import shutil
import line_numbers
import text_coloring

#keeps tracks of which files are currently open
open_files = [None,None]



#just in case we end up using multiple text area objects
text_areas = []

#this variable holds the active text area object
text_area = None

#creates the big text box where the files are displayed 
#and you can type in
def create_text_area(parent, window):
    global text_area
    text_area_frame = tk.Frame(parent)
    line_numbers_area = line_numbers.LineNumbers(text_area_frame, width=constants.line_numbers_area_width, height=5000)
    line_numbers_area.pack(side=tk.LEFT, fill="both")
    text_area = TextArea(text_area_frame, line_numbers_area, window=window, width=5000,height=5000)
    text_areas.append(text_area)
    
    #text_area.pack(side=tk.RIGHT, fill="both")
    
    
    text_area_frame.pack(side=tk.RIGHT, fill="both")
    
    
    
    
    
    return text_area_frame
    



def execute_both(a, args1, b, args2):
    a(*args1)
    b(*args2)
    #print(args1, args2)
def execute3(a, args1, b, args2, c, args3):
    a(*args1)
    b(*args2)
    c(*args3)
    #print(args1, args2, args3)
class TextArea(tk.Text):
    def __init__(self, text_area_frame, line_numbers_area, window=None, **args):
        super(TextArea, self).__init__(
                                            text_area_frame, 
                                            insertofftime = constants.caret_blink_off_time,
                                            insertontime = constants.caret_blink_on_time,
                                            **args)
        self.window = window
        self.text_area_frame = text_area_frame
        self.line_numbers_area = line_numbers_area
        line_numbers_area.text_area = self
        
        self.hotkey_manage = hotkey_manager.HotkeyManager(self)
        
        self.style = {}
        self.enclosing_style = {}
        self.enclosing_style_sorted_keys = []
        
        self.text_scrollbar = tk.Scrollbar(text_area_frame, command=lambda *args: execute_both(self.yview, args, self.line_numbers_area.yview, args))
        #self.text_scrollbar = tk.Scrollbar(text_area_frame, command=self.yview)
        #self["yscrollcommand"] = self.text_scrollbar.set
        self["yscrollcommand"] = lambda first, last: execute3(self.text_scrollbar.set, (first,last), self.line_numbers_area.yview, ("moveto", first), self.yview, ("moveto", first))
        self.line_numbers_area["yscrollcommand"] = lambda first, last: execute3(self.text_scrollbar.set, (first,last), self.line_numbers_area.yview, ("moveto", first), self.yview, ("moveto", first))
        
        #help(self.text_scrollbar.set)
        
        self.reset_text_colors_pending = False
        self.text_tokenizer = None
        #self.insert(tk.END, "hello")
        
        self.text_scrollbar.pack(side=tk.RIGHT, fill="both")
        self.pack(side=tk.RIGHT,  fill="both")
        
        self.bind("<<Modified>>", self._text_modify_callback)
        self.bind("<KeyPress>", self.key_press_callback)
        self.bind("<KeyRelease>", self.key_release_callback)
        self.bind("<Button-3>", self.right_click_callback)
        
        
        #keeps track of whether the control, alt, and shift keys
        #are currently pressed or released, to allow you to 
        #keep track of 
        #None means the key is not pressed
        #number value means the key is being held down
        #and the number is the time at which the key was pressed
        self.hotkey_elements = {"control" : None, "alt" : None, "shift" : None}
        
        
        self.text_modify_callback_every_other = False
        
        #which file the text area is currently displaying
        self.currently_open_file = None
        
        
        self.last_undo_frame_save_time = None
        self.undo_frame_save_pending = False
        
        
        self.last_save_time = None
        self.unsaved_changes = False
        self.opening_new_file_dont_immediately_save = False
        
        self.menu = tk.Menu(text_area_frame, tearoff=0)
        
        self.menu.add_command(label = "Change Color of This Word", command = self.change_color)
        
        self.menu.add_command(label = "Change Background", command = lambda: self.change_color("*background"))
        self.menu.add_command(label = "Change Highlight Color", command = lambda: self.change_color("*highlight"))
        self.menu.add_command(label = "Change Caret Color", command = lambda: self.change_color("*caret"))
        self.menu.add_command(label = "Change Default Text Color", command = lambda: self.change_color("*default"))
        self.menu.add_command(label = "Remove Color of This Word", command = lambda: self.remove_tag())
        self.menu.add_command(label = "Switch Style", command = lambda: self.switch_style())
        self.menu.add_command(label = "Change Font Size", command = self.change_font)
        self.menu.add_command(label = "New Style", command = lambda: self.new_style())
        self.menu.add_command(label = "Delete Style", command = lambda: self.delete_style())
        
        
        self.mode = None
        
        
        self.cleared_tokens_up_to= None#used for recoloring... for removing patches of tags
        #at a time rather than removing everythign then recoloring everything
        
        self.set_font_size(int(self.load_settings_file("font-size", 16)))
        
        
        self.open_file(None)
    
    
    def change_font(self):
        s = sd.askstring(title="", prompt="Select Font Size", initialvalue=str(self.font_size))
        if s == None: return
        try:
            s = int(s)
            self.set_font_size(s)
        except Exception as e:
            mb.showerror(str(e))
    def set_font_size(self, fs):
        self.font_size = fs
        self.configure(font=("Courier New", self.font_size, ""))
        self.line_numbers_area.configure(font=("Courier New", self.font_size, ""))
        self.write_settings_file()
    def load_settings_file(self, key = None, default_value = None):
        if os.path.isfile(constants.settings_file):
            f = open(constants.settings_file, "r")
            s = ""
            for line in f:
                s += line
            f.close()
            try:
                d = eval(s)
                if key != None:
                    if key in d:
                        return d[key]
                    else:
                        return default_value
                else:
                    return d
            except Exception as e:
                mb.showerror(str(e))
        else:
            if default_value == None:
                return {}
            else:
                return default_value
    def write_settings_file(self):
        try:
            f = open(constants.settings_file, "w")
            f.write(str(
            {
                "font-size" : self.font_size
            
            
            }
            
            
            )
            )
            f.close()
        except Exception as e:
            mb.showerror(str(e))
    def new_style(self):
        default_style_name = "NewStyle"
        
        if not os.path.isdir(constants.style_file_folder):os.mkdir(constants.style_file_folder)
            
        
        """
        default style name is "NewStyle" but if there
        already is a file named NewStyel then we want to
        have the suggested default name to be NewStyle2
        but if NewStyle2 is already taken then we suggest
        newStyle3 and so on and so on so so the goal
        of this segment of code is so that at the end of this
        segment the i variable contains the lowest number 
        after "NewStyle<insert number here>"that is not taken yet
        """
        default_style_name_numbers = set()
        for file in os.listdir(constants.style_file_folder):
            file = os.path.join(constants.style_file_folder, file)
            directory, basename, extension = util.split(file)
            if basename.startswith(default_style_name):
                try:
                    if basename == default_style_name: 
                        default_style_name_numbers.add(1)
                    else:
                        number = int(basename[len(default_style_name):])
                        default_style_name_numbers.add(number)
                except:
                    pass
        i=1
        while True:
            if i not in default_style_name_numbers:
                break
            i += 1
        
        
        
        
        
        
        
        new_style_name = sd.askstring(title = "New Style Name", prompt = "Enter name of new style", initialvalue=default_style_name + (str(i) if i > 1 else ""))
        if new_style_name == None: return
        
        _, __, extension = util.split(self.currently_open_file)
        if len(extension) >= 2:
            extension = extension[1:]
        else:
            extension = ""
        
        
        file_path_of_new_style_file = os.path.join(constants.style_file_folder, new_style_name + "." + extension + "-")
        if os.path.isfile(file_path_of_new_style_file) or os.path.isfile(file_path_of_new_style_file[0:-1]+"_"):
            mb.showinfo(title="", message="Style name \"" + new_style_name + "\" is already taken. Choose a different name.")
        else:
            shutil.copy(self.get_appropriate_style_file(), file_path_of_new_style_file)
            self.switch_to_style(file_path_of_new_style_file)
        
    def delete_style(self):
        
        delete_style_menu = tk.Menu(self.text_area_frame, tearoff=0)
        if os.path.isdir(constants.style_file_folder):
            if self.currently_open_file != None:
                
                _,_,extension = util.split(self.get_appropriate_style_file())
                extension = extension[0:-1]
                for file in os.listdir(constants.style_file_folder):
                    
                    file_full_path = os.path.join(constants.style_file_folder, file)
                    _, basename, _extension = util.split(file_full_path)
                    if _extension == extension + "-":
                        delete_style_menu.add_command(label = basename, command = lambda fp=file_full_path, bn=basename: self.do_delete_style(fp,bn))
                    elif _extension == extension + "_":
                        delete_style_menu.add_command(label = "*" + basename, command = lambda fp=file_full_path, bn=basename: self.do_delete_style(fp,bn))
                        
                        
        util.popup(delete_style_menu)
    def do_delete_style(self, style_file_name, basename):
        if(mb.askyesno(title="", message="Are you sure you want to delete the style named \"" + basename +"\"?")):
            os.remove(style_file_name)
    
        self.open_style_file()
        self.reset_text_colors()
    def switch_style(self):
        switch_style_menu = tk.Menu(self.text_area_frame, tearoff=0)
        if os.path.isdir(constants.style_file_folder):
            if self.currently_open_file != None:
                _,_,extension = util.split(self.get_appropriate_style_file())
                extension = extension[0:-1]
                if extension == None: extension = "_"
                for file in os.listdir(constants.style_file_folder):
                    
                    file_full_path = os.path.join(constants.style_file_folder, file)
                    _, basename, _extension = util.split(file_full_path)
                    if _extension == extension + "-":
                        switch_style_menu.add_command(label = basename, command = lambda fp=file_full_path: self.switch_to_style(fp))
                    elif _extension == extension + "_":
                        switch_style_menu.add_command(label = "*" + basename, command = lambda fp=file_full_path: self.switch_to_style(fp))
                        
        
        util.popup(switch_style_menu)
    def switch_to_style(self, style_file_name ):# style file name is full path (assumed to be inside style file folder)
        _,_,extension = util.split(style_file_name)
        if extension == "": raise Exception("???")
        
        if not os.path.isfile(style_file_name): 
            #print(style_file_name, "not a file")
            return
        if not style_file_name.endswith("-"): return
        
        if style_file_name.endswith("_"): return
        
        for file in os.listdir(constants.style_file_folder):
            _,_,ext = util.split(file)
            if ext[0:-1] == extension[0:-1]:
                os.rename(os.path.join(constants.style_file_folder, file), os.path.join(constants.style_file_folder, file[0:-1] + "-"))
                
        os.rename(style_file_name, style_file_name[0:-1] + "_")
        
        self.open_style_file()
        self.reset_text_colors()
                
    def open_terminal(self, entry_text):
        if self.mode == "File":
            self.save()
        self.currently_open_file = entry_text
        self.delete("1.0", "end -1 chars")
        self.mode = "Terminal"
        self.open_style_file()
        self.reset_text_colors()
    
    def right_click_callback(self, event):
        if self.currently_open_file == None:return
        self.mark_set("insert", self.index("@%d,%d" %(event.x, event.y)))
        util.popup(self.menu)
        
    
    def remove_tag(self):
        tags = list(self.tag_names(index=self.index("insert")))
        
        try:
            style_file = self.get_appropriate_style_file()
            lines = []
            f = open(style_file, "r")
            for line in f: lines.append(line)
            f.close()
            for i in range(len(lines)):
                
                parts = lines[i].split(" ")
                if parts[0] in tags:
                    lines[i] = "\n"
                if not lines[i].endswith("\n"): lines[i] += "\n"
            
            out = "".join(lines)
            while out.endswith("\n"): out=out[0:-1]
            
            
            f = open(style_file, "w")
            f.write(out)
            f.close()
            
        
        except Exception as e:
            mb.showerror(message=str(e))
            
        self.open_style_file()
        self.reset_text_colors()
    def change_color(self, tag = None):
        if tag == None:
            tags = list(self.tag_names(index=self.index("insert")))
        else:
            tags = [tag]
        if "sel" in tags: tags.remove("sel")
        
        default_color = "#FFFFFF"
        if len(tags) > 0:
            if "`" in tags[0] and tuple(tags[0].split("`")) in self.enclosing_style:
                default_color = self.enclosing_style[tuple(tags[0].split("`"))]
            elif tags[0] in self.style:
                default_color = self.style[tags[0]]
            color = cc.askcolor(default_color, title = "Choosing color for the token(s): " + ",".join(tags))
            if color == None: return
            if color[0] == None: return
            color = list(color[0])
            style_file = self.get_appropriate_style_file()
            
            lines = []
            f = open(style_file, "r")
            for line in f: lines.append(line)
            f.close()
            
        
            try:
                for i in range(len(lines)):
                    
                    parts = lines[i].split(" ")
                    if parts[0] in tags:
                        lines[i] = parts[0] + " " + " ".join([str(int(x)) for x in color]) + "\n"
                    if not lines[i].endswith("\n"): lines[i] += "\n"
                else:
                    lines.append(tags[0] + " " + " ".join([str(int(x)) for x in color]) + "\n")
                    #print("got here")
                out = "".join(lines)
                while out.endswith("\n"): out=out[0:-1]
                
                
                f = open(style_file, "w")
                f.write(out)
                f.close()
                
            
            except Exception as e:
                mb.showerror(message=str(e))
        else:
            
            #there is no tag currently selected  aka we right clicked on a default text
            
            #find the nearest token like thing
            maybe_the_token_they_were_looking_for = ""
            
            
            
            char_at_caret_is_space  = self.get(self.index("insert")) in {" ", "\n", "\t", "\r"}
            char_b4_caret_is_space = self.get(self.index("insert -1 chars")) in {" ", "\n", "\t", "\r"}
            if char_at_caret_is_space and char_b4_caret_is_space:
                pass
            
            elif char_b4_caret_is_space and self.get(self.index("insert")) not in constants.letters_and_numbers_caps_underscore:
                maybe_the_token_they_were_looking_for = self.get(self.index("insert"))
            elif char_at_caret_is_space and self.get(self.index("insert -1 chars")) not in constants.letters_and_numbers_caps_underscore:
                maybe_the_token_they_were_looking_for = self.get(self.index("insert -1 chars"))
            else:
                start = self.find_previous("insert -1 chars", constants.letters_and_numbers_caps_underscore, complement=True)
                end = self.find_next("insert", constants.letters_and_numbers_caps_underscore, complement=True)
                if start == -1 and end == -1:
                    maybe_the_token_they_were_looking_for = self.get("1.0", "end -1 chars")
                elif start == -1:
                    maybe_the_token_they_were_looking_for = self.get("1.0", end)
                elif end == -1:
                    maybe_the_token_they_were_looking_for = self.get(start + " +1 chars", "end -1 chars")
                else:
                    maybe_the_token_they_were_looking_for = self.get(start + " +1 chars", end)
                print(start,end)
            if len(maybe_the_token_they_were_looking_for) == 0: return
            
            all_numbers = False
            if len(maybe_the_token_they_were_looking_for) > 0:
                all_numbers = True
                for z in range(len(maybe_the_token_they_were_looking_for)):
                    if maybe_the_token_they_were_looking_for[z] not in constants.numbers:
                        all_numbers = False
                        break
            #style_name=None
            if all_numbers:
                style_name = "*number"
            else:
                style_name = sd.askstring(title = "Input", prompt = "What word/symbol do you want to color?\nOr, you can choose any two symbols and make all text in between those symbols a certain color.\n For example, if you want all things that look like this <<insert text here>> to be colored, you would enter below \n<<`>>\n The << is the prefix and >> is the suffix and ` marks where the prefix ends and the suffix begins. \nTo specify a string literal you could say \"`\". ", initialvalue=maybe_the_token_they_were_looking_for)
            
            if style_name == None: return
            
            
            
            color = cc.askcolor(default_color, title = "Choosing color for the token \"" + style_name + "\"")
            if color == None: return
            if color[0] == None: return
            color = list(color[0])
            style_file = self.get_appropriate_style_file()
            
            
            lines = []
            f = open(style_file, "r")
            for line in f: lines.append(line)
            f.close()
        
            try:
                for i in range(len(lines)):
                    
                    parts = lines[i].split(" ")
                    if parts[0] == style_name:
                        lines[i] = parts[0] + " " + " ".join([str(int(x)) for x in color]) + "\n"
                    if not lines[i].endswith("\n"): lines[i] += "\n"
                else:
                    lines.append(style_name + " " + " ".join([str(int(x)) for x in color]) + "\n")
                
                out = "".join(lines)
                while out.endswith("\n"): out=out[0:-1]
                
                
                f = open(style_file, "w")
                f.write(out)
                f.close()
                
            
            except Exception as e:
                mb.showerror(message=str(e))
            
            
            
                #raise e
        self.open_style_file()
        self.reset_text_colors()
        #print(color, type(color))
        
    
    def find_next(self, start_index : str, substrings, complement=False) -> str:
        if isinstance(substrings, str): substrings = {substrings}
        i = 0
        while True:
            index = start_index + " +" + str(i) + " chars"
            if self.do_any_strings_start_at_this_index(substrings, index) == (not complement):
                return index
            
            if self.compare(index, "==", "end"):
                return -1
            
            i+=1
    def find_previous(self, start_index : str, substrings, complement=False) -> str:
        if isinstance(substrings, str): substrings = {substrings}
        i = 0
        while True:
            index = start_index + " -" + str(i) + " chars"
            
            if self.do_any_strings_start_at_this_index(substrings, index) == (not complement):
                return index
            if self.compare(index, "==", "1.0"):
                return -1
            i+=1
    def do_any_strings_start_at_this_index(self, substrings, index):
        for substring in substrings:
            if self.get(index, index + " +" + str(len(substring)) + " chars") == substring:
                return True
                
        return False
    def get_indent(self, text_index):
        
        #count how many spaces at beginning of line
        i = 0
        while True:
            index = text_index + " linestart +" + str(i) + " chars"
            
            if self.compare(index, "==", "end") or self.get(index) != " ":
                break
            
            
            i += 1
        num_spaces = i
        #print("num_spaces", num_spaces)
        return num_spaces
        
        
        
        """
        i = 0
        while True:
            index = text_index + " -" + str(i) + " chars"
            
            if 
            
            i += 1
        """
    
    """
    #the key press module makes it so that
    #you can have complex hotkeys like 
    #control+shift and stuff
    #and all YOU need to do is just implement
    #the code that executes upon pressing those
    hotkeys inside the "hotkey" function 
    """
    def key_press_callback(self, event):
    
        key = str(event.keysym)
        #print(key)
        
        
        
        #deal with changing the tags every time you type
        self.window.after(10, self.reset_text_colors)
        
        #make the text editor see the place where the cursor is
        #if we just typed something into the text editor
        if key in constants.typeable_keys: 
            self.window.after(10, lambda:self.see("insert"))
        
        
        
        
        
        
        
        
        
        
        
        if key.startswith("Alt"): self.hotkey_elements["alt"] = time.time()
        if key.startswith("Control"): self.hotkey_elements["control"] = time.time()
        if key.startswith("Shift"): self.hotkey_elements["shift"] = time.time()
        
        
        #execute the proper hotkey if it is one of the allowed
        #hotkey keys
        
        #find _key, which is the key but without the capitalizations, so like
        #if you pressed "a" then _key would be "a" but if you pressed shift+9
        #key is "(" but _key would still be 9
        _key = key.lower()
        if _key in constants.num_shift_keys_conversion:
            _key = constants.num_shift_keys_conversion[_key]
            
            
            
        #generate the hotkey string
        #after this section of code, hotkey_string will either contain
        #the full hotkey description e.g. "control+shift+h"
        #or if neither of the hotkey qualifiers {shift,ctl,alt} were pressed
        #it will just be "" to indicate that no hotkey should be executed
        
        hotkey_string = ""
        if _key in constants.hotkey_keys:
            for key_ in self.hotkey_elements:
                if self.hotkey_elements[key_] != None:
                    hotkey_string += key_ + "+"
            
            #if neither shift or
            if hotkey_string != "":
                hotkey_string += _key
                
        
        
        
        #print("hotkey_string is", hotkey_string)
        #execute hotkey
        if hotkey_string != "":
            if self.mode == "File":
                res = self.hotkey_manage.receive_hotkey(hotkey_string)
                if res == "break":
                    return res
            elif self.mode == "Terminal":
                terminal.handle_key_press(hotkey_string, self.currently_open_file, event.char)
                return "break"
        else:#hotkey_string == ""
            if self.mode == "Terminal":
                terminal.handle_key_press(_key, self.currently_open_file, event.char)
                return "break"
                
        #special case to override ctl-z and ctl-y to have my own undo functionality
        if hotkey_string in {"control+z", "control+y", "control+k"}:
            #self.reset_text_colors() #maybe is this line needed idk?
            return "break"
                
            
            
            
            
        
        
        #respect indent on enter
        if constants.enter_respects_indent:
            #get indent
            
            if key == "Return":
                self.insert("insert", "\n" + " " * self.get_indent("insert"))
                return "break"
            
        #make tab spaces not tab character
        if key == "Tab":
            self.hotkey_manage.receive_hotkey("tab")
            return "break"
        
    def release_all_hotkey_qualifiers(self):
        for key in self.hotkey_elements:
            self.hotkey_elements[key] = None
    def key_release_callback(self, event):
        key = str(event.keysym)
        
        if key.startswith("Alt"): self.hotkey_elements["alt"] = None
        if key.startswith("Control"): self.hotkey_elements["control"] = None
        if key.startswith("Shift"): self.hotkey_elements["shift"] = None
        
        
        #return "break"
    
    
    
    
    
    
    
    
    
    """
    callback when the text area is modified
    
    there is a weird glitch where whenever you type
    something or make a change, this callback is
    called twice. Every time, all the time. 
    So thus I just made a boolean variable 
    that flips from true to false (self.text_modify_callback_every_other)
    each time and only when it's false the 
    callback procedures will be executed, and 
    when its true they will be skipped.
    """
    
    def _text_modify_callback(self, event):
        
        text_area.tk.call(text_area._w, 'edit', 'modified', 0)#https://code.activestate.com/recipes/464635-call-a-callback-when-a-tkintertext-is-modified/
        
        
        self.text_modify_callback_every_other = not self.text_modify_callback_every_other
        if self.text_modify_callback_every_other: return
        
        
        self.text_modify_callback(event)
        
        
        
        
        
    #the actual callback procedure
    def text_modify_callback(self, event):
        
        self.unsaved_changes = True
        
        
        
    
        
        
    #when you want the text area to open a file
    def open_file(self, file_name):
        #save the previous file before moving to the next file
        #so that if i make sudden changes but the save timer doesnt go off
        #before switching files, i can still have those changes saved here
        #just before we load the new file
        if self.mode == "File":
            self.save()
        
        if file_name != None and not os.path.isfile(file_name):
            mb.showinfo(title="", message="The file " + file_name +  " appears to have been deleted or renamed. If it's renamed you can try reopening it again under the new name.")
            self.open_file(None)
            return
            
        
        
        
        self.currently_open_file = file_name
        
        
        
        
        #if the file is None then delete the text and make the text pane uneditable
        if self.currently_open_file == None:
            self.delete("1.0", "end -1 chars")
            self.freeze()
            self.mode = None
            return
        else:
            self.unfreeze()
        
        self.mode = "File"
        
        #read the file
        
        s = ""
        f = open(file_name, "r")
        for line in f:
            s += line
        self.opening_new_file_dont_immediately_save = True
        
        #delete the text of the old file
        self.delete("1.0", "end -1 chars")
        
        #insert the new text
        self.insert(tk.INSERT, s)
        
        if file_area.file_information[self.currently_open_file]["file_scroll_position"] != None:
            
            #print("setting to", file_area.file_information[self.currently_open_file]["file_scroll_position"])
            self.yview_moveto(file_area.file_information[self.currently_open_file]["file_scroll_position"])
        
        
        self.open_style_file()
        self.reset_text_colors()
        #debug
        """
        self.tag_add("a","1.0","2.0")
        self.tag_configure("a",background="yellow")
        print(self.tag_names(index=None))
        print(self.tag_ranges("a"))
        """
        #debug
        
        
        
        f.close()
    
    
            
            
        
    
    def step(self, counter):
        #print(self.tag_ranges("def"))
        if self.mode == "File":
            self.undo_manager_routine()
            
            
            #save the text scrollbar position to the file area's file information
            if self.currently_open_file != None:
                file_area.file_information[self.currently_open_file]["file_scroll_position"] = self.yview()[0]
            
            
            #deal with periodic saving
            clock = time.time()
            if self.opening_new_file_dont_immediately_save:
                self.unsaved_changes = False
                self.opening_new_file_dont_immediately_save = False
            if self.unsaved_changes and (self.last_save_time == None or clock - self.last_save_time > constants.save_time_duration):
                self.last_save_time = clock
                self.unsaved_changes = False
                self.save()
                
                
                
                
            #make sure that if it thinks control or alt or shift is being held down
            #but its actually was pressed down and then window deselected
            #then released and the release was never registered
            #it can still release those buttons after some time
            clock = time.time()
            for key in ["alt", "control", "shift"]:
                if self.hotkey_elements[key] != None and clock - self.hotkey_elements[key] > constants.maximum_time_you_can_hold_down_ctl_alt_shift_before_it_registers_not_held_down:
                    self.hotkey_elements[key] = None
        elif self.mode == "Terminal":
            if self.currently_open_file != None:
                new_terminal_output = terminal.get_text(self.currently_open_file)
                if new_terminal_output != self.get("1.0", "end -1 chars"):
                    self.delete("1.0","end")
                    self.insert("1.0", new_terminal_output)
                    self.see("end")
                    self.reset_text_colors()
                
                
        #execute the pending color reset
        if self.reset_text_colors_pending:
            if self.text_tokenizer == None:
                self.text_tokenizer = text_coloring.TextColoringAsync(self)
                
        if self.text_tokenizer != None:
            self.execute_reset_text_colors()
        
        self.line_numbers_area.line_numbers_update()
            
    #try to save the current open file if there is a file open
    def save(self):
        if self.mode in {None, "Terminal"}: return
        if self.currently_open_file != None:
            f = open(self.currently_open_file, "w")
            s = self.get("1.0", "end -1 chars")
            #print(str(self.opening_new_file_dont_immediately_save) + "saving" + repr(s))
            f.write(s)
            f.close()
        
    def freeze(self):
        self.configure(state="disabled")
        self.line_numbers_area.configure(state="disabled")
    def unfreeze(self):
        self.configure(state="normal")
        self.line_numbers_area.configure(state="normal")    
    def __len__(self):
        return len(self.get("1.0", "end -1 chars"))
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
    """
    Text coloring
    
    "Module"
    """
    
    
    
    
    
    def int_to_index(self, i):
        return "1.0 + " + str(i) + " chars"
    def get_appropriate_style_file(self):
    
        if self.currently_open_file == None: return None
        
        if self.mode == "Terminal":
            extension = "terminal"
        else:
            dot = self.currently_open_file.rfind(".")
            if dot == -1:
                extension = ""
            else:
                extension = self.currently_open_file[dot+1:]
        
        try:
            #also make it so that if multiple are selected, it makes only one selected
            style_files_of_this_type = []
            selected_style_file = None
            default_style_files = []
            selected_default_style_file = None
            
            for file in os.listdir(constants.style_file_folder):
                file = os.path.join(constants.style_file_folder, file)
                
                
                if file.endswith("." + extension + "_") or file.endswith("." + extension + "-"):
                    style_files_of_this_type.append(file)
                if file.endswith("." + extension + "_"):
                    if selected_style_file == None:
                        selected_style_file = file
                    else:
                        #uh oh, two files are selected aka 2 style files of this type end with underscore
                        os.rename(file, file[0:-1] + "-")
                    
                    
                    
                    
            for file in os.listdir(constants.style_file_folder):
                file = os.path.join(constants.style_file_folder, file)
                if file.endswith("._") or file.endswith(".-"):
                    default_style_files.append(file)
                if file.endswith("._"):
                    if selected_default_style_file == None:
                        selected_default_style_file = file
                    else:
                        #uh oh, two files are selected aka 2 style files of this type end with underscore
                        os.rename(file, file[0:-1] + "-")
                    
            if selected_style_file != None: return selected_style_file
            if len(style_files_of_this_type) != 0:
                #select the first style file of this type
                old_name = style_files_of_this_type[0]
                new_name = style_files_of_this_type[0][0:-1] + "_"
                os.rename(old_name, new_name)
                return new_name
            
            if selected_default_style_file != None: return selected_default_style_file
            if len(default_style_files) != 0:
                #select the first default style file
                old_name = default_style_files[0]
                new_name = default_style_files[0][0:-1] + "_"
                os.rename(old_name, new_name)
                return new_name
            else:
                #there are no style files of this type and there are also NO default style files
                #how we got here? Idk but let's create a default style file
                f = open(os.path.join(constants.style_file_folder, "DefaultDark._"), "w")
                f.write(constants.default_default_style_file_content)
                f.close()
                return os.path.join(constants.style_file_folder, "DefaultDark._")
            
            
            
        except Exception as e:
            mb.showerror(message=str(e))
            return None
    def open_style_file(self):
        self.style = {}
        self.enclosing_style = {}
        
        
        
        try:
            file = self.get_appropriate_style_file()
            if file == None: return
            f = open(file, "r")
            enclosing_styles = {}
            
            
            """
            #go through each line in the style file
            #the line should be formatted  like
            
            <token name/type> <R component> <G component> <B component>
            
            
            with exactly one space in between each part
            the token name just represents what word has a special color
            so for example in java the word public is a key word and gets
            a special color so lets say you want to color 'public' blue.
            So you would write
            
            public 0 0 255
            
            blue is 255 and the r and g are 0
            
            
            But there are also special token types that match not specific tokens
            but instead they color a wide variety of text components
                *default (colors any text that doesn't match any other rule)
                *background (colors the background of the text area)
                *highlight (when you select text, this specifies the highlight color)
                *caret (the color of the caret
                
            for example
            
            *default 0 0 0 
            
            
            
            But also theres tokens like strings so for example 
                print("hello world")
            "hello world" is a string and it's enclosed by two quotes
            
            There is a special syntax to define and color tokens that
            are enclosed by a special prefix and suffix (enclosing styles).
            In the case of "hello world", the prefix is the quote (")
            and the suffix is also the quote. So if I wanted the string
            to be colored green, i would write in the style file
            
            "`" 0 255 0
            
            the ` separates the prefix from the suffix, but notice the token
            type/name portion has no spaces inside it. Make sure that there
            are no spaces inside, because when we split the input line by
            space, it is hard coded so that the second token is the r, followed
            by g and b. so if your prefix or suffix includes spaces then ur out
            of luck
            
            
            so another example is a slash slash comment in java it's like
            
            public class MyClass//this is a comment
            
            
            so the prefix is "//" and the suffix is newline
            (\n is specially interpreted as the newline character
            with the style file interpreter)
            so you would write 
            
            //`\n
            
            
            ALSO. VERY IMPORTANT. Any character that directly follows a
            backslash cannot count as part of the closing token
            This is useful for strings like
            
            "john said \"hi\" "
            
            
            
            
            
            SO in this for loop, we take each line, split by " ",
            and then turn the last three tokens into a color,
            and then the first token is the token name/type.
            If the token is of the format <prefix>`<suffix>
            then it is added to self.enclosing_styles and other
            wise added to self.style
            
            
            """
            for line in f:
                try:
                    if line.strip() == "": continue
                    line = line.strip().split(" ")
                    color = self.get_color(line)
                    
                    if "`" in line[0]:
                        prefix_suffix = line[0].split("`")
                        prefix_suffix = (
                                            prefix_suffix[0].replace("\\n","\n"), 
                                            prefix_suffix[1].replace("\\n","\n")
                                            
                                            )
                        self.enclosing_style[prefix_suffix] = color
                    else:
                        self.style[line[0]] = color
                except Exception as e:
                    mb.showerror(message=str(e))
                    
            #sort the keys by longest to shortest prefix to ensure longer keys have precedence
            prefixes_suffixes = list(enclosing_styles.keys())
            prefixes_suffixes.sort(key = lambda x: -len(x[0]))
            self.enclosing_style_sorted_keys = prefixes_suffixes
                
                
            
        except Exception as e:
            mb.showerror(message=str(e))
    def get_color(self, style_file_line):
        l = style_file_line
        ret = "#"
        for i in range(1,4):
            hx = str(hex(int(l[i])))
            hx = hx[2:]
            if len(hx) == 1: hx = "0" + hx
            ret += hx
        return ret
    
    
    """
    call this to reset text colors in efficient way
    """
    def reset_text_colors(self):
        self.reset_text_colors_pending = True
        
    def execute_reset_text_colors(self):
        
        start = time.time()
        i=0
        while True:
            if self.text_tokenizer.step() == True:
                self.text_tokenizer = None
                return
            if i % 100 == 0:
                if time.time() - start > constants.color_reset_budgeted_time_per_step:return
            i+=1
              
    def remove_tags_range(self, start, end):
        if isinstance(start, int):
            start = self.int_to_index(start)
        if isinstance(end, int):
            end = self.int_to_index(end)
        for name in self.tag_names():
            if name != "sel":
                self.tag_remove(name, start, end)
    
    """
    Undo Manager
    """
    
    
    def undo(self):
        index = self.index("insert")
        if self.currently_open_file != None:
            self.try_save_undo_frame()
            file_info = file_area.file_information[self.currently_open_file]
            
            if file_info["current_undo_frame"] > 0:
                file_info["current_undo_frame"] -= 1
                #print(file_info["current_undo_frame"] )
                self.delete("1.0","end")
                self.insert("1.0",file_info["undo_log"][file_info["current_undo_frame"]])
        self.mark_set("insert", index)
    def redo(self):
        index = self.index("insert")
        if self.currently_open_file != None:
            self.try_save_undo_frame()
            file_info = file_area.file_information[self.currently_open_file]
            
            if file_info["current_undo_frame"] < len(file_info["undo_log"])-1:
                file_info["current_undo_frame"] += 1
                self.delete("1.0","end")
                self.insert("1.0",file_info["undo_log"][file_info["current_undo_frame"]])
    
        self.mark_set("insert", index)
    
    
    """
    Periodically executes try_save_undo_frame every
    min_time_between_undo_frames seconds
    
    """
    def undo_manager_routine(self):
        if self.currently_open_file != None:
            if self.last_undo_frame_save_time == None or time.time() - self.last_undo_frame_save_time > constants.min_time_between_undo_frames:
                self.try_save_undo_frame()
                
                
    """
    Assumes we have a currently open file
    
    If the last undo frame is not
    equal to the current text, this function will add
    another undo frame (at the end of the undo log) 
    so that the last undo frame 
    is equal to the text in the text area
    
    if the undo log is now too long, then it will remove the
    first (0th) element of the undo log
    
    
    
    
    But if the last from of the undo log is already equal
    to the current text then we will not make a new frame
    
    """
    def try_save_undo_frame(self):
        text = self.get("1.0", "end -1 chars")
        file_info = file_area.file_information[self.currently_open_file]
        if file_info["current_undo_frame"] == None:
            file_info["current_undo_frame"] = 0
            file_info["undo_log"].append(text)
            
        else:
            #if file_info["undo_log"][file_info["current_undo_frame"]] != text:
            if text not in file_info["undo_log"]:
                if file_info["current_undo_frame"] != len(file_info["undo_log"])-1:
                    del file_info["undo_log"][file_info["current_undo_frame"] + 1:]
                
                file_info["undo_log"].append(text)
                
                while len(file_info["undo_log"]) > constants.max_undo_log_length:
                    del file_info["undo_log"][0]
                
                
                file_info["current_undo_frame"] = len(file_info["undo_log"])-1
                
                
                
                self.last_undo_frame_save_time = time.time()
                
                #print(file_info["undo_log"])
                    
    
            
            
            
            
            
