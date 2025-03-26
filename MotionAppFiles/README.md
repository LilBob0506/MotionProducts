# Motion.com Product Image Scraper

## Overview
This application automates the process of searching and downloading product images for Motion.com products which do not have images using Google and Bing. It reads product information from an Excel file and downloads relevant images automatically.

## Prerequisites
Ensure you have **Python 3.x** installed on your system.

### Required Python Packages
Install the necessary dependencies using:
```sh
pip install requests beautifulsoup4 pandas openpyxl
pip install Pillow
```

## Project Structure
```
MotionAppFiles/
│── image_scraper.py        # Main script to fetch and download images
│── excel_parse.py          # Reads manufacturer and part number from Excel
│── List.xlsx               # Excel file containing product details
│── images/                 # Directory where downloaded images are stored
│── README.md               # Documentation file
```

## How to Run
1. **Prepare the Excel File**
   - Place your Excel file (`List.xlsx`) in the project directory.
   - Ensure it has the necessary columns: `MFR_NAME` and `Part Number`.

2. **Run the Image Scraper**
```sh
python image_scraper.py
```

3. **Enter the Excel File Path**
```sh
Enter the Excel file path: ~/"Your_Directory_For_Repos"/MotionProducts/MotionAppFiles/List.xlsx
```

## Docker Run
'''sh
docker run -it \
  -e DISPLAY=host.docker.internal:0 \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v /Users/YOURNAME/Downloads:/host_files \
  motion-products

---


