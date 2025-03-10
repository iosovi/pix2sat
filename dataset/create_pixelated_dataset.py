import os
import shutil
from PIL import Image
from tqdm import tqdm


def average_color_pixelation(img, block_size, folder_path):
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
            block_average_color = block.resize((1, 1)).getpixel((0, 0))

            # Replace the block with the average color
            img.paste(block_average_color, (left, upper, right, lower))

    # Save the pixelated image
    file_name = img.filename
    img.save(f'{folder_path}\\{os.path.basename(file_name)}')


def pixelate_images(block_size, directory, output_directory):
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    else:
        # If it exists, remove all its contents
        for filename in os.listdir(output_directory):
            file_path = os.path.join(output_directory, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

    # Iterate over all files in the directory
    for filename in tqdm(os.listdir(directory)):
        # Check if the file is an image
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            # Open the image using PIL
            image_path = os.path.join(directory, filename)
            image = Image.open(image_path)

            # Apply the average_color_pixelation function
            average_color_pixelation(image, block_size, output_directory)


block_size = 8
pixelate_images(block_size, 'images', 'pixelated_images')
