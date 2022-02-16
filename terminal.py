import tkinter as tk
import file_area
import text_area
import constants
import os
import tkinter.simpledialog as sd
import _thread as thread
import subprocess
import sys
import platform
import psutil
from util import split


terminal_instances = {}
default_execution_commands = None



def get_text(terminal_instance):
    if terminal_instance not in terminal_instances: return ""
    try:
        if not os.path.isfile(terminal_instances[terminal_instance]["output_file"]): return ""
        f = open(terminal_instances[terminal_instance]["output_file"], "r")
        s = []
        
        i=0
        for line in reverse_readline(f):
            s.append(line+"\n") 
            i+= 1
            if i >= constants.max_terminal_num_lines: break
        
        
        s.reverse()
        #if len(s) > 0 and s[-1].endswith("\n"):
        #    s[-1] = s[-1][0:-1]
        
        f.close()
        ret = "".join(s) #+ #terminal_instances[terminal_instance]["stdin_text"]
        
        return ret
        
    except Exception as e:
        print("bad" + str(e))
    return None



"""
From https://stackoverflow.com/questions/2301789/how-to-read-a-file-in-reverse-order
"""
def reverse_readline(fh, buf_size=8192):
    """A generator that returns the lines of a file in reverse order"""
    
    segment = None
    offset = 0
    fh.seek(0, os.SEEK_END)
    file_size = remaining_size = fh.tell()
    while remaining_size > 0:
        offset = min(file_size, offset + buf_size)
        fh.seek(file_size - offset)
        buffer = fh.read(min(remaining_size, buf_size))
        remaining_size -= buf_size
        lines = buffer.split('\n')
        # The first line of the buffer is probably not a complete line so
        # we'll save it and append it to the last line of the next buffer
        # we read
        if segment is not None:
            # If the previous chunk starts right from the beginning of line
            # do not concat the segment to the last line of new chunk.
            # Instead, yield the segment first 
            if buffer[-1] != '\n':
                lines[-1] += segment
            else:
                yield segment
        segment = lines[0]
        for index in range(len(lines) - 1, 0, -1):
            if lines[index]:
                yield lines[index]
    # Don't yield None if the file was empty
    if segment is not None:
        yield segment




def save_default_execution_commands(cmds):
    f = open(constants.default_execution_commands_file, "w")
    f.write(str(cmds))
    f.close()
def load_default_execution_commands():
    if not os.path.isfile(constants.default_execution_commands_file):
        save_default_execution_commands({})
        
        
    f = open(constants.default_execution_commands_file, "r")
    s = ""
    for line in f:
        if line.endswith("\n"):
            line = line[0:-1]
        s += line
    f.close()
    try:
        return eval(s)
    except Exception as e: 
        print(e)
        return {}
default_execution_commands = load_default_execution_commands()

#print(default_execution_commands)

exec_counter = 0#every run job gets a unique monotonically increasing number, which is kept track of here
    


