import os
from PIL import Image
from tqdm import tqdm


def augment_images(directory_path, output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    new_folder_current_id = 1

    for filename in tqdm(os.listdir(directory_path)):
        if filename.endswith(".jpg") or filename.endswith(".png"):  # Add/modify image extensions as needed.
            img_path = os.path.join(directory_path, filename)
            img = Image.open(img_path)

            img.save(os.path.join(output_directory, str(new_folder_current_id).zfill(5) + '.png'))
            new_folder_current_id += 1

            rotate_90_img = img.rotate(90)
            rotate_90_img.save(os.path.join(output_directory, str(new_folder_current_id).zfill(5) + '.png'))
            new_folder_current_id += 1

            rotate_90_img = img.rotate(180)
            rotate_90_img.save(os.path.join(output_directory, str(new_folder_current_id).zfill(5) + '.png'))
            new_folder_current_id += 1

            rotate_90_img = img.rotate(270)
            rotate_90_img.save(os.path.join(output_directory, str(new_folder_current_id).zfill(5) + '.png'))
            new_folder_current_id += 1

            lr_flip_img = img.transpose(Image.FLIP_LEFT_RIGHT)
            lr_flip_img.save(os.path.join(output_directory, str(new_folder_current_id).zfill(5) + '.png'))
            new_folder_current_id += 1
            lr_flip_90_img = lr_flip_img.rotate(90)
            lr_flip_90_img.save(os.path.join(output_directory, str(new_folder_current_id).zfill(5) + '.png'))
            new_folder_current_id += 1

            ud_flip_img = img.transpose(Image.FLIP_TOP_BOTTOM)
            ud_flip_img.save(os.path.join(output_directory, str(new_folder_current_id).zfill(5) + '.png'))
            new_folder_current_id += 1
            ud_flip_90_img = ud_flip_img.rotate(90)
            ud_flip_90_img.save(os.path.join(output_directory, str(new_folder_current_id).zfill(5) + '.png'))
            new_folder_current_id += 1


# Usage:
augment_images('segmented_images', 'augmented_segmented_images')
