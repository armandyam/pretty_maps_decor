# Pretty maps wall decor

This repository contains a script that produces the image based on [pretty maps](https://github.com/marceloprates/prettymaps) and crops them into hexagonal shapes. This was used this to create a wall decoration based on the location of places stayed in previously. The maps generated were cut into hexagonal shapes and printed and stuck onto these [pin boards](https://www.amazon.de/dp/B07JNNM31F?psc=1&ref=ppx_yo2ov_dt_b_product_details). This is useful for creating custom map visuals on the wall. The main challenge was to convert the generated image onto the correct size for printing.

## Installation

1. Clone the repository:
    ```
    git clone https://github.com/armandyam/pretty_maps_decor.git
    cd pretty_maps_decor
    ```

2. Install the required packages:
    ```
    pip install -r requirements.txt
    ```

## Usage

### Generating and Cropping Images

To generate and crop images based on location data specified in a JSON file:

1. Ensure your `locations.json` file is in the root directory and follows this format:
    ```json
    {
        "Location1": "Address1",
        "Location2": ["latitude_value", "longitude_value"]
    }
    ```

2. Run the script:
    ```
    python main_script.py
    ```


