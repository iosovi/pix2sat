import numpy as np
import torch
from skimage.metrics import structural_similarity as ssim
from tqdm import tqdm
from PIL import Image
import os

from model_server.run_model import load_model, apply_model_to_image


class SSIM:
    def __init__(self, model_path, test_dir, model_type='unet'):
        self.model = load_model(model_path, model_type=model_type)
        self.test_dir = test_dir

    def __call__(self):
        total_ssim = 0.0
        num_images = 0

        for image_file in tqdm(os.listdir(self.test_dir)):
            image_path = os.path.join(self.test_dir, image_file)
            image = Image.open(image_path)

            width, height = image.size
            if image.size != (512, 256):
                print(f"\nSkipping over image {image_file} of size {image.size}\n")
                continue

            # Split the concatenated image into input and output images
            input_image = image.crop((0, 0, width // 2, height))
            real_image = image.crop((width // 2, 0, width, height))

            fake_image = apply_model_to_image(self.model, input_image)

            # Convert PIL Images to NumPy arrays
            input_array = np.array(real_image)
            real_array = np.array(fake_image)

            # Compute SSIM
            ssim_score = ssim(real_array, input_array, multichannel=True, channel_axis=2)

            # Accumulate SSIM score
            total_ssim += ssim_score
            num_images += 1

        # Calculate average SSIM
        average_ssim = total_ssim / num_images

        return average_ssim


# # Example usage
# model_path = R"C:\Users\lenovo\Desktop\pix2pix_2\latest_net_G.pth"
# test_dir = R"..\dataset\combined\test"
# image_processor = SSIM(model_path, test_dir)
# avg_ssim = image_processor.process_images()
# print("Average SSIM:", avg_ssim)
