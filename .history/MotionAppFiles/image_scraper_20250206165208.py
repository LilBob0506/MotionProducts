import os
import requests
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup

def fetch_image_urls(manufacturer, part_number, num_images=5):
    headers = {"User-Agent": "Mozilla/5.0"}
    
    search_query = f"{manufacturer} {part_number} product image"
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
                if len(image_urls) >= num_images:
                    return image_urls
    
    return image_urls

def download_images(image_urls, manufacturer, part_number):
    save_dir = f"images/{manufacturer}_{part_number}"
    os.makedirs(save_dir, exist_ok=True)
    
    for idx, img_url in enumerate(image_urls):
        try:
            img_path = os.path.join(save_dir, f"image_{idx+1}.jpg")
            urllib.request.urlretrieve(img_url, img_path)
            print(f"Downloaded: {img_path}")
        except Exception as e:
            print(f"Failed to download {img_url}: {e}")

if __name__ == "__main__":
    manufacturer = input("Enter manufacturer name: ")
    part_number = input("Enter product part number: ")
    
    print("Searching for images...")
    image_urls = fetch_image_urls(manufacturer, part_number)
    
    if image_urls:
        print("Downloading images...")
        download_images(image_urls, manufacturer, part_number)
        print("Done!")
    else:
        print("No images found.")
