import os
from PIL import Image
from torch.utils.data import Dataset


class CustomDataset(Dataset):
    def __init__(self, root_dir, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        self.file_list = os.listdir(self.root_dir)  # Assumes all files in root_dir are images.

    def __len__(self):
        return len(self.file_list)

    def __getitem__(self, idx):
        # Load image
        img_path = os.path.join(self.root_dir, self.file_list[idx])
        img = Image.open(img_path)

        # Split image into pixelated input and real output
        width, height = img.size
        pixelated_input = img.crop((0, 0, width // 2, height))
        real_output = img.crop((width // 2, 0, width, height))

        # Apply transforms if any
        if self.transform:
            pixelated_input = self.transform(pixelated_input)
            real_output = self.transform(real_output)

        return pixelated_input, real_output
