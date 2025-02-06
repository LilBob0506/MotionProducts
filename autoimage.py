import os
from PIL import Image # pip install Pillow

# Code takes all images from a folder location and creates two new images, one formatted to 496x496 and the other 64x64.
# When outputting the picture it appends "_496" and "_64" to the end of the original file name respectfully.

# Input folder directory (format with // instead of \)
# Code assumes all files in folder are images, no error handling for non images
input = "C://Users//sammy//OneDrive//Desktop//Home//cs495//Motion//InputPics"

# Output folder directory (format with // instead of \)
outfolder = "C://Users//sammy//OneDrive//Desktop//Home//cs495//Motion//OutPics"

dir_list = os.listdir(input) # Creates list with all original image file names

for pic in dir_list: # Runs for each image name

    imageopen = os.path.join(input, pic) # Appends filename to end of open path
    image = Image.open(imageopen) # Opens image

    new_496 = image.resize((496, 496)) # Reformats to 496x496
    new_64 = image.resize((64, 64)) # Reformats to 64x64

    out496 = pic.replace(pic[pic.rfind("."): ], "_496" + pic[pic.rfind("."): ]) # Appends "_496 to end of file name"
    out64 = pic.replace(pic[pic.rfind("."): ], "_64" + pic[pic.rfind("."): ]) # Appends "_64 to end of file name"

    out496 = os.path.join(outfolder, out496) # Appends new 496 filename to end of output path
    out64 = os.path.join(outfolder, out64) # Appends new 64 filename to end of output path

    new_496.save(out496, new_496.format) # Saves 496 image to output folder
    new_64.save(out64, new_64.format) # Saves 64 image to output folder