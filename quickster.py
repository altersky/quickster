import sqlite3, webbrowser, pystray, keyboard, threading, requests, zipfile, os, time
import tkinter as tk
import tkinter.font as tkFont
from tkinter import messagebox, ttk
from PIL import Image, ImageDraw
from datetime import datetime
from settings import *


# Function to initialize the database
def init_db():
    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS records (
            id TEXT PRIMARY KEY,
            tags TEXT,
            type TEXT,
            content TEXT,
            FOREIGN KEY(type) REFERENCES rec_types(id)
        )
    ''')
    # Create rec_types table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS rec_types (
        id TEXT PRIMARY KEY,
        desc TEXT
        )
    ''')
    # Insert data to rec_types
    cursor.execute('''
    INSERT OR REPLACE INTO rec_types (id, desc) values('link','Link');
    ''')
    # Insert data to rec_types
    cursor.execute('''
    INSERT OR REPLACE INTO rec_types (id, desc) values('text','Text field');
    ''')
    # Insert data to rec_types
    cursor.execute('''
    INSERT OR REPLACE INTO rec_types (id, desc) values('file','File');
    ''')
    conn.commit()
    conn.close()

# Function to display all records
def display_all_records():
    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()
    cursor.execute("SELECT id, tags, type, content FROM records")
    records = cursor.fetchall()
    conn.close()
    return records

# Function to update the list of records based on the entered tags
def update_treeview(event=None):
    tree.delete(*tree.get_children())  # delete all Treeview records
    global data
    tags_input = entry_search.get().strip()
    tags = [tag.strip() for tag in tags_input.split('#') if tag]  
    if tags:
        records = search_records(tags)
    else:
        records = display_all_records()

    data = records  # Save records to use it later with deletion

    for record in records:
        # Add record to Treeview, saving id in tags
        tree.insert("", tk.END, values=(record[0], record[1], record[2], record[3]))

    # Set colors for existing elemnts
    for i, item in enumerate(tree.get_children()):
        record_type = tree.item(item)['values'][2]  # Get content from record
        if record_type == 'link':
            color = link_color
        elif record_type == 'text':
            color = text_color
        else:
            color = file_color
        tree.item(item, tags=(color,))  # Set background color

    tree.tag_configure(text_color, background=text_color)
    tree.tag_configure(link_color, background=link_color)
    tree.tag_configure(file_color, background=file_color)

# Function to open a file or link
def open_link(event=None):
    selected_item = tree.selection()  # Get chosen line
    row_type = tree.item(selected_item, "values")[3]  # Get id from tags
    if row_type == 'link':
        if selected_item:  # Check if recoed is selected
            item = tree.item(selected_item)  # Get data from selected element
            link = item['values'][2]  # link is in column with index=2
            if link:  # Check that link contain something
                webbrowser.open(link)  # Open link in browser
                hide_window()
            else:
                messagebox.showwarning("Warning", "There is no link")
    elif row_type == 'file':
        # Get filename from 3d column with index=2
        file_name = tree.item(selected_item, "values")[2]
        file_path = f'files/{file_name}'  # Form relative path to file
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as file:
                file_content = file.read()
                root.clipboard_clear()  # Clear clipboard
                root.clipboard_append(file_content)  # Add text to clipboard
                root.update()  # Update clipboard state
        except Exception as e:
            messagebox.showwarning(f'File read error: {e}')
    else:
        messagebox.showwarning("Warning", "Record type must be 'link' or 'file'")

# Function to copy the content of the selected record
def copy_selected():
    selected_item = tree.selection()
    if selected_item:
        record_content = tree.item(selected_item)['values'][2]  # Get record content
        root.clipboard_clear()  
        root.clipboard_append(record_content)  

# Function to delete the selected record
def delete_record():
    selected_item = tree.selection()
    if selected_item:
        # Extract record ID, which is stored in hidden column
        record_id = tree.item(selected_item, "values")[0]  # Get id from tag

        if messagebox.askyesno("Confirmation", "Are you sure you want to delete record?"):
            conn = sqlite3.connect(dbname)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM records WHERE id=?", (record_id,))
            conn.commit()
            conn.close()
            update_treeview()
            entry_search.focus_set()  # Set focus on entry
    else:
        messagebox.showwarning("Warning", "Choose record to delete")

# Function to open the window
def show_window():
    root.deiconify()  
    root.lift()  
    root.attributes("-topmost", topmost_value)  
    root.focus_force()  
    entry_search.focus_set()

