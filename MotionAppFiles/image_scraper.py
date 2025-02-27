import os
import requests
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup
from excel_parse import get_entries
from autoimage import resize_images
from urllib.parse import urlparse
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import threading

should_stop = False
running = False
# Function to check if url is valid
def is_valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

# Function to produce search URLs
def fetch_image_urls(manufacturer, part_number, description, num_images=20):
    headers = {"User-Agent": "Mozilla/5.0"} 
    search_query = f"{manufacturer} {part_number} {description} product image"
    
    google_url = f"https://www.google.com/search?tbm=isch&q={urllib.parse.quote(search_query)}"
    bing_url = f"https://www.bing.com/images/search?q={urllib.parse.quote(search_query)}"
    
    image_urls = []
    
    for url in [google_url, bing_url]:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        
        img_tags = soup.find_all("img")
        
        for img in img_tags:
            img_url = img.get("src") or img.get("data-src")
            if img_url and img_url.startswith("http") and is_valid_url(img_url):
                image_urls.append(img_url)
                if len(image_urls) >= num_images:  # Break only after reaching the total number of images
                    break
        if len(image_urls) >= num_images:
            break
    
    return image_urls

# Function to download images and name them "ManufacturerName"_"PartNumber"
def download_images(image_urls, manufacturer, part_number):
    save_dir = f"images/staging"
    os.makedirs(save_dir, exist_ok=True)
    
    for idx, img_url in enumerate(image_urls):
        try:
            img_path = os.path.join(save_dir, f"{manufacturer}_{part_number}_{idx}.jpg")
            urllib.request.urlretrieve(img_url, img_path)
            print(f"Downloaded: {img_path}")
        except Exception as e:
            print(f"Failed to download {img_url}: {e}")

def clear_directory():
    dir_path = "images/staging"
    for filename in os.listdir(dir_path):
        file_path = os.path.join(dir_path, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")
    print("Directory cleared.")

def custom_file_dialog():
    def on_select():
        selected_file = file_listbox.get(file_listbox.curselection())
        file_path = os.path.join(current_dir, selected_file)
        if os.path.isfile(file_path):
            entry_var.set(file_path)
            dialog.destroy()
        else:
            messagebox.showerror("Error", "Please select a valid file.")

    def on_double_click(event):
        selected_file = file_listbox.get(file_listbox.curselection())
        file_path = os.path.join(current_dir, selected_file)
        if os.path.isdir(file_path):
            on_open()
        elif os.path.isfile(file_path):
            on_select()

    def on_back():
        nonlocal current_dir
        parent_dir = os.path.dirname(current_dir)
        if os.path.commonpath([home_dir, parent_dir]) == home_dir:
            current_dir = parent_dir
            update_file_list()

    def on_open():
        nonlocal current_dir
        selected_file = file_listbox.get(file_listbox.curselection())
        file_path = os.path.join(current_dir, selected_file)
        if os.path.isdir(file_path):
            current_dir = file_path
            update_file_list()
        elif os.path.isfile(file_path):
            on_select()

    def update_file_list():
        file_listbox.delete(0, tk.END)
        for item in os.listdir(current_dir):
            item_path = os.path.join(current_dir, item)
            if not item.startswith('.') and os.path.isdir(item_path) or item_path.endswith('.xlsx'):
                file_listbox.insert(tk.END, item)
        current_dir_label.config(text=current_dir)

    global running
    if running:
        messagebox.showwarning("Warning", "Scraping is already in progress.")
        return
    home_dir = os.path.expanduser("~")
    current_dir = home_dir

    dialog = tk.Toplevel(root)
    dialog.title("Select Excel File")
    dialog.geometry("600x400")

    current_dir_label = tk.Label(dialog, text=current_dir)
    current_dir_label.pack(pady=10)

    file_listbox = tk.Listbox(dialog)
    file_listbox.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
    file_listbox.bind("<Double-1>", on_double_click)

    back_button = tk.Button(dialog, text="Back", command=on_back)
    back_button.pack(side=tk.LEFT, padx=10, pady=10)

    open_button = tk.Button(dialog, text="Open", command=on_open)
    open_button.pack(side=tk.LEFT, padx=10, pady=10)

    select_button = tk.Button(dialog, text="Select", command=on_select)
    select_button.pack(side=tk.RIGHT, padx=10, pady=10)

    update_file_list()

def run():
    global running
    if running:
        messagebox.showwarning("Warning", "Scraping is already in progress.")
        return
    running = True
    excel_file = entry_var.get()
    scraping_thread = threading.Thread(target=start_scraping, args=(excel_file,))
    scraping_thread.start()

def start_scraping(excel_file):
    global current_entry_index
    entries = get_entries(excel_file)  # Fetch 10 entries as tuples

    if entries:
        for i, (manufacturer, part_number, description, id) in enumerate(entries):
            global should_stop
            if should_stop:
                break
            # Skip certain manufactuers for accuracy checking
            #if manufacturer == "3M" or manufacturer == "3M HEALTH CARE":
            #    continue
            current_entry_index = i + 1
            print(f"\n({i + 1}/{len(entries)}) Searching images for: {manufacturer} {part_number}, aka: {id}")
            image_urls = fetch_image_urls(manufacturer, part_number, description)
            
            if image_urls:
                print("Downloading images...")
                download_images(image_urls, manufacturer, part_number)
                resize_images(f"images/staging", f"images/{manufacturer}/{id}")
                clear_directory()
            else:
                print(f"No images found for {manufacturer} {part_number}.")
    else:
        print("No valid entries found in the Excel file.")

def on_closing():
    global should_stop
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        should_stop = True
        root.destroy()

def stop_running():
    global should_stop, current_entry_index
    should_stop = True
    messagebox.showinfo("Info", f"Scraping stopped at entry {current_entry_index}.")

# Main Function 
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Image Scraper")

    if os.name == 'nt':
        root.state('-zoomed')
    else:
        root.attributes('-fullscreen')

    entry_var = tk.StringVar()

    frame = tk.Frame(root)
    frame.pack(expand=True)

    image_path = "Motion_PP_SQ.png"
    img = Image.open(image_path)
    img = img.resize((200, 200), Image.ANTIALIAS)
    photo = ImageTk.PhotoImage(img)

    img_label = tk.Label(frame, image=photo)
    img_label.grid(row=0, column=0, columnspan=3, pady=0)

    tk.Label(frame, text="Select Excel File:").grid(row=1, column=0, padx=10, pady=10)
    tk.Entry(frame, textvariable=entry_var, width=50).grid(row=1, column=1, padx=10, pady=10)
    tk.Button(frame, text="Browse", command=custom_file_dialog).grid(row=1, column=2, padx=10, pady=10)
    tk.Button(frame, text="Run", command=run).grid(row=2, column=1, padx=10, pady=10)
    tk.Button(frame, text="Stop", command=stop_running).grid(row=2, column=2, padx=10, pady=10)
    #tk.Label(frame, text= f"Entry ()")
    #excel_file = input("Enter the Excel file path: ")
    
    root.protocol("WM_DELETE_WINDOW", on_closing)

    root.mainloop()