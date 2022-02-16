import os
import pyautogui

def split(file_path):
    directory = os.path.dirname(file_path)
    extension = os.path.splitext(os.path.basename(file_path))[1]
    basename = os.path.splitext(os.path.basename(file_path))[0]
    return directory, basename, extension
def popup(menu):
    pos = pyautogui.position()
    menu.tk_popup(*pos)