# Key press handler
def handle_keypress(event):
    key_code = event.keycode  # Get keystroke code
    # Check if Ctrl button is pressed
    if event.state & functional_key:
        if key_code == add_record_key:  # Check if <a> button pressed
            add_record()
            return "break"
        elif key_code == open_key: # Check if <o> buttin pressed
            open_link()
            hide_window()
            return "break"
        elif key_code == help_key: # Check if <h> buttin pressed
            open_help()
            return "break"
        elif key_code == edit_record_key: # Check if <e> buttin pressed
            edit_record()
            return "break"
        elif key_code == copy_record_key: # Check if <c> buttin pressed
            copy_selected()
            hide_window()
            return "break"

    # Move from entry to list
    if entry_search.focus_get() == entry_search:
        if event.keysym == 'Down':
            # Set focus on first list element
            tree.focus_set()
            # Mark first element
            first_item = tree.get_children()[0]
            tree.selection_set(first_item)
            tree.see(first_item)
            return "break"  # Stop event handling
        elif event.keysym == 'Up':
            return "break" 

    # "Down" and "Up" handling
    elif tree.focus_get() == tree:
        if event.keysym == 'Down':
            selected_item = tree.selection()
            if selected_item:
                # Get index from current element
                index = tree.index(selected_item[0])
                # Check if there is next element
                if index < len(tree.get_children()) - 1:
                    next_item = tree.get_children()[index + 1]
                    tree.selection_set(next_item)
                    tree.see(next_item)
                return "break"
        elif event.keysym == 'Up':
            selected_item = tree.selection()
            if selected_item:
                # Get index for current element
                index = tree.index(selected_item[0])
                # Check if there previous element
                if index > 0:
                    prev_item = tree.get_children()[index - 1]
                    tree.selection_set(prev_item)
                    tree.see(prev_item)
                else:
                    # Return focus on entry
                    entry_search.focus_set()
                return "break"


        elif event.keysym == "BackSpace":
            # Set focus on entry
            entry_search.focus_set()
            # Delete last symbol form entry
            current_text = entry_search.get()
            if current_text:  # Check if entry is empty
                entry_search.delete(len(current_text) - 1)  # Delete last symbol
            return "break"


        else:
            # If any other symbol entered
            if len(event.keysym) == 1:  # Check if it is a symbol
                entry_search.focus_set()  # Set focus on entry
                entry_search.insert(tk.END, event.char)  # Add character in the end of line
                return "break"

# Function to edit the selected record
def edit_record(event=None):
    selected_item = tree.selection()[0]
    selected_id = tree.item(selected_item, "values")[0]
    print(selected_item)
    def save_record(event=None):
        tags = entry_tags.get()
        content = entry_content.get("1.0", tk.END).strip()
        record_type = combo_type.get()  # Get selected record type

        if tags and content and record_type:  # Check if all fields are filled
            conn = sqlite3.connect(dbname)
            cursor = conn.cursor()
            # Refresh table record
            cursor.execute("UPDATE records SET tags = ?, content = ?, type = ? WHERE id = ?", 
                           (tags, content, record_type, selected_id))
            conn.commit()
            conn.close()
            edit_window.destroy()  
            update_treeview()
            entry_search.focus_set()  # Set focus to entry
        else:
            messagebox.showwarning("Warning", "Fill all the fields")

    def on_tags_enter(event):
        combo_type.focus_set() 

    def on_type_enter(event):
        entry_content.focus_set()

    # Create new window
    edit_window = tk.Toplevel()
    edit_window.title("Edit record")
    edit_window.iconbitmap(icon)  # Set empty bitmap

    # Create widgets
    label_tags = tk.Label(edit_window, text="Tags:")
    entry_tags = tk.Entry(edit_window, width=record_tags_width)
    label_type = tk.Label(edit_window, text="Record type:")
    
    # Create drop-down list to choose record type
    combo_type = ttk.Combobox(edit_window, width=record_combobox_width) 
    label_content = tk.Label(edit_window, text="Content:")
    entry_content = tk.Text(edit_window, wrap=tk.WORD, height=10, width=record_content_width)

    # Locate widgets
    label_tags.grid(row=0, column=0, padx=10, pady=10, sticky='w')
    entry_tags.grid(row=0, column=1, padx=10, pady=10, sticky='w')
    label_type.grid(row=1, column=0, padx=10, pady=10, sticky='w')
    combo_type.grid(row=1, column=1, padx=10, pady=10, sticky='w')
    label_content.grid(row=2, column=0, padx=10, pady=10, sticky='w')
    entry_content.grid(row=2, column=1, padx=10, pady=10)

    # Get current database record
    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()
    cursor.execute("SELECT tags, content, type FROM records WHERE id = ?", (selected_id,))
    record = cursor.fetchone()
    conn.close()


    # Fill drop-down list with rec_types table records
    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM rec_types")
    types = cursor.fetchall()
    combo_type['values'] = [t[0] for t in types]  # Extract type id
    conn.close()


    if record:
        entry_tags.insert(0, record[0])  # Fill with tags
        entry_content.insert("1.0", record[1])  # Fill with content
        combo_type.set(record[2])  # Set record type

    # Bind <Enter> press event
    entry_tags.bind('<Return>', on_tags_enter)
    combo_type.bind('<Return>', on_type_enter)
    entry_content.bind('<Return>', save_record)
    edit_window.bind("<Escape>", lambda event: edit_window.destroy())
    entry_tags.focus_set()

