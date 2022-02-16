import constants


class TextColoringAsync:
    def __init__(self, text_area):
        self.text_area = text_area
        self.text = text_area.get("1.0", "end")
        self.length = len(self.text)
        self.text += " " * 10
        self.E = {}#existing tokens
        self.C = {}#the tokens we want to have
        self.T = {}#map from ("tag name", start index, end index) : token type
        self.tok_txt = {}
        self.stage = 0
        self.newlines = self.find_newlines(self.text)
        
        
        text_area.reset_text_colors_pending = False
        
        
        
        for name in self.text_area.tag_names():
            #print(self.text_area.tag_ranges(name))
            if name != "sel" and name != constants.find_text_tag:
                self.E[name] = set()
                index_double = []
                for textindex in self.text_area.tag_ranges(name):
                    index_double.append(self.text_area.index(textindex))
                    if len(index_double) >= 2:
                        self.E[name].add((index_double[0], index_double[1]))
                        index_double = []
                        
                
            
            
            
        
        self.i = -1
        self.token_start = None
        self.token_type = None
        self.skip = 0
        self.tokens = []
        
        
        self.tag_range_index = 0
        self.tag_name_index = -1
        self.tag_ranges = None
        self.tag_names = None
        
        
        
        
                
    def step(self):
        
        if self.stage == 0:
            
            for tag in self.text_area.style:
                if tag == "*background":
                    self.text_area.config(bg=self.text_area.style[tag])
                    self.text_area.line_numbers_area.config(bg=self.text_area.style[tag])
                elif tag == "*default":
                    self.text_area.config(fg=self.text_area.style[tag])
                    self.text_area.line_numbers_area.config(fg=self.text_area.style[tag])
                elif tag == "*highlight":
                    if "*background" in self.text_area.style:
                        self.text_area.tag_configure("sel", background=self.text_area.style[tag], foreground=self.text_area.style["*background"])
                        
                    else:
                        self.text_area.tag_configure("sel", background=self.text_area.style[tag])
                    
                elif tag == "*caret":
                    self.text_area.config(insertbackground=self.text_area.style[tag])
                elif tag == "*linenumber":
                    self.text_area.line_numbers_area.config(fg=self.text_area.style[tag])
                else:
                    self.text_area.tag_configure(tag, foreground=self.text_area.style[tag])
            
            for prefix,suffix in self.text_area.enclosing_style:
                self.text_area.tag_configure(prefix+"`"+suffix, foreground=self.text_area.enclosing_style[prefix,suffix])
            self.stage = 1
            #print("stage 1")
            
        elif self.stage == 1:
            for z in range(20): #consume 20 characters on each function call so we dont waste so much time calling and uncalling
                self.i += 1 
                
                i = self.i
                #print(i)
                if i >= self.length: 
                    self.stage = 2
                    self. i = 0
                    self.tag_names = list(self.E.keys())
                    return 
                
                """
                sometimes, when you approach the end of the token, you are able
                to recognize the end of the token before you actually get there.
                Like this comment is in a triple quotation thingy so if we were
                to get to the first quote of the closing triple quote we can just check that the next two
                are also quotes, and if the next two are also quotes then we can
                deduce that this is the end of the triply quotation comment token
                thing and then we can yield that token to the calling function.
                However, the problem is that the algorithm is going to immediately
                look for the start of the next token right here which is not good
                because it will see the quotes which we are currently indexed at
                and it's gonna think that another triple quote is starting right now.
                So if you set skip_token_start_code to true then the algorithm
                will skip the part where it looks for the start of a token right
                here, and we'll move onto the next token. However, since the next two
                are also quotes we probably want to skip over those as well because those
                quotes have already been accounted for as the closing of this triple
                quote comment. So, if you set skip = 2 you can tell the algorithm to
                skip the next two characters
                """
                skip_token_start_code = False
                
                if self.skip > 0:
                    self.skip -= 1
                    continue
                    #return 
                
                text = self.text
                len_text = len(text)
                char = text[i]
                
                
                
                #here is where we recognize the ends of tokens and 
                #transition to the next token by setting token_start to None
                if self.token_start != None:
                    if self.token_type == "alphanumeric":
                        if char in constants.letters_and_numbers_caps_underscore:
                            pass
                        else:
                            self.add_to_C_T_txt(self.token_start, i , self.token_type)
                            #self.text_area.autofill.add_token(self.token_start, i, text[self.token_start:i])
                            self.token_start = None
                    elif self.token_type == "*number":
                        if char in constants.letters_and_numbers_caps_underscore or char == ".":
                            pass
                        else:
                            self.add_to_C_T_txt(self.token_start, i , self.token_type)
                            self.token_start = None
                    elif self.token_type == "symbol":
                        self.add_to_C_T_txt(self.token_start, i , self.token_type)
                        self.token_start = None
                    
                    elif isinstance(self.token_type, tuple):
                        suffix = self.token_type[1]
                        if text[i: i+len(suffix)] == suffix:
                            self.add_to_C_T_txt(self.token_start, i + len(suffix) , self.token_type)
                            self.token_start = None
                            skip_token_start_code = True
                            self.skip = len(suffix) - 1
                    
                    
                #here is where we recognize the beginnings of tokens
                #ALSO Here is where all the token types are defined
                if self.token_start == None and not skip_token_start_code:
                    
                    if char != " " and char != "\n" and char != "\r" and char != "\t":
                        if char in constants.numbers or (char == "." and text[i+1] in constants.numbers):
                            self.token_start = i
                            self.token_type = "*number"
                        elif char in constants.letters_and_numbers_caps_underscore:
                            self.token_start = i
                            self.token_type = "alphanumeric"
                        else:
                            for prefix,suffix in self.text_area.enclosing_style:
                                if text[i:i+len(prefix)] == prefix:
                                    self.token_start = i
                                    self.token_type = (prefix,suffix)
                                    self.skip = len(prefix) - 1
                                    
        elif self.stage == 2:
            
            if self.tag_name_index == -1:
                self.tag_name_index = 0
                self.tag_range_index = 0
                self.tag_names = list(self.E.keys())
                
                #print(self.E, "-------",self.C)
                
                
                
            
            if self.tag_name_index < len(self.E):
                if self.tag_range_index == 0:
                    self.tag_ranges = list(self.E[self.tag_names[self.tag_name_index]])
                    
                
                if self.tag_range_index < len(self.tag_ranges):
                    tag_name = self.tag_names[self.tag_name_index]
                    r = self.tag_ranges[self.tag_range_index]
                    if tag_name not in self.C or r not in self.C[tag_name]:
                        self.text_area.tag_remove(tag_name, r[0], r[1])
                        #print("deleting", tag_name, r)
                    self.tag_range_index += 1
                else:
                    self.tag_range_index = 0
                    self.tag_name_index += 1
            else:
                self.tag_name_index = -1
                self.tag_range_index = 0
                self.tag_names = list(self.C.keys())
                self.stage = 3
                return
                
                    
                
        elif self.stage == 3:
            
            if self.tag_name_index == -1:
                self.tag_name_index = 0
                self.tag_range_index = 0
                self.tag_names = list(self.C.keys())
                #print("adding start")
                
                
                
            
            if self.tag_name_index < len(self.C):
                if self.tag_range_index == 0:
                    self.tag_ranges = list(self.C[self.tag_names[self.tag_name_index]])
                    
                
                if self.tag_range_index < len(self.tag_ranges):
                    tag_name = self.tag_names[self.tag_name_index]
                    r = self.tag_ranges[self.tag_range_index]
                    if tag_name not in self.E or r not in self.E[tag_name]:
                        self.text_area.tag_add(tag_name, r[0], r[1])
                    self.tag_range_index += 1
                else:
                    self.tag_range_index = 0
                    self.tag_name_index += 1
            else:
                return True
            
            
            
            
                
    def add_to_C_T_txt(self, token_start, token_end, token_type):
        token_text = self.text[token_start:token_end]
        tag_name = self.find_tag_name(token_text, token_type)
        if tag_name == None: return
        indices = self.generate_text_indices(token_start,token_end)
        #print("indices for ",token_text, indices)
        
        if tag_name not in self.C: self.C[tag_name] = set()
        self.C[tag_name].add(indices)
        self.T[(tag_name, indices[0], indices[1])] = token_type
        self.tok_txt[(tag_name, indices[0], indices[1])] = token_text
        
    
    
    def find_tag_name(self, token_text, token_type):
        if token_type == "alphanumeric" or token_type == "symbol":
            if token_text in self.text_area.style:
                return token_text
        
        elif token_type in self.text_area.style:
            return token_type
        elif token_type in self.text_area.enclosing_style:
            return token_type[0] + "`" + token_type[1]
        else:
            return None
    def generate_text_indices(self, token_start, token_end):
        return (self.convert_to_text_index(token_start), self.convert_to_text_index(token_end))
    def convert_to_text_index(self, i):
        if i >= self.length: return "end"
        newlines = self.newlines
        #binary search
        max = len(newlines)-1
        min = 0
        while True:
            
            mid = int((max + min)/2)
            
            if newlines[mid] < i and (mid+1 >= len(newlines) or newlines[mid+1] >= i):
                line_of_i = mid + 1
                break
            elif newlines[mid] < i:
                min = mid
            elif newlines[mid] >= i:
                max = mid
            else:
                raise ("wtf?")
            
            
        
        
        position = i - newlines[line_of_i-1] - 1
            
        return str(line_of_i) + "." + str(position)
            
        
        
        
        
        
        
    def find_newlines(self, text):
        ret = [-1]
        for i in range(len(text)):
            if text[i] == "\n":
                ret.append(i)
        return ret

def main():
    class Dummy():
        def __init__(self):
            pass
        def get(self, a, b):
            return "fdsklfjkdsjflk\ndslkfjlkdsjf\ndskljfkldsjf\n"
        def tag_names(self):
            return []
            
            
    t = TextColoringAsync(Dummy())
    print(t.convert_to_text_index(40))
if __name__ == "__main__": main()
