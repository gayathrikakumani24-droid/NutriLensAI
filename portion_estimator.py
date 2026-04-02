import torch
import cv2
import numpy as np

# Load MiDaS (depth model)
midas = torch.hub.load("intel-isl/MiDaS", "MiDaS_small")
midas.eval()

transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
transform = transforms.small_transform


def estimate_portion(image):

    img = np.array(image)
    
    input_batch = transform(img)

    with torch.no_grad():
        depth = midas(input_batch)

    depth = torch.nn.functional.interpolate(
        depth.unsqueeze(1),
        size=img.shape[:2],
        mode="bicubic",
        align_corners=False,
    ).squeeze()

    depth_map = depth.cpu().numpy()

    # Simple threshold segmentation (food region)
    mask = depth_map > np.percentile(depth_map, 60)

    food_volume = np.sum(depth_map * mask)
    total_volume = np.sum(depth_map)

    portion_ratio = food_volume / total_volume

    # Assume standard portion = 300g
    estimated_grams = portion_ratio * 300

    return round(estimated_grams, 2)