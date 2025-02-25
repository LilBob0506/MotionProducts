import os
from PIL import Image # pip install Pillow
def resize_images(input_folder, output_folder):
# Code takes all images from a folder location and creates two new images, one formatted to 496x496 and the other 64x64.
# When outputting the picture it appends "_496" and "_64" to the end of the original file name respectfully.

# Input folder directory (format with // instead of \)
# Code assumes all files in folder are images, no error handling for non images
# Output folder directory (format with // instead of \)
    

    dir_list = os.listdir(input_folder) # Creates list with all original image file names
    i = 0 # Counter for appending to end of file name

    for pic in dir_list: # Runs for each image name
        imageopen = os.path.join(input_folder, pic) # Appends filename to end of open path
        i += 1 # Increments counter for next image    
        try:
            image = Image.open(imageopen) # Opens image
        except IOError:
            print(f"Unable to open {pic}. Skipping.")
            continue
        
        if image.mode != 'RGB':
            image = image.convert('RGB') # Converts image to RGB

        new_496 = image.resize((496, 496)) # Reformats to 496x496
        new_64 = image.resize((64, 64)) # Reformats to 64x64

        out496 = pic # Appends "_496 to end of file name"
        out64 = pic # Appends "_64 to end of file name"

        out496 = os.path.join(output_folder + "/496", out496) # Appends new 496 filename to end of output path
        out64 = os.path.join(output_folder + "/64", out64) # Appends new 64 filename to end of output path
        
        os.makedirs(output_folder + "/496", exist_ok=True)
        os.makedirs(output_folder + "/64", exist_ok=True)

        new_496.save(out496, new_496.format) # Saves 496 image to output folder
        new_64.save(out64, new_64.format) # Saves 64 image to output folder