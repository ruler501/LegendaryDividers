import os

import pdf2image
import yaml

from typing import List

DIVIDER_WIDTH = 728
DIVIDER_HEIGHT = 592
DIVIDER_MARGIN_HEIGHT = 100
DIVIDER_MARGIN_WIDTH = 80
DIVIDER_OFFSET_HEIGHT = 100
DIVIDER_OFFSET_WIDTH = 90
LABEL_HEIGHT = 72


def extract_images(filename: str, names: List[str], width: int = 2, height: int = 3):
    if not os.path.exists("temp"):
        os.makedirs("temp")
    if not os.path.exists("output"):
        os.makedirs("output")
    pages = pdf2image.convert_from_path(filename, output_folder="temp")

    for page_number, page in enumerate(pages):
        for y_index in range(height):
            for x_index in range(width):
                index = width * height * page_number + width * y_index + x_index
                if index >= len(names):
                    return
                x = DIVIDER_OFFSET_WIDTH + x_index * (DIVIDER_WIDTH + DIVIDER_MARGIN_WIDTH)
                y = DIVIDER_OFFSET_HEIGHT + y_index * (DIVIDER_HEIGHT + DIVIDER_MARGIN_HEIGHT)
                result = page.crop((x, y + LABEL_HEIGHT, x + DIVIDER_WIDTH, y + DIVIDER_HEIGHT))
                name = names[index]
                print(name)
                result.save(f"output/{name}.png")


if __name__ == "__main__":
    data = []
    with open("image_source.yaml") as image_source:
        data = yaml.load(image_source)
    for source_file in data:
        extract_images(source_file["path"], source_file["names"])
