from PIL import Image, ImageFilter
import numpy as np
from scipy.spatial import Voronoi

# Load the image
img = Image.open('sat_img_00046.png')

# Define the pixelation block size
block_size = 8

def average_color_pixelation(img, block_size):
    # Get the dimensions of the image
    width, height = img.size

    # Calculate the number of horizontal and vertical pixels
    h_pixels = width // block_size
    v_pixels = height // block_size

    # Loop through each pixelated block
    for i in range(h_pixels):
        for j in range(v_pixels):
            # Calculate the range of pixels to average
            left = i * block_size
            upper = j * block_size
            right = (i + 1) * block_size
            lower = (j + 1) * block_size
            
            # Crop the block of pixels
            block = img.crop((left, upper, right, lower))
            
            # Calculate the average color of the block
            block_average_color = block.resize((1,1)).getpixel((0,0))
            
            # Replace the block with the average color
            img.paste(block_average_color, (left, upper, right, lower))
            
    # Save the pixelated image
    img.save(img.filename.split('.')[0]+'_pixelated_ac.jpg')
    print(f"Generated pixelated image with {h_pixels}/{v_pixels}")


#Nearest Neighbour Pixelation
def nn_pixelation(img, block_size):
    # Get the dimensions of the image
    width, height = img.size

    # Calculate the number of blocks in each dimension
    num_blocks_x = (width + block_size - 1) // block_size
    num_blocks_y = (height + block_size - 1) // block_size

    # Loop over each block
    for i in range(num_blocks_x):
        for j in range(num_blocks_y):
            
            # Calculate the block boundaries
            x0 = i * block_size
            y0 = j * block_size
            x1 = min(x0 + block_size, width)
            y1 = min(y0 + block_size, height)
            
            # Get the color of the top-left pixel in the block
            pixel = img.getpixel((x0, y0))
            
            # Set all pixels in the block to that color
            for x in range(x0, x1):
                for y in range(y0, y1):
                    img.putpixel((x, y), pixel)

    # Save the pixelated image
    img.save(img.filename.split('.')[0]+'_pixelated_nn.jpg')
    print(f"Generated pixelated image with {num_blocks_x}/{num_blocks_y}")

nn_pixelation(img, block_size)