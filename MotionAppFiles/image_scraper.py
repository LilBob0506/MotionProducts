import os
import sys
import requests
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup
from excel_parse import get_entries, get_context_urls
from autoimage import resize_images
from urllib.parse import urlparse
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import threading
from tkinter.filedialog import askopenfilename
import json

if os.name == 'nt':  # Windows
    CONFIG_DIR = os.path.join(os.environ["USERPROFILE"], "ImageScraperFiles")
else:  # Unix-like (Linux/Mac)
    CONFIG_DIR = os.path.join(os.environ["HOME"], "ImageScraperFiles")

CONFIG_FILE = os.path.join(CONFIG_DIR,"config.json")

os.makedirs(CONFIG_DIR, exist_ok=True)

should_stop = False # Flag to check if scraping should stop
running = False # Flag to check if scraping is in progress
man_website = False # True if manufacturer website is used

# Function to check if url is valid
def is_valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Function to produce search URLs
def fetch_image_urls(manufacturer, part_number, con_url, description):
    global man_website
    num_images = 20
    headers = {"User-Agent": "Mozilla/5.0"} 
    if man_website:
        if part_number:
            search_query = f'site:{con_url} "{manufacturer} {part_number}"' #Specific sites
        else:
            search_query = f'site:{con_url} "{manufacturer} {description}"'
    else:
        if part_number:
            search_query = f'"{manufacturer} {part_number}"'
        else:
            search_query = f'"{manufacturer} {description}"'
    
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
def download_images(image_urls, manufacturer, part_number, output_dir):
    save_dir = f"{output_dir}/images/staging"
    os.makedirs(save_dir, exist_ok=True)
    
    for idx, img_url in enumerate(image_urls):
        try:
            img_path = os.path.join(save_dir, f"{manufacturer}_{part_number}_{idx}.jpg")
            urllib.request.urlretrieve(img_url, img_path)
            print(f"Downloaded: {img_path}")
        except Exception as e:
            print(f"Failed to download {img_url}: {e}")

