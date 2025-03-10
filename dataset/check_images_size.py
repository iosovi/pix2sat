# specify the directory and the target size
import os

from PIL import Image

image_directory = R'C:\Users\lenovo\Desktop\Licenta\licenta\dataset\images'
target_size = (256, 256)

for filename in os.listdir(image_directory):
    if filename.endswith(".png"):
        img_path = os.path.join(image_directory, filename)
        with Image.open(img_path) as img:
            width, height = img.size
            if (width, height) != target_size:
                print(f"The image {filename} does not have the target size {target_size}. Its size is {(width, height)}")