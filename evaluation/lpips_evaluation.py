import lpips
import torch
from PIL import Image
import os
from torchvision import transforms
from tqdm import tqdm

from model_server.run_model import apply_model_to_image, load_model


class LPIPS:
    def __init__(self, model_path, test_path, net='alex', model_type='unet'):
        self.loss_fn = lpips.LPIPS(net=net)  # Can use 'alex' or 'vgg'
        self.model = load_model(model_path, model_type=model_type)
        self.test_path = test_path

    def __call__(self):
        # Get the list of image filenames in the test directory
        test_files = os.listdir(self.test_path)

        # Calculate LPIPS distance for each pair of images
        total_distance = 0.0
        num_pairs = 0

        for i in tqdm(range(0, len(test_files))):
            # Load the input and output images
            image_path = os.path.join(self.test_path, test_files[i])
            image = Image.open(image_path)

            if image.size != (512, 256):
                print(f"Skipping over image {test_files[i]} of size {image.size}")
                continue

            width, height = image.size
            half_width = width // 2

            # Split the concatenated image into input and output images
            input_image = image.crop((0, 0, half_width, height))
            real_image = image.crop((half_width, 0, width, height))

            # Generate the corresponding satellite image using your model
            generated_img = apply_model_to_image(self.model, input_image)

            # Convert images to PyTorch tensors and add a batch dimension
            transform = transforms.ToTensor()
            input_tensor = torch.unsqueeze(transform(real_image), 0)
            generated_tensor = torch.unsqueeze(transform(generated_img), 0)

            # Compute LPIPS distance
            distance = self.loss_fn.forward(input_tensor, generated_tensor)

            # Accumulate the distance
            total_distance += distance.item()
            num_pairs += 1

        # Calculate the average LPIPS distance
        average_distance = total_distance / num_pairs

        return average_distance


# model_path = R"F:\runs\pix2pix_base\latest_net_G.pth"
# test_path = R'..\dataset\combined\test'
# lpips_eval = LPIPS(model_path, test_path, net='alex')
# avg_dist = lpips_eval()
# print('Average LPIPS distance: ', avg_dist)
