import configparser
import os

config = configparser.ConfigParser()
config.read("metadata.ini")


def check_folder(folder_path):
    result = True
    for i in range(1, int(config['DEFAULT']['ImageCount']) * 8 + 1):
        file_name = f'{str(i).zfill(5)}.png'
        file_path = os.path.join(folder_path, file_name)
        if not os.path.isfile(file_path):
            print(f"FILE MISSING: {file_name}")
            result = False
    return result


if __name__ == "__main__":
    folder = 'augmented_images'
    if check_folder(folder):
        print('All files are present')
    else:
        print('Some files are missing')