# Function to add a new record
def add_record(event=None):
    def save_record(event=None):
        tags = entry_tags.get()
        content = entry_content.get("1.0", tk.END).strip()
        record_type = combo_type.get()  # Get selected record type

        if tags and content and record_type:  # Check if all fields are filled
            current_timestamp = datetime.now().strftime('%d-%m-%yT%H:%M:%S')
            conn = sqlite3.connect(dbname)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO records (id, tags, content, type) VALUES (?, ?, ?, ?)", 
                           (current_timestamp, tags, content, record_type))
            conn.commit()
            conn.close()
            add_window.destroy()  
            update_treeview()
            entry_search.focus_set()
        else:
            messagebox.showwarning("Warning", "Fill all the fields")

    def on_tags_enter(event):
        combo_type.focus_set()  # Change focus

    def on_type_enter(event):
        entry_tags.focus_set()  # Change focus


    # Create new window
    add_window = tk.Toplevel()
    add_window.title("Add record")
    add_window.iconbitmap(icon) 

    label_content = tk.Label(add_window, text="Content:")
    entry_content = tk.Text(add_window, wrap=tk.WORD, height=10, width=record_content_width)
    
    # Creare drop-down widget for record type
    label_type = tk.Label(add_window, text="Record tpe:")
    combo_type = ttk.Combobox(add_window, values=["text", "link", "file"], width=record_combobox_width)
    combo_type.current(0)  # Set "text" as defaul value

    # Create tag widget
    label_tags = tk.Label(add_window, text="Tags:")
    entry_tags = tk.Entry(add_window, width=record_tags_width)

    label_content.grid(row=0, column=0, padx=10, pady=10, sticky='w')
    entry_content.grid(row=0, column=1, padx=10, pady=10)

    label_type.grid(row=1, column=0, padx=10, pady=10, sticky='w')
    combo_type.grid(row=1, column=1, padx=10, pady=10, sticky='w')

    label_tags.grid(row=2, column=0, padx=10, pady=10, sticky='w')
    entry_tags.grid(row=2, column=1, padx=10, pady=10, sticky='w')
    

    # Fill dropdown list with data from rec_types table
    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM rec_types")
    types = cursor.fetchall()
    combo_type['values'] = [t[0] for t in types]
    conn.close()

    # Bind <Enter> keypress events
    entry_content.bind('<Return>', on_tags_enter)
    combo_type.bind('<Return>', on_type_enter)
    entry_tags.bind('<Return>', save_record)
    add_window.bind("<Escape>", lambda event: add_window.destroy())

    entry_content.focus_set()

# Function to search data in the database by tags
def search_records(tags):
    positive_tags = []
    negative_tags = []

    for tag in tags:
        if tag.startswith('-'):
            # Remove '-' and add to negative list
            negative_tags.append(tag[1:])
        else:
            # Add to positive list
            positive_tags.append(tag)

    # Form initial SQL query
    sql_query = "SELECT id,tags,type,content FROM records WHERE "
    
    # Add positive conditions
    if positive_tags:
        sql_query += " AND ".join([f"tags LIKE '%{tag}%'" for tag in positive_tags])

    # Add negative conditions
    if negative_tags:
        if positive_tags:
            sql_query += " AND "  # Add AND if there are positive conditions
        sql_query += " AND ".join([f"tags NOT LIKE '%{tag}%'" for tag in negative_tags])

    conn = sqlite3.connect(dbname)
    cursor = conn.cursor()
    cursor.execute(sql_query)
    records = cursor.fetchall()
    conn.close()

    return records

# Function to open help
def open_help():
    help_window = tk.Toplevel(root)
    help_window.title("Instruction")
    center_window(help_window,help_window_width,help_window_height)
    help_window.iconbitmap(icon)

    text_area = tk.Text(help_window, wrap=tk.WORD)
    text_area.pack(expand=True, fill=tk.BOTH)

    # Insert help text
    text_area.insert(tk.END, help_text)

    # Turn off text edit
    text_area.configure(state='disabled')
    
    help_window.bind("<Escape>", lambda event: help_window.destroy())

    help_window.attributes("-topmost", topmost_value)  
    help_window.focus_set()