def clear_directory(output_dir):
    dir_path = f"{output_dir}/images/staging"
    for filename in os.listdir(dir_path):
        file_path = os.path.join(dir_path, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")
    print("Directory cleared.")

def custom_file_dialog(option):
    global running
    if running:
        messagebox.showwarning("Warning", "Scraping is already in progress.")
        return

    file_types = [("Excel files", "*.xlsx"), ("All files", "*.*")]

    file_path = askopenfilename(
        initialdir="/host_files",  # Your Docker-mounted directory
        title="Select an Excel file",
        filetypes=file_types
    )

    if file_path:  # If a file is selected
        if option == 0:
            file_var.set(file_path)
        elif option == 1:
            context_var.set(file_path)
    else:
        messagebox.showwarning("Warning", "No file selected.")

def run():
    global running, should_stop
    if running:
        messagebox.showwarning("Warning", "Scraping is already in progress.")
        return
    running = True
    should_stop = False
    run_button.config(state=tk.DISABLED)
    messagebox.showinfo("Info", "Scraping started.")
    excel_file = file_var.get()
    context_file = context_var.get()
    output_dir = output_var.get()
    try:
        entry_range_x = int(entry_var_x.get())
        entry_range_y = int(entry_var_y.get())
    except ValueError:
        messagebox.showerror("Error", "Please enter valid entry range.")
        running = False
        return
    scraping_thread = threading.Thread(target=start_scraping, args=(excel_file,entry_range_x,entry_range_y,context_file,output_dir,))
    scraping_thread.start()
    running = False
    return

def start_scraping(excel_file, entry_range_x, entry_range_y, context_file,output_dir):
    global current_entry_index, total_entry_count, man_website,running
    entries = get_entries(excel_file)  # Fetch entries as tuples
    context_urls = get_context_urls(context_file)
    total_entry_count = len(entries) + 1
    last_manufacturer = ""
    repeat = 0
    if entries and context_urls:
        for i, (manufacturer, part_number, description, id) in enumerate(entries):
            global should_stop
            if should_stop:
                break
            #Debug statement for moving through manufactuerers rapidly
            #if manufacturer == last_manufacturer:
            #    repeat += 1
            #    if repeat >= 5:
            #        continue
            #if manufacturer != last_manufacturer:
            #    repeat = 0
            #End debug

            if (entry_range_x != 0 and i < entry_range_x -1) or (entry_range_y != 0 and entry_range_y <= i):
                continue
            if manufacturer != last_manufacturer:
                for (url_manufacturer, url) in (context_urls):
                    #print (f"Manufacturer: {manufacturer}, URL Manufacturer: {url_manufacturer} : {url}")
                    if manufacturer == url_manufacturer:
                        #print(f"Found context URL for {manufacturer}: {url}")
                        con_url = url
                        man_website = True
                        break
                    else:
                        #print(f"No context URL found for {manufacturer}.")
                        con_url = ""
                        man_website = False
                    
                last_manufacturer = manufacturer
            current_entry_index = i + 1
            tk.Label(frame, text= f"Entry ({current_entry_index}/{total_entry_count})").grid(row=6,column=1,padx=10,pady=10)
            print(f"\n({i + 1}/{len(entries)}) Searching images for: {manufacturer} {part_number}, aka: {id}")
            image_urls = fetch_image_urls(manufacturer, part_number, con_url, description)
            
            if image_urls:
                print("Downloading images...")
                download_images(image_urls, manufacturer, part_number,output_dir)
                if man_website:
                    resize_images(f"{output_dir}/images/staging", f"{output_dir}/images/specific/{manufacturer}/{id}")
                else:
                    resize_images(f"{output_dir}/images/staging", f"{output_dir}/images/generic/{manufacturer}/{id}")
                clear_directory(output_dir)
            else:
                print(f"No images found for {manufacturer} {part_number}.")
    else:
        print("No valid entries found in the Excel file.")
    
    running = False
    run_button.config(state=tk.NORMAL)
    return

def on_closing():
    global should_stop
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        should_stop = True
        root.destroy()

def stop_running():
    global should_stop, current_entry_index, running
    should_stop = True
    running = False
    messagebox.showinfo("Info", f"Scraping stopped at entry {current_entry_index}.")
    return

def clear_fields():
    entry_var_x.set("")
    entry_var_y.set("")
    file_var.set("")
    context_var.set("")
    output_var.set("")
    
def save_config(name, value):
    config = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
    config[name] = value
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

def load_config(name):
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            return config.get(name, "")
    return ""

# Main Function 
if __name__ == "__main__":
    root = tk.Tk()
    root.config(padx=30, pady=30) 
    root.title("")

    if os.name == 'nt':
        root.state('zoomed')
    else:
        root.attributes('-fullscreen')

    file_var = tk.StringVar()
    file_var.set(load_config("file_var"))
    output_var = tk.StringVar()
    output_var.set(load_config("output_var"))
    context_var = tk.StringVar()
    context_var.set(load_config("context_var"))
    entry_var_x = tk.StringVar()
    entry_var_y = tk.StringVar()
    frame = tk.Frame(root)
    frame.pack(expand=True)

    image_path = resource_path("Motion_PP_SQ.png")
    img = Image.open(image_path)
    img = img.resize((200, 200), Image.LANCZOS)
    photo = ImageTk.PhotoImage(img)

    img_label = tk.Label(frame, image=photo)
    img_label.grid(row=0, column=0, columnspan=3, pady=5)

    # Range of entries
    tk.Label(frame, text="Enter range of Entries (x,y) or 0,0 for All:", anchor="w").grid(row=1, column=0, sticky="w", padx=5, pady=5)
    tk.Entry(frame, textvariable=entry_var_x, width=10, bd=1, relief="solid", highlightthickness=2).grid(row=1, column=1, padx=5, pady=5, sticky="w") 
    tk.Entry(frame, textvariable=entry_var_y, width=10, bd=1, relief="solid", highlightthickness=2).grid(row=1, column=1, padx=5, pady=5, sticky="e") 

    # Excel file input
    tk.Label(frame, text="Select Excel File for input:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
    tk.Entry(frame, textvariable=file_var, width=50, bd=1, relief="solid", highlightthickness=2).grid(row=2, column=1, padx=5, pady=5, sticky="ew")
    tk.Button(frame, text="Browse", command=lambda: [
        file_var.set(askopenfilename(initialdir="/host_files", filetypes=[("Excel files", "*.xlsx")], title="Select an Excel file")),
        save_config("file_var", file_var.get())
        ]
    ).grid(row=2, column=2, padx=5, pady=5)

    # Content URLs
    tk.Label(frame, text="Select Excel File for context URLs:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
    tk.Entry(frame, textvariable=context_var, width=50, bd=1, relief="solid", highlightthickness=2).grid(row=3, column=1, padx=5, pady=5, sticky="ew")
    tk.Button(frame, text="Browse", command=lambda: [
        context_var.set(askopenfilename(initialdir="/host_files", filetypes=[("Excel files", "*.xlsx")], title="Select an Excel file")),
        save_config("context_var", context_var.get())
        ]
        ).grid(row=3, column=2, padx=5, pady=5)

    # Clear, Run, Stop buttons
    tk.Button(frame, text="Clear", command=clear_fields).grid(row=5, column=0, padx=5, pady=10)
    run_button = tk.Button(frame, text="Run", command=run)
    run_button.grid(row=5, column=1, padx=5, pady=10)
    tk.Button(frame, text="Stop", command=stop_running).grid(row=5, column=2, padx=5, pady=10)
    
    #Output directory button
    tk.Label(frame, text="Select a Destination for output:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
    tk.Entry(frame, textvariable=output_var, width=50, bd=1, relief="solid", highlightthickness=2).grid(row=4, column=1, padx=5, pady=5, sticky="ew")
    tk.Button(frame, text="Browse", command=lambda: [
        output_var.set(filedialog.askdirectory(initialdir="/host_files", title="Select a Destination for output")),
        save_config("output_var", output_var.get())
        ]
        ).grid(row=4, column=2, padx=5, pady=5)

    root.protocol("WM_DELETE_WINDOW", on_closing)

    root.mainloop()