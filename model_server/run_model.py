import functools
from collections import OrderedDict

import torch
from PIL import Image
from torch import nn
from torchvision import transforms
from pix2pix_cyclegan.models.networks import UnetGenerator, ResnetGenerator, get_norm_layer, define_G, init_net


def load_model(model_path, model_type='unet', verbose=False):
    input_nc = 3  # Number of input channels
    output_nc = 3  # Number of output channels
    ngf = 64  # Number of filters in the last layer
    use_dropout = False
    net = None

    norm_layer = functools.partial(nn.BatchNorm2d, affine=True, track_running_stats=True)

    state_dict = torch.load(model_path)

    if model_type == 'unet':
        net = UnetGenerator(input_nc, output_nc, 8, ngf,
                            norm_layer=norm_layer,
                            use_dropout=use_dropout)

    if model_type == 'resnet':
        new_dict = OrderedDict()
        for k, v in state_dict.items():
            # load_state_dict expects keys with prefix 'module.'
            new_dict["module." + k] = v
        state_dict = new_dict
        # make sure you pass the correct parameters to the define_G method
        net = define_G(input_nc=3, output_nc=3, ngf=64, netG="resnet_9blocks",
                                   norm="batch", use_dropout=True, init_gain=0.02, gpu_ids=[0])

    net.load_state_dict(state_dict)
    net.eval()

    return net


def preprocess_image(img):
    preprocess = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(256),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
    ])

    img_tensor = preprocess(img)
    return img_tensor.unsqueeze(0)


def postprocess_output(output_tensor):
    output_tensor = output_tensor.squeeze(0)
    output_tensor = (output_tensor + 1) / 2.0
    output_img = transforms.ToPILImage()(output_tensor)
    return output_img


def apply_model_to_image(model, image):
    input_tensor = preprocess_image(image)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    with torch.no_grad():
        output_tensor = model(input_tensor)

    output_img = postprocess_output(output_tensor)

    return output_img


if __name__ == "__main__":
    model_path = R"F:\runs\pix2sat_resnet\latest_net_G.pth"
    input_image = Image.open(R"C:\Users\lenovo\Desktop\epoch046_real_A.png")
    model = load_model(model_path, model_type='resnet', verbose=True)
    output_image = apply_model_to_image(model, input_image)
    output_image.save(R"C:\Users\lenovo\Desktop\epoch046_real_A_output.png")
