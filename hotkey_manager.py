import tkinter as tk
import constants
import tkinter.simpledialog as sd
import time
import tkinter.messagebox as mb


class HotkeyManager():
    def __init__(self, text_area):
        self.text_area = text_area
        self.hotkey_dictionary = {
            "control+i" : "insert",
            "control+backspace" : "delete_word",
            "control+z" : "undo",
            "control+y" : "redo",
            "shift+tab" : "shift_tab",
            "tab" : "tab",
            "control+q" : "quotes",
            "control+p" : "paren",
            "control+l" : "brackets",
            "control+n" : "java_indent",
            "control+b" : "bash_indent",
            "control+m" : "python_indent",
            "control+f" : "find",
            "control+comma" : "prev",
            "control+period" : "next",
            "control+e" : "clear",
            "control+r" : "find_and_replace"
            
        
        }
        self.conversion = {
            "insert" : self.insert,
            "undo" : self.undo,
            "redo" : self.redo,
            "delete_word" : self.delete_word,
            "shift_tab" : self.shift_tab,
            "tab" : self.tab,
            "quotes" : self.quotes,
            "paren" : self.paren,
            "brackets" : self.brackets,
            "java_indent" : self.java_indent,
            "bash_indent" : self.bash_indent,
            "python_indent" : self.python_indent,
            "find" : self.find,
            "prev" : self.prev,
            "clear" : self.clear,
            "next" : self.next,
            "find_and_replace" : self.find_and_replace,
        }
        self.find_table = []
        self.token_length = None
    
    def receive_hotkey(self, hotkey_string):
        if hotkey_string in {"control+c", "control+v", "control+a"}: return
        
        if hotkey_string in self.hotkey_dictionary:
            return self.conversion[self.hotkey_dictionary[hotkey_string]]()
            
            
            
    def insert(self):
        self.text_area.insert("1.0", "hello")
    def undo(self):
        self.text_area.undo()
    def redo(self):
        self.text_area.redo()
    def delete_word(self):
        char = self.text_area.get("insert -1 chars")
        if char in {" ", "\n", "\t", "\r"}:
            end_of_previous_word = self.text_area.find_previous("insert", constants.letters_and_numbers_caps_underscore)
            if end_of_previous_word == -1: end_of_previous_word = "0.0"
            start_of_previous_word = self.text_area.find_previous(end_of_previous_word, constants.letters_and_numbers_caps_underscore, complement=True)
            if start_of_previous_word == -1: start_of_previous_word = "0.0"
            else: start_of_previous_word += " +1 chars"
            self.text_area.delete(start_of_previous_word,"insert")
            return "break"
        elif char in constants.letters_and_numbers_caps_underscore:
            start_of_previous_word = self.text_area.find_previous("insert -1 chars", constants.letters_and_numbers_caps_underscore, complement=True)
            if start_of_previous_word == -1: start_of_previous_word = "0.0"
            else: start_of_previous_word += " +1 chars"
            self.text_area.delete(start_of_previous_word,"insert")
            return "break"
        else:
            self.text_area.delete("insert -1 chars")
            return "break"
    def shift_tab(self):
        if self.text_area.tag_ranges("sel"):
            selected_from_start = False
            last_nl = self.text_area.find_previous("sel.first", {"\n"})
            if last_nl == -1: 
                last_nl = "1.0"
                selected_from_start = True
            else:
                last_nl += " +1 chars"
            last_nl = self.text_area.index(last_nl)
            
            text = self.text_area.get(last_nl, "sel.last")
            number_of_removals = text.count("\n" + constants.tab)
            text = text.replace("\n" + constants.tab, "\n")
            if text.startswith(constants.tab):
                text = text[len(constants.tab):]
            
            self.text_area.delete(last_nl, "sel.last")
            self.text_area.insert(last_nl, text)
            self.text_area.tag_add(tk.SEL, last_nl, last_nl + " +" + str(len(text)) + " chars")
            return "break"
        else:
            
            if self.text_area.get("insert -4 chars", "insert") == constants.tab:
                #print("last 4 chrs are '" + self.text_area.get("insert -4 chars", "insert") + "'")
                original_insert = self.text_area.index("insert")
                new_insert = self.text_area.index("insert -4 chars")
                self.text_area.delete(original_insert + " -4 chars", original_insert)
                self.text_area.mark_set("insert", new_insert)
            return "break"
    def tab(self):
        if self.text_area.tag_ranges("sel"):
            selected_from_start = False
            last_nl = self.text_area.find_previous("sel.first", {"\n"})
            if last_nl == -1: 
                last_nl = "1.0"
                selected_from_start = True
            else:
                last_nl += " +1 chars"
            last_nl = self.text_area.index(last_nl)
            
            text = self.text_area.get(last_nl, "sel.last")
            number_of_removals = text.count("\n" + constants.tab)
            text = text.replace("\n", "\n" + constants.tab)
            text = "    " + text
            
            self.text_area.delete(last_nl, "sel.last")
            self.text_area.insert(last_nl, text)
            self.text_area.tag_add(tk.SEL, last_nl, last_nl + " +" + str(len(text)) + " chars")
            return "break"
        else:
            self.text_area.insert("insert", constants.tab)
            return "break"
            
    def quotes(self):
        original_insert = self.text_area.index("insert")
        self.text_area.insert(original_insert, "\"\"")
        self.text_area.mark_set("insert", original_insert + " +1 chars")
    def paren(self):
        original_insert = self.text_area.index("insert")
        self.text_area.insert(original_insert, "()")
        self.text_area.mark_set("insert", original_insert + " +1 chars")
    def brackets(self):
        original_insert = self.text_area.index("insert")
        self.text_area.insert(original_insert, "[]")
        self.text_area.mark_set("insert", original_insert + " +1 chars")
    def python_indent(self):
        original_insert = self.text_area.index("insert")
        n = self.text_area.find_next(original_insert, {"\n"})
        if n == -1: n = end
        insertion = ":\n" + " " * self.text_area.get_indent(original_insert) + constants.tab
        
        self.text_area.insert(n, insertion)
        self.text_area.mark_set("insert", n + " +" + str(len(insertion)) + "chars")
    def java_indent(self):
        original_insert = self.text_area.index("insert")
        n = self.text_area.find_next(original_insert, {"\n"})
        if n == -1: n = end
        insertion_first_part = (
                    "\n" + 
                    " " * self.text_area.get_indent(original_insert) + 
                    "{\n" + " " * self.text_area.get_indent(original_insert) + 
                    constants.tab)
        insertion_total = (insertion_first_part +
                    "\n" +
                    " " * self.text_area.get_indent(original_insert) + 
                    "}"
                    )
        
        self.text_area.insert(n, insertion_total)
        self.text_area.mark_set("insert", n + " +" + str(len(insertion_first_part)) + "chars")
    def bash_indent(self):
        original_insert = self.text_area.index("insert")
        n = self.text_area.find_next(original_insert, {"\n"})
        if n == -1: n = end
        insertion_first_part = (
                    "\n" + 
                    " " * self.text_area.get_indent(original_insert) + 
                    "do\n" + " " * self.text_area.get_indent(original_insert) + 
                    constants.tab)
        insertion_total = (insertion_first_part +
                    "\n" +
                    " " * self.text_area.get_indent(original_insert) + 
                    "done"
                    )
        
        self.text_area.insert(n, insertion_total)
        self.text_area.mark_set("insert", n + " +" + str(len(insertion_first_part)) + "chars")
    def find(self):
        self.text_area.release_all_hotkey_qualifiers()
        #print(self.text_area.tag_ranges(constants.find_text_tag))
        default_value = ""
        if "sel" in self.text_area.tag_names():
            ranges = self.text_area.tag_ranges("sel")
            if len(ranges) > 1:
                default_value = self.text_area.get(self.text_area.index(ranges[0]), self.text_area.index(ranges[1]))
        
        self.find_table = []
        self.text_area.tag_delete(constants.find_text_tag)
        self.text_area.tag_configure(constants.find_text_tag, background="#FFFF00", foreground="#000000")
        
        
        
        phrase = sd.askstring(title="Find", prompt= "\n\n\n" + " " * 50 + "Enter phrase to search for" + " " * 50 + "\n Use control_< and control_> to navigate to the next and previous\nPress control_e to clear the find results" , initialvalue=default_value)
        self.text_area.focus_set()
        if phrase == None: return
        
        
        
        text = self.text_area.get("1.0", "end -1 chars")
        length = len(text)
        self.token_length = len(phrase)
        text = text  + " " * len(phrase)
        
        for i in range(len(text)):
            if text[i:i+len(phrase)] == phrase:
                self.text_area.tag_add(constants.find_text_tag, self.text_area.int_to_index(i), self.text_area.int_to_index(i+len(phrase)))
                self.find_table.append(self.text_area.int_to_index(i))
                #print("added text_find at", (self.text_area.int_to_index(i), self.text_area.int_to_index(i+len(phrase))))
        
        
        
        
        #try to highlight the next or previous find
        
        for i in range(len(self.find_table)-1, -1, -1):
            if self.text_area.compare(self.find_table[i], "<", "insert"):
                self.text_area.see(self.find_table[i])
                self.text_area.mark_set("insert", self.find_table[i])
                self.text_area.tag_remove("sel", "1.0", "end")
                self.text_area.tag_add("sel", self.find_table[i], self.find_table[i] + " +" + str(self.token_length) + " chars")
                
        else:
            for i in range(len(self.find_table)):
                if self.text_area.compare(self.find_table[i], ">", "insert"):
                    self.text_area.see(self.find_table[i])
                    self.text_area.mark_set("insert", self.find_table[i])
                    self.text_area.tag_remove("sel", "1.0", "end")
                    self.text_area.tag_add("sel", self.find_table[i], self.find_table[i] + " +" + str(self.token_length) + " chars")
                    return
        
    def prev(self):
        self.text_area.hotkey_elements["control"] = time.time()
        for i in range(len(self.find_table)-1, -1, -1):
            if self.text_area.compare(self.find_table[i], "<", "insert"):
                self.text_area.see(self.find_table[i])
                self.text_area.mark_set("insert", self.find_table[i])
                self.text_area.tag_remove("sel", "1.0", "end")
                self.text_area.tag_add("sel", self.find_table[i], self.find_table[i] + " +" + str(self.token_length) + " chars")
                return
    def next(self):
        self.text_area.hotkey_elements["control"] = time.time()
        for i in range(len(self.find_table)):
            if self.text_area.compare(self.find_table[i], ">", "insert"):
                self.text_area.see(self.find_table[i])
                self.text_area.mark_set("insert", self.find_table[i])
                self.text_area.tag_remove("sel", "1.0", "end")
                self.text_area.tag_add("sel", self.find_table[i], self.find_table[i] + " +" + str(self.token_length) + " chars")
                return
    def clear(self):
        self.text_area.tag_delete(constants.find_text_tag)
        self.find_table = []
        
        
        
        
    def find_and_replace(self):
        self.text_area.release_all_hotkey_qualifiers()
        #print(self.text_area.tag_ranges(constants.find_text_tag))
        
        
        
        
        
        phrase = sd.askstring(title="Find", prompt= "\n\n\n" + " " * 25 + "Enter phrase to search for. Program will only search and replace in the selected text." + " " * 25 , initialvalue="")
        self.text_area.focus_set()
        if phrase == None: return
        replace = sd.askstring(title="Replace", prompt= "\n\n\n" + " " * 50 + "Enter phrase to replace with" + " " * 50 , initialvalue="")
        self.text_area.focus_set()
        if replace == None: return
        
        if "sel" not in self.text_area.tag_names() or len(self.text_area.tag_ranges("sel")) == 0:
            start = "1.0"
            end = "end -1 chars"
        else:
            start = self.text_area.tag_ranges("sel")[0]
            end = self.text_area.tag_ranges("sel")[1]
        
        text = self.text_area.get(start, end)
        number_of_replacements = text.count(phrase)
        text = text.replace(phrase,replace)
        
        self.text_area.delete(start, end)
        self.text_area.insert(start, text)
        
        mb.showinfo(title="", message="Made " + str(number_of_replacements) + " replacements")
        
        self.text_area.focus_set()
        self.text_area.reset_text_colors()
        
        
        
        
        
