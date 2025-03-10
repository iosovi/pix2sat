from evaluation.fid_evaluation import FID
from evaluation.lpips_evaluation import LPIPS
from evaluation.ssim_evalutation import SSIM

model_path = R"F:\runs\pix2sat_final\latest_net_G.pth"
test_path = R'..\dataset\combined\test'

model_type = 'unet'

fid = FID(model_path, test_path, model_type=model_type)
ssim = SSIM(model_path, test_path, model_type=model_type)
lpips = LPIPS(model_path, test_path, net='alex', model_type=model_type)

print("Computing FID...")
fid_score = fid()
print(f"FID Score: {fid_score}")

print("Computing SSIM...")
ssim_score = ssim()
print(f"SSIM Score: {ssim_score}")

print("Computing LPIPS...")
lpips_score = lpips()
print(f"LPIPS Score: {lpips_score}")


