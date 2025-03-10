import os
import shutil

from PIL import Image
from tqdm import tqdm
from colorspacious import cspace_convert


def rgb_to_lab(rgb_color):
    return cspace_convert(rgb_color, "sRGB255", "CIELab")


def lab_distance(lab1, lab2):
    return sum((lab1[i] - lab2[i]) ** 2 for i in range(3))


def closest_color(pixel, color_set):
    min_distance = float('inf')
    closest = None

    lab_pixel = rgb_to_lab(pixel)
    lab_color_set = [rgb_to_lab(color) for color in color_set]

    for i, lab_color in enumerate(lab_color_set):
        distance = lab_distance(lab_pixel, lab_color)

        if distance < min_distance:
            min_distance = distance
            closest = color_set[i]

    return closest


def recolor_pixelated(input_folder, output_folder, color_set, block_size=(8, 8)):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    else:
        # If it exists, remove all its contents
        for filename in os.listdir(output_folder):
            file_path = os.path.join(output_folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

    for img_name in tqdm(os.listdir(input_folder)):
        img_path = os.path.join(input_folder, img_name)
        img = Image.open(img_path)

        img_width, img_height = img.size

        for y in range(0, img_height, block_size[1]):
            for x in range(0, img_width, block_size[0]):
                # Get the current block color
                block_color = img.getpixel((x, y))
                # Find the closest color from the color set
                new_color = closest_color(block_color, color_set)
                # Replace the block with the new color
                for j in range(y, min(y + block_size[1], img_height)):
                    for i in range(x, min(x + block_size[0], img_width)):
                        img.putpixel((i, j), new_color)

        # Save the modified image
        img.save(os.path.join(output_folder, img_name))


if __name__ == "__main__":
    colors = [
        (5, 31, 76),  # DEEP OCEAN
        (236, 189, 163),  # SAND
        (150, 199, 137),  # LIGHT FOREST
        (16, 47, 62),  # DARK FOREST
        (135, 94, 58),  # LIGHT MOUNTAIN
        (90, 62, 35),  # DARK MOUNTAIN
        (255, 255, 255),  # SNOW
    ]

    recolor_pixelated("pixelated_images", "segmented_images", colors)
