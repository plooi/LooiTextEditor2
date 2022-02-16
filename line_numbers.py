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



class LineNumbers(tk.Text):
    def __init__(self, text_area_frame, **args):
        super().__init__(text_area_frame, **args)
        self.text_area_frame = text_area_frame
        self.text_area = None
        
        self.bind("<Button-3>", self.right_click_callback)
        self.bind("<KeyPress>", self.key_press_callback)
        
        
        self.menu = tk.Menu(text_area_frame, tearoff=0)
        self.menu.add_command(label = "Change Line Number Color", command = lambda:self.text_area.change_color("*linenumber"))
        
        
        
        self.line_numbers_update_in_progress = False
        self.i = -1
        self.num_lines = -1
        self.lines_str = None
        
    def line_numbers_update(self):
        #print(self.text_area.cget("width"))
        if not self.line_numbers_update_in_progress:
            self.line_numbers_update_in_progress = True
            self.i = 1
            self.num_lines = int(self.text_area.index('end').split('.')[0]) - 1
            self.lines_str = []
        
        
        start_time = time.time()
        while time.time() - start_time < constants.line_numbers_update_time_budget:
            code = self.consume_line()
            if code == 0:#code 0 means we're done with all lines. now set new lines string 
                #print("liens str",self.lines_str)
                lines_str = "\n".join(self.lines_str)
                #print(self.lines_str)
                
                
                old_lines_str = self.get("1.0", "end -1 chars")
                
                #print(self.yview())
                
                if old_lines_str != lines_str:
                    first,last = self.yview()
                    #self.configure(state="normal")
                    self.delete("1.0", "end")
                    self.insert("1.0", lines_str)
                    #self.configure(state="disabled")
                    self.yview("moveto", first)
                
                break
        
        
        
        
        
    def consume_line(self):
    
        if self.i >= self.num_lines+1: 
            self.line_numbers_update_in_progress = False
            return 0
        #print("i", self.i, "lines str",self.lines_str)
        remaining_lines = self.num_lines - self.i
        how_many_no_wrap = remaining_lines
        max_how_many_no_wrap = 5#1#5#10#20
        if how_many_no_wrap > max_how_many_no_wrap: how_many_no_wrap = max_how_many_no_wrap
        how_many_time_div_2 = 0
        while True:
            if how_many_no_wrap == 0: #this line is wrapping
                #print("a")
                break
            elif self.text_area.compare(str(self.i) + ".0 +" + str(how_many_no_wrap) + " lines", "==", str(self.i) + ".0 +" + str(how_many_no_wrap) + " display lines"):
                #print("b")
                
                self.lines_str += [str(x) for x in range(self.i, self.i + how_many_no_wrap)]
                self.i += how_many_no_wrap
                if self.i >= self.num_lines+1: 
                    self.line_numbers_update_in_progress = False
                    return 0
                #print("skipped", how_many_no_wrap, "divided",how_many_time_div_2)
                return
            else:
                #print("c")
                how_many_no_wrap = int(how_many_no_wrap/2)
                
                
                
                how_many_time_div_2 += 1
                
        
        
            
        
        self.lines_str.append(str(self.i))
        j = 1
        while True:
            if self.text_area.compare(str(self.i) + ".0 +1 lines", "==", str(self.i) + ".0 +" + str(j) + " display lines"):
                break
            else:
                self.lines_str.append("")
                
            j += 1
        self.i += 1
            
        
        
    def right_click_callback(self, event):
        if self.text_area.currently_open_file == None:return
        util.popup(self.menu)
    def key_press_callback(self, event):
        return "break"
