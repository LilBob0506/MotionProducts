import os
import requests
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup
from excel_parse import get_entries
from autoimage import resize_images

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
            if img_url and img_url.startswith("http"):
                image_urls.append(img_url)
                if len(image_urls) >= num_images:  # Break only after reaching the total number of images
                    break
        if len(image_urls) >= num_images:
            break
    
    return image_urls

# Function to download images and name them "ManufacturerName"_"PartNumber"
def download_images(image_urls):
    save_dir = f"images/staging"
    os.makedirs(save_dir, exist_ok=True)
    
    for idx, img_url in enumerate(image_urls):
        try:
            img_path = os.path.join(save_dir, f"image_{idx+1}.jpg")
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

# Main Function 
if __name__ == "__main__":
    excel_file = input("Enter the Excel file path: ")
    entries = get_entries(excel_file)  # Fetch 10 entries as tuples

    if entries:
        for i, (manufacturer, part_number, description, id) in enumerate(entries):
            # Skip certain manufactuers for accuracy checking
            #if manufacturer == "3M" or manufacturer == "3M HEALTH CARE":
            #    continue
            print(f"\n({i + 1}/{len(entries)}) Searching images for: {manufacturer} {part_number}, aka: {id}")
            image_urls = fetch_image_urls(manufacturer, part_number, description)
            
            if image_urls:
                print("Downloading images...")
                download_images(image_urls)
                resize_images(f"images/staging", f"images/{manufacturer}/{id}")
                clear_directory()
            else:
                print(f"No images found for {manufacturer} {part_number}.")
    else:
        print("No valid entries found in the Excel file.")
