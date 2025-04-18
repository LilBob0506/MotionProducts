# MotionProducts

This application automates the process of searching and downloading product images for Motion.com products which do not have images using Google and Bing. It reads product information from an Excel file and downloads relevant images automatically.

### Project Website

https://lilbob0506.github.io/MotionProducts/

## How to Install Software

### Prerequisites

- Python 3.12+
- Docker (optional)
- Git

### Required Python Packages

Install the necessary dependencies using:
```sh
pip install -r requirements.txt
```
### Deployment with Docker

```sh
git clone https://github.com/LilBob0506/MotionProducts
cd MotionAppFiles

docker build -t image_scraper .
docker run -p 8000:8000 image_scraper
```

### Deployment without Docker

```sh
git clone https://github.com/LilBob0506/MotionProducts
cd MotionAppFiles

pip install -r requirements.txt

python image_scraper.py
```
### Windows and Mac Executables

- Found in `MotionProducts/MotionAppFiles/Executable`
- Will run application without the need to download dependancies or build/run program

### External Resources

- Google Images: https://www.google.com/search?tbm=isch
- Bing Images: https://www.bing.com/images/search 
- Free usage, no API keys needed


## How to Use each completed feature

### 1. Load Product Entries

Load an Excel file with manufacturer names, part numbers, and descriptions

- Used in GUI: "Select Excel File for input: "
- Code: `get_entries()` from `excel_parse.py`

### 2. Use Manufacturer-Specific Context URLs

Optionally add another Excel file to specify preferred manufacturer websites to search from.

- Used in GUI: "Select Excel File for context URLs: "
- Code: `get_context_urls()` from `excel_parse.py`

### 3. Scrape Images from Google & Bing

Searches both Google Images and Bing Images for each entry.

- Code:\
&emsp; `fetch_image_urls()` in `image_scraper.py` builds search queries\
&emsp; Parses HTML responses with BeautifulSoup package

- External Resources\
&emsp; Google Images: https://www.google.com/search?tbm=isch\
&emsp; Bing Images: https://www.bing.com/images/search

- Notes:\
&emsp; Manufacturer URLs improve search relevance\
&emsp; Scrapes up to 20 images per product

### 4. Download & Save Images

Downloads images to a specified output directory.

- Used in GUI: "Select a Destination for output: "
- Code: `download_images()` saves as `{Manufacturer}_{PartNumber}_{Index}.jpg` in `/images/staging`

#### Directory created:

```
/output/
  └── images/
      ├── staging/
      ├── generic/{Manufacturer}/{ProductID}
      └── specific/{Manufacturer}/{ProductID}
```
### 5. Resize & Organize Images

Uses `resize_images()` from `autoimage.py` to resize and save images under:

- `/images/specific/` if the manufacturer website was used
- `/images/generic/` otherwise

### 6. GUI Control Flow

| Button | Action |
| --- | --- |
| `Run`  | Starts the scraping process. Uses threading to keep GUI responsive. |
| `Stop` | Stops scraping. Saves progress. |
| `Clear` | Resets all fields |
| `Browse` | Used to select Excel or output folders.

### Function Link Example

When user hits run: 

- GUI collects file paths and range from `file_var`, `context_var`, `entry_var_x/y`
- Calls `start_scraping()` in a background thread
- `start_scraping()`:\
&emsp; Loops through Excel entries\
&emsp; Calls `fetch_image_urls()` to query Google/Bing\
&emsp; Calls `download_images()` to save raw files\
&emsp; Calls `resize_images()` to format and move output\
&emsp; Calls `clear_directory()` to reset staging area

## How to modify/extend software

### Technical Overview

| Component | Technology |
| --- | --- |
| Language  | Python 3.12+ |
| Image Processing | PIL (Pillow) |
| Web scraping | Requests + BeautifulSoup |
| External Resources | Google & Bing image search (scraped, no API) |
|Optional Virtualization | Docker |

### Dependencies

- Listed in `requirements.txt`
- Install with: `pip install -r requirements.txt`

### Build/Run Instructions

No compiler or build system needed - just Python

- To run: `python image_scraper.py`\
- To package, tools like PyInstaller can be used:
`pyinstaller --noconfirm --onefile image_scraper.py`

### Testing

Test with `List.xlsx` to load manufacturer names, part numbers, and descriptions and `Context URLs.xlsx` to specify preferred manufacturer websites to search from.

- `MotionProducts/MotionAppFiles/List.xlsx`
- `MotionProducts/MotionAppFiles/Context URLs.xlsx`

### Issues
- Moving image storage to cloud (e.g. Google Cloud)
- Image quality and accuracy 

### Coding Style

- Use clear, self-explanatory function names (download_images, not dlimg)
- Comments for all functions
- GUI logic in image_scraper.py
- Processing logic in `autoimage.py`, `excel_parse.py`
- Avoid hardcoded paths — use os.path.join() and config storage

### How to extend Features

- Store images in the cloud

## FAQ

### 1. Can I use this on Mac and Linux?

Yes! The application is cross-platform and runs on:

- Windows
- macOS
- Linux

Just make sure Python 3.12+ is installed, along with the dependencies listed in requirements.txt.

###  2. Where are the downloaded images located?

Downloaded images are stored in a folder structure under the output directory you selected in the app:
```
/your-output-folder/
└── images/
    ├── staging/                  ← Temporary download location before sorting
    ├── generic/{Manufacturer}/{ProductID}/
    └── specific/{Manufacturer}/{ProductID}/
```
Or if you're running the executable, check the folder where the executable is located.

### 3. Why do some of the images have poor quality?

There are a few reasons for this:

- Low-resolution thumbnails	- Google and Bing may return small thumbnail versions of images, especially when scraping without clicking into full-size previews.
- No high-quality sources available - If a product is obscure or has limited web presence, image options may be poor across the board.
- Search query ambiguity - If the part number or description is too generic, irrelevant or low-quality images may be returned.
- Manufacturer site not used - If no matching context URL is found, the scraper defaults to a generic search, which may yield mixed results.

For the best results ensure you provide a context Excel file with accurate manufacturer URLs.