# Function to center the window on the screen
def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()  
    screen_height = window.winfo_screenheight()  
    x = (screen_width // 2) - (width // 2)  
    y = (screen_height // 2) - (height // 2)  
    window.geometry(f'{width}x{height}+{x}+{y}')  

# Function to create an icon in the system tray
def create_tray_icon():
    icon = pystray.Icon("test_icon", create_image(), "quickster", menu=pystray.Menu(
        pystray.MenuItem("Open", show_window),
        pystray.MenuItem("Exit", exit_program)
    ))
    icon.run()

# Function to create the icon image
def create_image():
    width = 64
    height = 64
    image = Image.new('RGB', (width, height), (255, 255, 255))
    dc = ImageDraw.Draw(image)
    dc.rectangle([width // 4, height // 4, width * 3 // 4, height * 3 // 4], fill=(0, 0, 255))
    return image

# Function to exit the program
def exit_program(icon, item):
    icon.stop()
    root.quit()

# Function to minimize the window to the tray
def hide_window(event=None):
    root.withdraw()
    return "break"  

# Launch icon in system tray in seperate thread
def run_tray():
    create_tray_icon()

# Function to send a file to Telegram
def send_file_to_telegram(file_path, bot_chat_id, token):
    folder_to_archive = 'files'
    current_date = datetime.now().strftime('%d%m%y')
    archive_name = f'quickster_bu_{current_date}.zip'

    # Check if file and folder exist
    if os.path.isfile(file_to_archive) and os.path.isdir(folder_to_archive):
        with zipfile.ZipFile(archive_name, 'w') as archive:
            archive.write(file_to_archive, os.path.basename(file_to_archive))
            
            # Add folder content recursivly
            for foldername, subfolders, filenames in os.walk(folder_to_archive):
                for filename in filenames:
                    file_path = os.path.join(foldername, filename)
                    # Add file to archive
                    archive.write(file_path, os.path.relpath(file_path, os.path.dirname(folder_to_archive)))

    url = f"https://api.telegram.org/bot{token}/sendDocument"
    with open(archive_name, 'rb') as file:
        response = requests.post(url, files={'document': file}, data={'chat_id': bot_chat_id})
    
    os.remove(archive_name)

# Function to back up to Telegram
def backup_to_tlgrm():
    while True:
        now = datetime.now()
        if time_from_bu <= now.hour < time_to_bu:
            send_file_to_telegram(file_to_archive, chat_id, bot_token)
            time.sleep(7200)
        else:
            time.sleep(600)  # Wait 10 mins for next check

# Function to check if files folder exists
def ensure_files_directory():
    if not os.path.exists('files'):
        os.makedirs('files')

# Initialize the database
init_db()

# Create main window
root = tk.Tk()
root.overrideredirect(True)  # Remove top of window
root.protocol("WM_DELETE_WINDOW", hide_window)

font_style = tkFont.Font(family="Helvetica", size=search_entry_font_size)  # Choose font and font-size

# Add tag search entry line
entry_search = tk.Entry(root, width=search_entry_width, font=font_style)
entry_search.pack(pady=5)
entry_search.bind("<KeyRelease>", lambda event: update_treeview())
entry_search.focus_set()

# Create Treeview for record show
tree = ttk.Treeview(root, columns=("id", "tags", "type", "content" ), height=tree_height)
tree.column("#0", width=0, stretch=tk.NO)  # Hide first column
tree.column("id", width=0, stretch=tk.NO)   
tree.column("tags", width=tags_width)
tree.column("type", width=0, stretch=tk.NO)  # Hide type column
tree.column("content", width=content_width)
tree.pack(pady=10)

# Set window initial size and center it
root.geometry(f'{initial_width}x{initial_height}')  
center_window(root, initial_width, initial_height)  

# Run a thread for tray icon
threading.Thread(target=run_tray, daemon=True).start()  

# Bind Escape button for window minimization
keyboard.add_hotkey('esc', hide_window)

# Bind <Shift + Delete> for entry delete
root.bind('<Shift-Delete>', lambda event: delete_record())

# Bind key for focus manage
root.bind('<Key>', handle_keypress)

# Maximize program from tray
keyboard.add_hotkey('ctrl+F1', show_window)

# Check if files directory exists and if not, create it 
ensure_files_directory()

if do_tlgrm_backup:
    # Start check backup time thread
    threading.Thread(target=backup_to_tlgrm, daemon=True).start()

# Launch program maincycle
root.mainloop()