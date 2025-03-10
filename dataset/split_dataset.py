import os
import random
import shutil


def split_dataset(folder_name_A, folder_name_B, split_percent):

    # Create a new directory for the split dataset
    split_folder_name_A = folder_name_A + "_split"
    split_folder_name_B = folder_name_B + "_split"

    if os.path.exists(split_folder_name_A):
        shutil.rmtree(split_folder_name_A)

    if os.path.exists(split_folder_name_B):
        shutil.rmtree(split_folder_name_B)

    os.mkdir(split_folder_name_A)
    os.mkdir(split_folder_name_B)

    # Create subdirectories for train and test sets
    train_folder_A = os.path.join(split_folder_name_A, "train")
    train_folder_B = os.path.join(split_folder_name_B, "train")
    os.mkdir(train_folder_A)
    os.mkdir(train_folder_B)
    test_folder_A = os.path.join(split_folder_name_A, "test")
    test_folder_B = os.path.join(split_folder_name_B, "test")
    os.mkdir(test_folder_A)
    os.mkdir(test_folder_B)

    # Get a list of all the image files in the original folder
    image_files_A = [f for f in os.listdir(folder_name_A) if os.path.isfile(os.path.join(folder_name_A, f))]
    image_files_B = [f for f in os.listdir(folder_name_B) if os.path.isfile(os.path.join(folder_name_B, f))]

    assert(len(image_files_A) == len(image_files_B))

    image_count = len(image_files_A)

    combined_files = list(zip(image_files_A, image_files_B))

    # Shuffle the image file list
    random.shuffle(combined_files)

    image_files_A, image_files_B = zip(*combined_files)

    # Split the image files into train and test sets
    split_index = int(image_count * split_percent)
    train_images_A = image_files_A[:split_index]
    train_images_B = image_files_B[:split_index]
    test_images_A = image_files_A[split_index:]
    test_images_B = image_files_B[split_index:]

    # Copy the train images to the train folder A
    for image_name in train_images_A:
        source_path = os.path.join(folder_name_A, image_name)
        destination_path = os.path.join(train_folder_A, image_name)
        shutil.copyfile(source_path, destination_path)

    # Copy the train images to the train folder B
    for image_name in train_images_B:
        source_path = os.path.join(folder_name_B, image_name)
        destination_path = os.path.join(train_folder_B, image_name)
        shutil.copyfile(source_path, destination_path)

    # Copy the test images to the test folder A
    for image_name in test_images_A:
        source_path = os.path.join(folder_name_A, image_name)
        destination_path = os.path.join(test_folder_A, image_name)
        shutil.copyfile(source_path, destination_path)

    # Copy the test images to the test folder B
    for image_name in test_images_B:
        source_path = os.path.join(folder_name_B, image_name)
        destination_path = os.path.join(test_folder_B, image_name)
        shutil.copyfile(source_path, destination_path)

    print(f"Folder A : {folder_name_A}")
    print(f"Original image folder: {len(image_files_A)} images")
    print(f"Train image folder: {len(train_images_A)} images")
    print(f"Test image folder: {len(test_images_A)} images")
    print(f"Lost images in split: {len(image_files_A) - (len(train_images_A) + len(test_images_A))}")
    print("---------------------------------")
    print(f"Folder A : {folder_name_B}")
    print(f"Original image folder: {len(image_files_B)} images")
    print(f"Train image folder: {len(train_images_B)} images")
    print(f"Test image folder: {len(test_images_B)} images")
    print(f"Lost images in split: {len(image_files_B) - (len(train_images_B) + len(test_images_B))}")


if __name__ == '__main__':
    folder_name_A = "augmented_segmented_images"
    folder_name_B = "augmented_images"
    split_percent = 0.9
    split_dataset(folder_name_A, folder_name_B, split_percent)