"""
exec

Executed EVERYTHING that needs to happen in order to run a file (file
passed in as parameter). This includes adding an entry to the file
bar, creating an entry in the terminal_instances dictionary to keep
track of the running job, and actually starting the process
"""
def execute(file, external=False):
    global exec_counter
    if not os.path.isdir(constants.terminal_dir):
        os.mkdir(constants.terminal_dir)
    
    runtime_command = "echo 'i dont know how to run this file sorry'"
    directory,basename,extension = split(file)
    if file in default_execution_commands:
        runtime_command = default_execution_commands[file]
    else:
        
        extension_without_dot = extension[1:] if len(extension)>0 else ""
        
        if extension_without_dot in default_execution_commands:
            
            file_placeholder_with_extension = "<<<file" + extension + ">>>"
            file_placeholder_without_extension = "<<<file>>>"
            
            runtime_command = default_execution_commands[extension_without_dot].replace(
                file_placeholder_with_extension, basename + extension
            ). replace(file_placeholder_without_extension, basename)
            
    default_runtime_command = runtime_command
    runtime_command = sd.askstring(title="Run", prompt="\n\n\n" + " " * 20 + "Executing this command" + " " * 20 + "\n\n\n", initialvalue=runtime_command)
    if runtime_command==None:return
    
    if default_runtime_command != runtime_command:
        default_execution_commands[file] = runtime_command
        save_default_execution_commands(default_execution_commands)
    
    
    
    output_file = os.path.join(constants.terminal_dir, "run" + str(exec_counter) + ".txt")
    process_terminated_file = os.path.join(constants.terminal_dir, "finished" + str(exec_counter) + ".txt")
    
    
    
    
    
    if not external:
        runtime_command = "cd \"" + directory + "\" & (" + runtime_command + " ) > \"" + output_file  + '" 2>&1' + " & echo done > \"" + process_terminated_file + '"'
        
        
        terminal_instance_name = "*Run " + basename + extension + " <Run " + str(exec_counter) + ">"
        
        
        file_area.listbox.insert(0, terminal_instance_name)#adds the terminal instance to the file area
        
        text_area.text_area.open_terminal(terminal_instance_name)
        print("running " + runtime_command)
        process = subprocess.Popen(runtime_command, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
        
        
        
        terminal_instances[terminal_instance_name] = new_terminal_instance(terminal_instance_name,runtime_command, output_file, process_terminated_file, process.pid, process)
        #print("stdin is",process.stdin)
        
    else:
        runtime_command = "cd \"" + directory + "\" & cmd /c start cmd.exe /K " + runtime_command + " & pause"
        process = subprocess.Popen(runtime_command, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
    exec_counter += 1
def new_terminal_instance(terminal_instance_name, runtime_command, output_file, process_terminated_output_file, pid, process):
    
    
    instance = {
    "name" : terminal_instance_name,
    "command" : runtime_command,
    "output_file" : output_file,
    "pid" : pid,
    "process_terminated" : process_terminated_output_file,
    "process" : process,
    "can_write" : True
    
    }
    
    return instance



"""
This function called when any key or key 
combination is pressed when in terminal
mode


key is either a single key e.g. "a", "g", "x"
or it is a hotkey combination e.g. "control-c"

"""
def handle_key_press(key, terminal_name, char):
    terminal_instance = terminal_instances[terminal_name]
    if terminal_name != None:
        #if "+not in key"
        
        if key == "control+c":
            
            
            if "pid" in terminal_instance:
                if is_running(terminal_instance):
                    f = open(terminal_instance["process_terminated"], "w")
                    f.write("done")
                    f.close()
                    kill_proc_tree(terminal_instance["pid"])
                    subprocess.Popen("echo ctl+C >> \"" + terminal_instance["output_file"] + "\"", stdout=subprocess.PIPE, shell=True)
                    
                else:
                    print(terminal_instance["pid"], "is a terminal instance but process not running")
        """
        elif key == "return":
            if terminal_instance["can_write"]:
                terminal_instance["process"].stdin.write(terminal_instance["stdin_text"].encode())
                terminal_instance["process"].stdin.close()
                terminal_instance["can_write"] = False
                terminal_instance["stdin_text"] = ""
        else:
            
            if char != None:
                terminal_instance["stdin_text"] += char
        """
def is_running(terminal_instance):
    return not os.path.isfile(terminal_instance["process_terminated"])
    
        

"""
from https://www.semicolonworld.com/question/54124/subprocess-deleting-child-processes-in-windows
"""
def kill_proc_tree(pid, including_parent=True, timeout=2):    
    parent = psutil.Process(pid)
    children = parent.children(recursive=True)
    for child in children:
        try:
            child.kill()
        except:
            pass
    gone, still_alive = psutil.wait_procs(children, timeout=timeout)
    if including_parent:
        try:
            parent.kill()
        except:
            pass
        parent.wait(timeout)

def delete_terminal_instance(name):
    terminal_instance = terminal_instances[name]
    
    if is_running(terminal_instance):
        f = open(terminal_instance["process_terminated"], "w")
        f.write("done")
        f.close()
        kill_proc_tree(terminal_instance["pid"])
        print("deleted the terminal instance and killed the process")
    else:
        print(terminal_instance["pid"], "is a terminal instance but process not running. Deleting the terminal instance")
    
    del terminal_instances[name]
        
    

    
if not os.path.isdir(constants.terminal_dir):
    os.mkdir(constants.terminal_dir)
for file in os.listdir(constants.terminal_dir):
    os.remove(os.path.join(constants.terminal_dir, file))

