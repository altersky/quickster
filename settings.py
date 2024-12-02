help_text='''
  Control+F1 - Maximize program from tray
  Control+a - Add a new entry (Navigate between fields using Enter)
  Control+e - Edit an existing entry
  Control+o - Open a link (the entry must be of link type and contain a link in the content. 
  Alternatively, copy the file content to the clipboard (the file must be located in .\\files\\filename, 
  and the filename must be specified in the entry content))
  Shift+Delete - Delete entry

  Tags can be added by separating them with the # symbol for searching as well.
  You can print #- to exclude entry with this tag

  You can navigate between the input field and the list using the up and down keys.

  While in the list, you can start typing a tag or delete a tag using backspace'''

# DB name
dbname='quickster.db'

# Color of list entry background
link_color='#4588fc'
text_color='#FFCC33'
file_color='#99CC99'

# Defines if main window is always on top
topmost_value = True

# Defines functional key for all hotkeys. 0x004 is <Control>
functional_key = 0x0004

# shortcuts for keys to do any function in program (codes are used, so that latin and cyrillic keys both work)
add_record_key = 65 # a
edit_record_key = 69 # e
copy_record_key = 67 # c
help_key = 72 # h
open_key = 79 # o

#icon = 'favicon.ico'
icon = 'favicon.ico'
#search_entry_width = 64
search_entry_width = 70
#search_entry_font_size = 16
search_entry_font_size = 16
#tags_width = 100
tags_width = 200
#content_width = 500
content_width = 750
#tree_height = 26
tree_height = 28
#initial_width = 600
initial_width = 800
#initial_height = 500
initial_height = 600
#add_record_tags_width = 58
record_tags_width = 58
#add_record_combobox_width = 55
record_combobox_width = 55
#add_record_content_width = 44
record_content_width = 44
#help_window_width
help_window_width=850
#help_window_height
help_window_height=270

# telegram backup settings
bot_token = 'your_bot_token'
chat_id = 'your_chat_id'

# Backup parameters
file_to_archive = dbname # archive name
time_from_bu = 18 # From which hour backup to telegram
time_to_bu = 19 # To which hour backup to telegram

# To do or not to do telegram backup
do_tlgrm_backup = True