import os

import pdf2image
import yaml

from typing import List

from divider import DIVIDER_WIDTH, DIVIDER_HEIGHT, DIVIDER_MARGIN_HEIGHT, DIVIDER_MARGIN_WIDTH, DIVIDER_OFFSET_HEIGHT,\
    DIVIDER_OFFSET_WIDTH, LABEL_HEIGHT


def extract_images(filename: str, names: List[str], width: int = 2, height: int = 3):
    if not os.path.exists("temp"):
        os.makedirs("temp")
    if not os.path.exists("output"):
        os.makedirs("output")
    pages = pdf2image.convert_from_path(filename, output_folder="temp")

    for page_number, page in enumerate(pages):
        for x_index in range(width):
            for y_index in range(height):
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
