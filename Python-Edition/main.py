import requests, json, webbrowser, tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import showinfo

# To do: implement JotaNotes file encryption

filepath = None

def open_file(event=None):
    global filepath
    filepath = askopenfilename(filetypes=[
        ("Text Files", "*.txt"),
        ("Python code", "*.py"),
        ("JSON file", "*.json"),
        ("HTML Website", "*.html"),
        ("JavaScript", "*.js"),
        ("Cascade StyleSheet", "*.css"),
        ("C code", "*.c"),
        ("C++ code", "*.cpp"),
        ("C/C++ header", "*.h"),
        ("C# code", "*.cs"),
        ("Unix config file", ".*"),
        ("All Files", "*.*")
        ])
    if not filepath:
        return
    txt_edit.delete("1.0", tk.END)
    with open(filepath, "r", encoding="utf-8") as input_file:
        text = input_file.read()
        txt_edit.insert(tk.END, text)
    window.title(f"Jotalea Text Editor - {filepath}")

def new_file(event=None):
    txt_edit.delete("1.0", tk.END)
    window.title("Jotalea Text Editor - New File")

def save_file(event=None):
    global filepath
    temp_filepath = asksaveasfilename(defaultextension=".txt", filetypes=[
        ("Text Files", "*.txt"),
        ("Python code", "*.py"),
        ("JSON file", "*.json"),
        ("HTML Website", "*.html"),
        ("JavaScript", "*.js"),
        ("Cascade StyleSheet", "*.css"),
        ("C code", "*.c"),
        ("C++ code", "*.cpp"),
        ("C/C++ header", "*.h"),
        ("C# code", "*.cs"),
        ("Unix config file", ".*"),
        ("All Files", "*.*")
        ])
    
    if not temp_filepath:
        return

    if isinstance(temp_filepath, tuple):
        print("Received a tuple instead of a string.")
        return
    
    filepath = temp_filepath
    
    with open(filepath, "w", encoding="utf-8") as output_file:
        text = txt_edit.get("1.0", tk.END)
        output_file.write(text)
    
    window.title(f"Jotalea Text Editor - {filepath}")

def save_file_as(event=None):
    global filepath
    if filepath is None:
        filepath = asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if not filepath:
            return
    with open(filepath, "w", encoding="utf-8") as output_file:
        text = txt_edit.get("1.0", tk.END)
        output_file.write(text)
    window.title(f"Jotalea Text Editor - {filepath}")

def call_gpt3_api(
        prompt,
        api_key,
        model="gpt-3.5-turbo-16k",
        endpoint="https://api.openai.com/v1/chat/completions",
        max_tokens=1024
    ):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful AI."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens
    }
    
    response = requests.post(endpoint, headers=headers, json=data)
    
    if response.status_code == 200:
        return json.loads(response.text)["choices"][0]["message"]["content"]
    else:
        return f"Error: {response}"

def ask_gpt3(prompt, api_key, endpoint="https://api.openai.com/v1/chat/completions", char_limit=512, ai_model="gpt-3.5-turbo-16k"):
    prompt = user_input.get("1.0", "end-1c")
    key = api_key
    api_endpoint = endpoint
    chat_limit = char_limit

    response = call_gpt3_api(prompt, key, api_endpoint, chat_limit, ai_model)

    gpt3_response.delete("1.0", tk.END)
    gpt3_response.insert(tk.END, response)

def open_gpt3_window():
    global user_input, gpt3_response, api_key_entry, endpoint_entry, char_limit_entry, ai_model_entry
    gpt3_win = tk.Toplevel(window)
    gpt3_win.title("Ask ChatGPT")

    user_input = tk.Text(gpt3_win, height=10, width=50)
    user_input.grid(row=0, column=0, columnspan=4)

    tk.Button(gpt3_win, text="Ask ChatGPT", command=ask_gpt3).grid(row=1, column=0, columnspan=4)

    gpt3_response = tk.Text(gpt3_win, height=10, width=50, state=tk.DISABLED)
    gpt3_response.grid(row=2, column=0, columnspan=4)

    # Configuración de la API
    tk.Label(gpt3_win, text="API Key:").grid(row=3, column=0)
    api_key_entry = tk.Entry(gpt3_win, width=40).grid(row=3, column=1)

    tk.Label(gpt3_win, text="Endpoint:").grid(row=4, column=0)
    endpoint_entry = tk.Entry(gpt3_win, width=60).grid(row=4, column=1)

    tk.Label(gpt3_win, text="Char Limit:").grid(row=5, column=0)
    char_limit_entry = tk.Entry(gpt3_win, width=10).grid(row=5, column=1)

    tk.Label(gpt3_win, text="AI Model:").grid(row=6, column=0)
    ai_model_entry = tk.Entry(gpt3_win, width=20).grid(row=6, column=1)

def save_config(config):
    with open("config.json", "w") as f:
        json.dump(config, f)

