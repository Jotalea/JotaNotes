import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from tkinter import filedialog, messagebox
import tkinter as tk

filepath = None
key = 'JotaNotes'

def encrypt_text(text, key):
    cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(text.encode('utf-8'), AES.block_size))
    iv = base64.b64encode(cipher.iv).decode('utf-8')
    ct = base64.b64encode(ct_bytes).decode('utf-8')
    return iv, ct

def decrypt_text(iv, ct, key):
    cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, base64.b64decode(iv))
    pt = cipher.decrypt(base64.b64decode(ct))
    return unpad(pt, AES.block_size).decode('utf-8')

def save_encrypted_file(filepath, text, key):
    iv, encrypted_text = encrypt_text(text, key)
    with open(filepath, 'w') as file:
        file.write(f"{iv}:{encrypted_text}")

def open_encrypted_file(filepath, key):
    with open(filepath, 'r') as file:
        iv, encrypted_text = file.read().split(':')
        return decrypt_text(iv, encrypted_text, key)

def open_file():
    global filepath
    filepath = filedialog.askopenfilename(filetypes=[
        ("JotaNotes Encrypted File", "*.jne"),
        ("Text Files", "*.txt"),
        ("All Files", "*.*")
    ])
    if not filepath:
        return
    try:
        text = open_encrypted_file(filepath, key)
    except Exception as e:
        messagebox.showerror("Error", str(e))
        return
    text_editor.delete("1.0", tk.END)
    text_editor.insert(tk.END, text)
    window.title(f"Jotalea Text Editor - {filepath}")

def new_file():
    text_editor.delete("1.0", tk.END)
    window.title("Jotalea Text Editor - New File")

def save_file():
    global filepath
    if filepath:
        try:
            save_encrypted_file(filepath, text_editor.get("1.0", tk.END), key)
        except Exception as e:
            messagebox.showerror("Error", str(e))
    else:
        save_file_as()

def save_file_as():
    global filepath
    filepath = filedialog.asksaveasfilename(filetypes=[
        ("JotaNotes Encrypted File", "*.jne"),
        ("Text Files", "*.txt"),
        ("All Files", "*.*")
    ])
    if not filepath:
        return
    try:
        if filepath.lower().endswith('.jne'):
            save_encrypted_file(filepath, text_editor.get("1.0", tk.END), key)
        else:
            with open(filepath, 'w') as file:
                file.write(text_editor.get("1.0", tk.END))
    except Exception as e:
        messagebox.showerror("Error", str(e))
    window.title(f"Jotalea Text Editor - {filepath}")

window = tk.Tk()
window.title("Jotalea Text Editor")
window.geometry("640x360")
window.minsize(300, 200)

text_editor = tk.Text(window)
text_editor.pack(expand=True, fill="both")

menu_bar = tk.Menu(window)

file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="New", command=new_file)
file_menu.add_command(label="Open", command=open_file)
file_menu.add_command(label="Save", command=save_file)
file_menu.add_command(label="Save As...", command=save_file_as)
menu_bar.add_cascade(label="File", menu=file_menu)

window.config(menu=menu_bar)

window.mainloop()
