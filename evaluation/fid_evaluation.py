import numpy as np
import torch
from torch.utils.data import DataLoader
from torchvision.transforms import transforms
from tqdm import tqdm
from scipy import linalg
from InceptionV3 import InceptionV3
from evaluation.CustomDataset import CustomDataset
from model_server.run_model import load_model


class FID:
    def __init__(self, model_path, test_path, model_type='unet'):
        self.model = InceptionV3([3], normalize_input=False)
        self.test_model = load_model(model_path, model_type, verbose=True)
        self.test_path = test_path

    def __call__(self, batch_size=8):

        transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(256),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
        ])

        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

        self.model.to(device).eval()
        self.test_model.to(device).eval()

        all_real_features = []
        all_fake_features = []

        dataset = CustomDataset(root_dir=self.test_path, transform=transform)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True, drop_last=True)
        for data in tqdm(dataloader, total=len(dataloader)):
            with torch.no_grad():
                pixelated_input, real_output = data

                pixelated_input = pixelated_input.to(device)
                real_output = real_output.to(device)

                fake_output = self.test_model(pixelated_input)

                fake_output = fake_output.squeeze(0)
                fake_output = (fake_output + 1) / 2.0

                real_features = self.model(real_output)[-1].squeeze()
                fake_features = self.model(fake_output)[-1].squeeze()

                all_real_features.append(real_features)
                all_fake_features.append(fake_features)

        all_real_features = torch.cat(all_real_features, dim=0)
        all_fake_features = torch.cat(all_fake_features, dim=0)

        real_mean = all_real_features.mean(dim=0)
        real_cov = torch.matmul((all_real_features - real_mean).T, (all_real_features - real_mean)) / (len(all_real_features) - 1)

        fake_mean = all_fake_features.mean(dim=0)
        fake_cov = torch.matmul((all_fake_features - fake_mean).T, (all_fake_features - fake_mean)) / (len(all_fake_features) - 1)

        fid_score = self.calculate_frechet_distance(real_mean, real_cov, fake_mean, fake_cov)
        return fid_score

    def calculate_frechet_distance(self, mu1, sigma1, mu2, sigma2, eps=1e-6):
        """Numpy implementation of the Frechet Distance.
                The Frechet distance between two multivariate Gaussians X_1 ~ N(mu_1, C_1)
                and X_2 ~ N(mu_2, C_2) is
                        d^2 = ||mu_1 - mu_2||^2 + Tr(C_1 + C_2 - 2*sqrt(C_1*C_2)).

                Stable version by Dougal J. Sutherland.

                Params:
                -- mu1   : Numpy array containing the activations of a layer of the
                           inception net (like returned by the function 'get_predictions')
                           for generated samples.
                -- mu2   : The sample mean over activations, precalculated on an
                           representative data set.
                -- sigma1: The covariance matrix over activations for generated samples.
                -- sigma2: The covariance matrix over activations, precalculated on an
                           representative data set.

                Returns:
                --   : The Frechet Distance.
                """

        # convert pytorch tensors to numpy arrays
        mu1 = mu1.cpu().numpy()
        mu2 = mu2.cpu().numpy()
        sigma1 = sigma1.cpu().numpy()
        sigma2 = sigma2.cpu().numpy()

        mu1 = np.atleast_1d(mu1)
        mu2 = np.atleast_1d(mu2)

        sigma1 = np.atleast_2d(sigma1)
        sigma2 = np.atleast_2d(sigma2)

        assert mu1.shape == mu2.shape, \
            'Training and test mean vectors have different lengths'
        assert sigma1.shape == sigma2.shape, \
            'Training and test covariances have different dimensions'

        diff = mu1 - mu2

        # Product might be almost singular
        covmean, _ = linalg.sqrtm(sigma1.dot(sigma2), disp=False)
        if not np.isfinite(covmean).all():
            msg = ('fid calculation produces singular product; '
                   'adding %s to diagonal of cov estimates') % eps
            print(msg)
            offset = np.eye(sigma1.shape[0]) * eps
            covmean = linalg.sqrtm((sigma1 + offset).dot(sigma2 + offset))

        # Numerical error might give slight imaginary component
        if np.iscomplexobj(covmean):
            if not np.allclose(np.diagonal(covmean).imag, 0, atol=1e-3):
                m = np.max(np.abs(covmean.imag))
                raise ValueError('Imaginary component {}'.format(m))
            covmean = covmean.real

        tr_covmean = np.trace(covmean)

        return (diff.dot(diff) + np.trace(sigma1)
                + np.trace(sigma2) - 2 * tr_covmean)


# if __name__ == "__main__":
#     model_path = R"F:\runs\pix2sat_resnet\latest_net_G.pth"
#     test_path = R'..\dataset\combined\test'
#     fid = FID(model_path, test_path)
#     fid_score = fid()
#     print('FID score: ', fid_score)
