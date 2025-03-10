import configparser
import contextlib
import io
import os
import random
import signal

import ee
import geemap
import numpy as np
import rasterio
from PIL import Image
from tqdm import tqdm

# Initialize the Earth Engine API
ee.Initialize()
config = configparser.ConfigParser()
config.read("metadata.ini")


def stopping_handler(sig, frame):
    print("Saving metadata to file...")
    with open('metadata.ini', 'w') as f:
        config.write(f)


signal.signal(signal.SIGINT, stopping_handler)


class Area:
    def __init__(self, label, lat_min, lat_max, lon_min, lon_max):
        self.label = label
        self.lat_min = lat_min
        self.lat_max = lat_max
        self.lon_min = lon_min
        self.lon_max = lon_max


def generate_file_number(num, max_number=10000):
    num_digits = len(str(max_number))
    return str(num).zfill(num_digits)


def generate_coordinates(area: Area):
    latitude_range = (area.lat_min, area.lat_max)
    longitude_range = (area.lon_min, area.lon_max)
    latitude = random.uniform(latitude_range[0], latitude_range[1])
    longitude = random.uniform(longitude_range[0], longitude_range[1])
    return latitude, longitude


# Define the cloud mask function
def mask_s2_clouds(image):
    qa = image.select('QA60')
    cloud_bit_mask = 1 << 10
    cirrus_bit_mask = 1 << 11
    mask = qa.bitwiseAnd(cloud_bit_mask).eq(0).And(qa.bitwiseAnd(cirrus_bit_mask).eq(0))
    return image.updateMask(mask).divide(10000)


def check_land(region, resolution, check_water):
    land_cover = ee.Image('MODIS/006/MCD12Q1/2013_01_01').select('LC_Type1')

    # Clip the land cover dataset to the region of interest
    clipped_land_cover = land_cover.clip(region)

    # Define a water mask (MODIS land cover type 17 represents water)
    water_mask = clipped_land_cover.eq(17)

    # Define a land mask by selecting non-water pixels (value != 17)
    land_mask = clipped_land_cover.neq(17)

    # Calculate the number of water and land pixels in the region
    water_pixel_count = water_mask.reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=region,
        scale=resolution  # Adjust the scale based on the resolution of the dataset
    ).getInfo()['LC_Type1']

    land_pixel_count = land_mask.reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=region,
        scale=resolution  # Adjust the scale based on the resolution of the dataset
    ).getInfo()['LC_Type1']

    # Determine if there is both water and land in the region
    has_water = water_pixel_count > 0
    has_land = land_pixel_count > 0

    result = has_land

    if check_water:
        result = result and has_water

    return result


def generate_region(area_of_interest, resolution, water_probability=0.5):

    region_found = False
    region = None

    # Water should be present in the photo approximately 50% of the time
    check_water = random.random() < water_probability

    while not region_found:
        # Central point coordinates
        lat, lon = generate_coordinates(area_of_interest)

        # Convert resolution to degrees (assuming Earth's circumference is approximately 40,000 km)
        degrees_per_pixel = (resolution / 1000) / 111.32

        # Calculate the region's width and height in degrees based on the desired image size
        width_degrees = 256 * degrees_per_pixel
        height_degrees = 256 * degrees_per_pixel

        # Define the region based on the central point and the calculated width and height
        region = ee.Geometry.Rectangle([lon - width_degrees / 2, lat - height_degrees / 2,
                                        lon + width_degrees / 2, lat + height_degrees / 2])

        region_found = check_land(region, resolution, check_water)

    return region


def create_satellite_image_dataset_from_area(
        area_of_interest: Area,
        image_count: int,
        resolution: int,
        filepath: str,
        prefix: str = "sat_img_"):
    current_image_count = int(config['DEFAULT']['ImageCount'])

    # Load Sentinel-2 TOA reflectance data
    dataset = ee.ImageCollection('COPERNICUS/S2') \
        .filterDate('2020-01-01', '2022-12-31') \
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 5)) \
        .map(mask_s2_clouds)

    for i in tqdm(range(image_count)):

        region = generate_region(area_of_interest, resolution)
        image_dataset = dataset.median().clip(region)

        # Define the visualization parameters
        rgb_vis = {
            'min': 0.05,
            'max': 0.25,
            'bands': ['B4', 'B3', 'B2']
        }

        # Apply the visualization parameters
        image = image_dataset.visualize(**rgb_vis)

        with io.StringIO() as buffer, contextlib.redirect_stdout(buffer):
            geemap.ee_export_image(image, filename='temp_output_map.tif', scale=resolution, region=region)

        # Read the GeoTIFF file using rasterio
        with rasterio.open('temp_output_map.tif') as src:
            img_array = src.read()

        # Rearrange dimensions (bands, height, width) -> (height, width, bands)
        img_array = np.transpose(img_array, (1, 2, 0))

        # Convert the image to 8-bit format
        img_array = np.uint8(img_array)

        # Scale to 256 by 256
        img_array = img_array[:-1, :-1, :]

        # Save the image using PIL
        output_img = Image.fromarray(img_array)

        if output_img.size != (256, 256):
            i -= 1
        else:
            output_img.save(f'{filepath}/{prefix}{generate_file_number(i + 1 + current_image_count)}.png')

            # Update config file
            config['DEFAULT']['ImageCount'] = str(int(config['DEFAULT']['ImageCount']) + 1)

            with open('metadata.ini', 'w') as f:
                config.write(f)

    os.remove("temp_output_map.tif")


area_1 = Area(
    "Greece and Turkey",
    lat_min=35.75625605330991,
    lat_max=40.53618394741599,
    lon_min=20.576025383691217,
    lon_max=40.769369740322986
)

area_2 = Area(
    "Italy-Greece-Turkey",
    lat_min=36.591221576321274,
    lat_max=45.093719372911494,
    lon_min=13.418242070758168,
    lon_max=36.59010575757779
)


if __name__ == "__main__":
    # Desired zoom_level (meters per pixel)
    zoom_level = 150
    image_target_count = 14
    create_satellite_image_dataset_from_area(
        area_2,
        image_target_count,
        zoom_level,
        "images"
    )
