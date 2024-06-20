import os
import logging
import json
from typing import Tuple, Union, Dict
from PIL import Image, ImageDraw
import numpy as np
import matplotlib.pyplot as plt
from prettymaps import plot

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def add_margin(pil_img: Image.Image, top: int, right: int, bottom: int, left: int,
               color: Union[int, Tuple[int, int, int]]) -> Image.Image:
    """
    Add margin to a PIL image.

    Args:
        pil_img (Image.Image): The original image to which the margin will be added.
        top (int): The size of the top margin.
        right (int): The size of the right margin.
        bottom (int): The size of the bottom margin.
        left (int): The size of the left margin.
        color (Union[int, Tuple[int, int, int]]): The color of the margin. Can be an integer or a tuple representing RGB values.

    Returns:
        Image.Image: The new image with added margins.
    """
    logging.info(f"Adding margin: top={top}, right={right}, bottom={bottom}, left={left}, color={color}")
    width, height = pil_img.size
    new_width = width + right + left
    new_height = height + top + bottom
    result = Image.new(pil_img.mode, (new_width, new_height), color)
    result.paste(pil_img, (left, top))
    return result


def polycut(name: str, directory: str) -> None:
    """
    Crop an image to a hexagonal shape and save it.

    Args:
        name (str): The name of the image file (without extension).
        directory (str): The folder where the image file is located and where the output will be saved.

    Returns:
        None
    """
    logging.info(f"Processing image: name={name}, directory={directory}")
    file_path = os.path.join(directory, name)
    extensions = ['.png', '.jpeg', '.jpg']
    file_name = next((file_path + ext for ext in extensions if os.path.isfile(file_path + ext)), None)

    if not file_name:
        logging.error(f"Image file for {name} not found in {directory}")
        return

    im = Image.open(file_name).convert("RGBA")
    width, height = im.size
    dim = min(width, height)

    if width > height:
        min_x = (width - height) / 2
        im = im.crop((min_x, 0, min_x + height, height))

    sz = im.size
    width = sz[0]
    height = sz[1]
    factor = 1.0 / np.sqrt(3.0) if width > height else 1.0 / 2.0
    r = dim * factor
    req_width = 17.0
    page_width = 20.0
    padding_factor = int(np.floor((width * (page_width / req_width - 1.0)) / 2.0))

    im_padded = add_margin(im, padding_factor, padding_factor, padding_factor, padding_factor, (255, 255, 255))
    im_array = np.asarray(im_padded)

    polygon = []
    for i in range(6):
        theta = i * 2.0 * np.pi / 6.0
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        polygon.append((x + im_padded.width / 2.0, y + im_padded.height * 0.89 / 2.0))

    mask_im = Image.new('L', (im_array.shape[1], im_array.shape[0]), 0)
    ImageDraw.Draw(mask_im).polygon(polygon, outline=1, fill=1)
    mask = np.array(mask_im)

    new_im_array = np.empty(im_array.shape, dtype='uint8')
    new_im_array[:, :, :3] = im_array[:, :, :3]
    new_im_array[:, :, 3] = mask * 255

    new_im = Image.fromarray(new_im_array, "RGBA")

    output_dir = directory
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logging.info(f"Created directory: {output_dir}")

    new_im.save(os.path.join(output_dir, name + "_hex.png"))
    logging.info(f"Saved hexagonal image: {os.path.join(output_dir, name + '_hex.png')}")


def save_images(loc: Union[str, Tuple[float, float]], name: str, output_dir: str) -> None:
    """
    Generate and save an image of a location.

    Args:
        loc (Union[str, Tuple[float, float]]): The location to generate the image for. Can be an address or a tuple of coordinates.
        name (str): The name of the output image file.
        output_dir (str): The folder where the output image will be saved.

    Returns:
        None
    """
    logging.info(f"Generating image for location: {loc}, name: {name}")
    fig, ax = plt.subplots(figsize=(12, 12), constrained_layout=True)
    layers = plot(
        loc, radius=300,
        ax=ax,
        layers={
            'perimeter': {'circle': False, 'dilate': 0},
            'streets': {
                'width': {
                    'motorway': 5,
                    'trunk': 5,
                    'primary': 4.5,
                    'secondary': 4,
                    'tertiary': 3.5,
                    'residential': 3,
                    'service': 2,
                    'unclassified': 2,
                    'pedestrian': 2,
                    'footway': 1,
                }
            },
            'building': {'tags': {'building': True, 'landuse': 'construction'}, 'union': False},
            'water': {'tags': {'natural': ['water', 'bay']}},
            'green': {'tags': {'landuse': 'grass', 'natural': ['island', 'wood'], 'leisure': 'park'}},
            'forest': {'tags': {'landuse': 'forest'}},
            'parking': {'tags': {'amenity': 'parking', 'highway': 'pedestrian', 'man_made': 'pier'}}
        },
        drawing_kwargs={
            'background': {'fc': '#F2F4CB', 'ec': '#dadbc1', 'hatch': 'ooo...', 'zorder': -1},
            'perimeter': {'fc': '#F2F4CB', 'ec': '#dadbc1', 'lw': 0, 'hatch': 'ooo...', 'zorder': 0},
            'green': {'fc': '#D0F1BF', 'ec': '#2F3737', 'lw': 1, 'zorder': 1},
            'forest': {'fc': '#64B96A', 'ec': '#2F3737', 'lw': 1, 'zorder': 1},
            'water': {'fc': '#a1e3ff', 'ec': '#2F3737', 'hatch': 'ooo...', 'hatch_c': '#85c9e6', 'lw': 1, 'zorder': 2},
            'parking': {'fc': '#F2F4CB', 'ec': '#2F3737', 'lw': 1, 'zorder': 3},
            'streets': {'fc': '#2F3737', 'ec': '#475657', 'alpha': 1, 'lw': 0, 'zorder': 3},
            'building': {'palette': ['#FFC857', '#E9724C', '#C5283D'], 'ec': '#2F3737', 'lw': .5, 'zorder': 4},
        },
    )

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logging.info(f"Created directory: {output_dir}")

    plt.savefig(os.path.join(output_dir, name + ".png"), dpi=500)
    logging.info(f"Saved image: {os.path.join(output_dir, name + '.png')}")


def load_locations(file_path: str) -> Dict[str, Union[str, Tuple[float, float]]]:
    """
    Load location data from a JSON file and convert coordinate lists to tuples.

    Args:
        file_path (str): Path to the JSON file containing location data.

    Returns:
        dict: Dictionary of location names and their corresponding addresses or coordinates as tuples.
    """
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Convert coordinate lists to tuples
    for key, value in data.items():
        if isinstance(value, list):
            data[key] = tuple(value)

    return data


if __name__ == '__main__':
    loc_names = load_locations('locations.json')
    output_dir = "output"

    for name, loc in loc_names.items():
        save_images(loc, name, output_dir)
        polycut(name, output_dir)