def load_config():
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_api_config():
    config = {}
    config["api_key"] = api_key_entry.get()
    config["endpoint"] = endpoint_entry.get()
    config["char_limit"] = char_limit_entry.get()
    config["ai_model"] = ai_model_entry.get()
    save_config(config)

def load_api_config():
    config = load_config()
    api_key_entry.insert(0, config.get("api_key", ""))
    endpoint_entry.insert(0, config.get("endpoint", "https://api.openai.com/v1/chat/completions"))
    char_limit_entry.insert(0, config.get("char_limit", "512"))
    ai_model_entry.insert(0, config.get("ai_model", "gpt-3.5-turbo"))

def cut_text(event=None):
    txt_edit.event_generate("<<Cut>>")

def copy_text(event=None):
    txt_edit.event_generate("<<Copy>>")

def paste_text(event=None):
    txt_edit.event_generate("<<Paste>>")

def show_help(event=None):
    help_win = tk.Toplevel(window)
    help_win.title("Help menu")
    help_win.geometry("450x90")
    help_win.resizable(False, False)

    tk.Label(help_win, text="This is a simple text editor. Use the File menu to open or save files.").grid(row=0, column=0)
    tk.Label(help_win, text="Software version 1.0").grid(row=1, column=0)
    tk.Button(help_win, text="Open official website", command=open_website).grid(row=2, column=0, columnspan=4)

def open_website():
    webbrowser.open("https://jotalea.com.ar", new=2)

def quit_app(event=None):
    quit_win = tk.Toplevel(window)
    quit_win.title("Are you sure?")
    quit_win.geometry("450x90")
    quit_win.resizable(False, False)

    tk.Label(quit_win, text="Are you sure you want to exit?").grid(row=0, column=0)
    tk.Label(quit_win, text="Changes will not be saved").grid(row=1, column=0)
    tk.Button(quit_win, text="Yes, quit", command=window.quit).grid(row=2, column=0)
    tk.Button(quit_win, text="No, don't quit", command=quit_win.destroy).grid(row=2, column=1)

window = tk.Tk()
window.title("Jotalea Text Editor")
window.geometry("640x360")
window.minsize(300, 200)

window.bind("<Control-o>", lambda event: open_file())
window.bind("<Control-s>", lambda event: save_file())
window.bind("<Control-Shift-S>", lambda event: save_file_as())  # Podría reemplazar esto con una función "Save As..."
window.bind("<Control-n>", new_file)
window.bind("<Control-x>", lambda event: cut_text())
window.bind("<Control-c>", lambda event: copy_text())
window.bind("<Control-v>", lambda event: paste_text())
window.bind("<F1>", lambda event: show_help())
window.bind("<Control-q>", quit_app)

menu_bar = tk.Menu(window)

menu_file = tk.Menu(menu_bar, tearoff=0)
menu_file.add_command(label="New", command=new_file)
menu_file.add_command(label="Open", command=open_file)
menu_file.add_command(label="Save", command=save_file)
menu_file.add_command(label="Save As...", command=save_file_as)
menu_file.add_command(label="Exit", command=quit_app)

# menu_options = tk.Menu(menu_bar, tearoff=0)                                                                                       # DELETE THE "#" AT THE BEGGINING TO IMPLEMENT FEATURE
# menu_options.add_command(label="Placeholder Option")
# menu_options.add_command(label="Save API settings", command=save_api_config)                                                      # DELETE THE "#" AT THE BEGGINING TO IMPLEMENT FEATURE

menu_edit = tk.Menu(menu_bar, tearoff=0)
menu_edit.add_command(label="Cut", command=cut_text)
menu_edit.add_command(label="Copy", command=copy_text)
menu_edit.add_command(label="Paste", command=paste_text)

menu_help = tk.Menu(menu_bar, tearoff=0)
menu_help.add_command(label="About", command=show_help)
menu_help.add_command(label="Website", command=open_website)

menu_gpt = tk.Menu(menu_bar, tearoff=0)
menu_gpt.add_command(label="Ask ChatGPT", command=open_gpt3_window)

menu_bar.add_cascade(label="File", menu=menu_file)
# menu_bar.add_cascade(label="Options", menu=menu_options)
menu_bar.add_cascade(label="Edit", menu=menu_edit)
menu_bar.add_cascade(label="Help", menu=menu_help)
#menu_bar.add_cascade(label="ChatGPT", menu=menu_gpt)                                                                              # DELETE THE "#" AT THE BEGGINING TO IMPLEMENT FEATURE

window.config(menu=menu_bar)

api_key_entry = tk.Entry()
endpoint_entry = tk.Entry()
char_limit_entry = tk.Entry()
ai_model_entry = tk.Entry()

txt_edit = tk.Text(window)
txt_edit.grid(row=0, column=0, sticky="nsew") 

window.rowconfigure(0, weight=1)
window.columnconfigure(0, weight=1)

load_api_config()

window.mainloop()
