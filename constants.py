
import os
button_padding = 5
button_size = 40
file_area_width = 18
file_area_character_limit = 17
file_area_path_index = 100#the index in the file button string where the full path is located

#file area colors
file_area_foreground = "#555555"
file_area_background = "#DDDDDD"
file_area_select_foreground = "Black"
file_area_select_background = "White"
file_area_font = ("Helvetica",14,"")



#text saving
save_time_duration = 5#minimum how many seconds between saves so we don't keep spamming the save file operation
#which would slow down system
open_file_log = "./open_files"





game_loop_frame_time = 50 #milliseconds



#text typing properties
enter_respects_indent = True
letters_and_numbers = [chr(x) for x in range(97,123)] + [str(x) for x in range(0,10)] 
letters_and_numbers_caps_underscore = [chr(x) for x in range(65,91)] + [chr(x) for x in range(97,123)] + [str(x) for x in range(0,10)] + ["_"]
letters_and_numbers_caps_underscore = set(letters_and_numbers_caps_underscore)

hotkey_keys = letters_and_numbers + ["equal", "minus", "backspace", "tab", "period", "comma"]
typeable_keys = set.union(letters_and_numbers_caps_underscore, 
{"+", "=", "Return", "Space",
"Return",
"backslash",
"bar",
"BackSpace",
"plus",
"equal",
"minus",
"parenright",
"parenleft",
"asterisk",
"ampersand",
"asciicircum",
"percent",
"dollar",
"numbersign",
"at",
"exclam",
"asciitilde",
"quoteleft",
"Up","Down","Left","Right"

})


numbers = set([str(x) for x in range(0,10)])
tab = "    "
caret_blink_off_time = 500
caret_blink_on_time = 500

#undo stuff
min_time_between_undo_frames = 2
max_undo_log_length = 50

style_file_folder = "./styles"
color_reset_budgeted_time_per_step = .025
line_numbers_update_time_budget = .025


num_shift_keys_conversion = {

"exclam" : "1",
"at" : "2",
"numbersign" : "3",
"dollar" : "4",
"percent" : "5",
"asciicircum" : "6",
"ampersand" : "7",
"asterisk" : "8",
"parenleft" : "9",
"parenright" : "0",
"underscore" : "minus",
"plus" : "equal"

}



maximum_time_you_can_hold_down_ctl_alt_shift_before_it_registers_not_held_down = 12#seconds
terminal_dir = os.path.join(os.getcwd(), "runs")


default_execution_commands_file = "./cmd.txt"
max_terminal_num_lines = 500
process_terminated_special_sequence = "+-------------------Finished-------------------+"#"<<<<<<PROCESS~~~```~~~TERMINATED>>>>>>"


default_default_style_file_content = """
*default 255 255 255
*background 50 51 55
*highlight 184 207 229
*caret 255 255 255
"""
line_numbers_area_width = 4
token_clearing_block_range = 13000
settings_file = "./settings.txt"

find_text_tag = "*text_find"
