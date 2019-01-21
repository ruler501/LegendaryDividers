import math
import os
import textwrap

import yaml

from collections import Counter
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont
from typing import List, Mapping, Tuple, Union


class Divider:
    def __init__(self, formatting: Mapping, properties: Mapping):
        self.format = formatting
        self.properties = properties

    @staticmethod
    def load(filename: str) -> Tuple[List["Divider"], Mapping]:
        with open(filename) as source_file:
            data = yaml.load(source_file)
        global_values = {
            "grid_lines": data["grid_lines"],
            "grid_width": data["grid_width"],
            "grid_spacing": data["grid_spacing"],
            "double_sided": data["double_sided"],
            "separate_docs": data["separate_docs"],
            "width_count": data["width_count"],
            "height_count": data["height_count"],
            "page_width": data["page_width"],
            "page_height": data["page_height"],
            "divider_width": data["divider_width"],
            "divider_height": data["divider_height"],
            "offset_height": data["offset_height"],
            "offset_width": data["offset_width"],
            "margin_width": data["margin_width"],
            "margin_height": data["margin_height"]
            }
        formatting = data["format"]
        populate_from_rarities = data["populate_from_rarities"]
        results: List[Divider] = []
        for card in data["cards"]:
            for rarity, count in populate_from_rarities["rarities"].items():
                if rarity not in card:
                    continue
                for source, property_name in populate_from_rarities["properties"].items():
                    if source not in card[rarity]:
                        continue
                    if property_name not in card:
                        card[property_name] = []
                    card[property_name] += [card[rarity][source]]*count
            results.append(Divider(formatting, card))
        return results, global_values

    @staticmethod
    def render_pages(dividers: List["Divider"], global_properties: Mapping):
        pages: List[Image] = []
        grid_lines = global_properties["grid_lines"]
        grid_width = global_properties["grid_width"]
        grid_spacing = global_properties["grid_spacing"]
        double_sided = global_properties["double_sided"]
        width = global_properties["width_count"]
        height = global_properties["height_count"]
        page_width = global_properties["page_width"]
        page_height = global_properties["page_height"]
        divider_width = global_properties["divider_width"]
        divider_height = global_properties["divider_height"]
        offset_height = global_properties["offset_height"]
        offset_width = global_properties["offset_width"]
        margin_width = global_properties["margin_width"]
        margin_height = global_properties["margin_height"]
        for page_number in range(int(math.ceil(len(dividers) / width / height))):
            page = Image.new("RGBA", (page_width, page_height), color="White")
            draw = ImageDraw.Draw(page)
            for x_index in range(width):
                should_break = False
                for y_index in range(height):
                    index = width * height * page_number + height * x_index + y_index
                    if index >= len(dividers):
                        should_break = True
                        break
                    divider = dividers[index]
                    x = offset_width + x_index * (divider_width + margin_width)
                    y = offset_height + y_index * (divider_height + margin_height)
                    div_image = divider.render()
                    page.paste(div_image, (x, y))
                    if grid_lines:
                        draw.line(((x - margin_width + grid_spacing, y-1), (x - grid_spacing, y-1)),
                                  fill="Black", width=grid_width)
                        draw.line(((x-1, y - margin_height + grid_spacing), (x-1, y - grid_spacing)),
                                  fill="Black", width=grid_width)
                        draw.line(((x - margin_width + grid_spacing, y + divider_height),
                                   (x - grid_spacing, y + divider_height)), fill="Black", width=grid_width)
                        draw.line(((x - 1, y + divider_height + grid_spacing),
                                   (x - 1, y + divider_height + margin_height - grid_spacing)),
                                  fill="Black", width=grid_width)
                        draw.line(((x + divider_width + grid_spacing, y - 1),
                                   (x + divider_width + margin_width - grid_spacing, y - 1)),
                                  fill="Black", width=grid_width)
                        draw.line(((x + divider_width, y - margin_height + grid_spacing),
                                   (x + divider_width, y - grid_spacing)), fill="Black", width=grid_width)
                        draw.line(((x + divider_width, y + divider_height + grid_spacing),
                                   (x + divider_width, y + divider_height + margin_height - grid_spacing)),
                                  fill="Black", width=grid_width)
                        draw.line(((x + divider_width + grid_spacing, y + divider_height),
                                   (x + divider_width + margin_width - grid_spacing, y + divider_height)),
                                  fill="Black", width=grid_width)
                if should_break:
                    break
            pages.append(page)
            if double_sided:
                page = Image.new("RGBA", (page_width, page_height), color="White")
                draw = ImageDraw.Draw(page)
                for x_index in range(width):
                    should_break = False
                    for y_index in range(height):
                        index = width * height * page_number + height * x_index + y_index
                        if index >= len(dividers):
                            should_break = True
                            break
                        divider = dividers[index]
                        x = offset_width + (width - x_index - 1) * (divider_width + margin_width)
                        y = offset_height + y_index * (divider_height + margin_height)
                        div_image = divider.render()
                        page.paste(div_image, (x, y))
                        if grid_lines:
                            draw.line(((x - margin_width + grid_spacing, y-1), (x - grid_spacing, y-1)),
                                      fill="Black", width=grid_width)
                            draw.line(((x-1, y - margin_height + grid_spacing), (x-1, y - grid_spacing)),
                                      fill="Black", width=grid_width)
                            draw.line(((x - margin_width + grid_spacing, y + divider_height),
                                       (x - grid_spacing, y + divider_height)), fill="Black", width=grid_width)
                            draw.line(((x - 1, y + divider_height + grid_spacing),
                                       (x - 1, y + divider_height + margin_height - grid_spacing)),
                                      fill="Black", width=grid_width)
                            draw.line(((x + divider_width + grid_spacing, y - 1),
                                       (x + divider_width + margin_width - grid_spacing, y - 1)),
                                      fill="Black", width=grid_width)
                            draw.line(((x + divider_width, y - margin_height + grid_spacing),
                                       (x + divider_width, y - grid_spacing)), fill="Black", width=grid_width)
                            draw.line(((x + divider_width, y + divider_height + grid_spacing),
                                       (x + divider_width, y + divider_height + margin_height - grid_spacing)),
                                      fill="Black", width=grid_width)
                            draw.line(((x + divider_width + grid_spacing, y + divider_height),
                                       (x + divider_width + margin_width - grid_spacing, y + divider_height)),
                                      fill="Black", width=grid_width)
                    if should_break:
                        break
                pages.append(page)
        return pages

    @staticmethod
    def resolve_position(position: Tuple[Union[int, str], Union[int, str]],
                         _: Tuple[Tuple[int, int], Tuple[int, int]], current_x: int, current_y: int) -> \
            Tuple[int, int]:
            result = []
            if position[0] == "auto":
                result.append(current_x)
            else:
                result.append(int(position[0]))
            if position[1] == "auto":
                result.append(current_y)
            else:
                result.append(int(position[1]))
            return result[0], result[1]

    def render_container(self, result: Image, draw: ImageDraw, draw_property: Mapping,
                         bounding_box: Tuple[Tuple[int, int], Tuple[int, int]], current_x: int, current_y: int,
                         backwards: bool) -> Tuple[int, int]:
        new_bounding_box = [self.resolve_position(draw_property["position"], bounding_box, current_x, current_y),
                            list(draw_property["size"])]
        # CodeReview: Need to handle that when backwards is set new_bounding_box[0][0] needs to be the right
        #   boundary not the left
        print(draw_property)
        print("ContainerPre", backwards, current_x, bounding_box, new_bounding_box)
        if new_bounding_box[1][0] == "auto":
            new_bounding_box[1][0] = bounding_box[1][0] - new_bounding_box[0][0] + bounding_box[0][0]
            if backwards:
                new_bounding_box[1][0] = current_x - bounding_box[1][0] + bounding_box[0][0]
                new_bounding_box[0][0] = bounding_box[1][0]
        if new_bounding_box[1][1] == "auto":
            new_bounding_box[1][1] = bounding_box[1][1] - new_bounding_box[0][1] + bounding_box[0][1]
        new_backwards = draw_property["backwards"]
        if new_backwards:
            current_x = new_bounding_box[0][0] + new_bounding_box[1][0]
        new_bounding_box = new_bounding_box[0], new_bounding_box[1]
        print("Container", new_backwards, new_bounding_box, current_x)
        for recursive_draw_property in draw_property["properties"]:
            prev_current_x = current_x
            prev_current_y = current_y
            cached_x = current_x
            current_x, current_y = self.render_property(result, draw, recursive_draw_property, new_bounding_box,
                                                        current_x, current_y, new_backwards)
            if prev_current_x != current_x:
                current_x += draw_property["spacing"] if not new_backwards else -draw_property["spacing"]
                print("XChanged", cached_x, current_x)
            if prev_current_y != current_y:
                current_y += draw_property["spacing"]
        return current_x, current_y

    def render_text(self, _: Image, draw: ImageDraw, draw_property: Mapping,
                    bounding_box: Tuple[Tuple[int, int], Tuple[int, int]], current_x: int, current_y: int,
                    backwards: bool) -> Tuple[int, int]:
        font = ImageFont.truetype(draw_property["font"], draw_property["font_size"])
        text = self.properties.get(draw_property["property"])
        current_x, current_y = self.resolve_position(draw_property["position"], bounding_box, current_x, current_y)
        if text is not None:
            background = self.properties.get(draw_property["background_property"])
            if background is None:
                background = draw_property["background_default"]
            text_color = self.properties.get(draw_property["text_color_property"])
            if text_color is None:
                text_color = draw_property["text_color_default"]
            text_width, text_height = draw.textsize(text, font)
            desired_width = draw_property["size"][0] if draw_property["size"][0] != "auto" else text_width
            desired_height = draw_property["size"][1] if draw_property["size"][1] != "auto" else text_height
            if backwards:
                current_x -= desired_width
            draw.rectangle(((current_x, current_y), (current_x + desired_width, current_y + desired_height)),
                           fill=background)
            # CodeReview: center between current_y and bottom of bounding box
            x_coord = (current_x + (desired_width - text_width) // 2) if draw_property["centered_width"] else current_x
            y_coord = (current_y + (desired_height - text_height) // 2) if draw_property["centered_height"] \
                else current_y
            draw.text((x_coord, y_coord), text, fill=text_color, font=font)
            current_x += desired_width
        elif draw_property["required"]:
            raise Exception(f"Missing required property: {draw_property['property']} from card {self.properties}")
        return current_x, current_y

    def render_list(self, result: Image, draw: ImageDraw, draw_property: Mapping,
                    bounding_box: Tuple[Tuple[int, int], Tuple[int, int]], current_x: int, current_y: int,
                    backwards: bool) -> Tuple[int, int]:
        theme_font = None
        if "text" in draw_property["type"]:
            theme_font = ImageFont.truetype(draw_property["font"], draw_property["font_size"])
        items = self.properties.get(draw_property["property"])
        current_x, current_y = self.resolve_position(draw_property["position"], bounding_box, current_x, current_y)
        size_x, size_y = draw_property["size"]
        if size_x == "auto":
            size_x = bounding_box[1][0] - current_x + bounding_box[0][0]
            if backwards:
                size_x = current_x - bounding_box[0][0]
        if size_y == "auto":
            size_y = bounding_box[1][1] - current_y + bounding_box[0][1]
        print(current_x, size_x, backwards)
        if backwards:
            current_x = current_x - size_x
        orientation = draw_property["orientation"]
        internal_current_y = current_y
        internal_current_x = current_x
        if items is not None:
            cached_current_x = current_x
            cached_current_y = current_y
            spacing = draw_property["spacing"]
            x_border = current_x + size_x
            y_border = current_y + size_y
            rows = draw_property["rows"]
            columns = draw_property["columns"]
            first = True
            # CodeReview: Specify an order that all will conform to
            for item in items:
                resource_name = f"resources/icons/{item}.png"
                if "icon" in draw_property["type"] and os.path.isfile(resource_name):
                    icon = Image.open(resource_name)
                    icon_width, icon_height = icon.size
                    icon = icon.resize((self.format["icon_height"] * icon_width // icon_height,
                                        self.format["icon_height"]), Image.HAMMING)
                    icon_width, icon_height = icon.size
                    x_coord = internal_current_x
                    y_coord = internal_current_y
                    if orientation == "horizontal":
                        if not first:
                            x_coord += spacing
                        first = False
                        if draw_property["centered_height"]:
                            y_coord += (size_y // (rows or 1) - icon_height) // 2
                    if orientation == "vertical":
                        if not first:
                            y_coord += spacing
                        first = False
                        if draw_property["centered_width"]:
                            x_coord += (size_x // (columns or 1) - icon_width) // 2
                    if orientation == "horizontal" and x_coord + icon_width > x_border \
                            and rows is not None and internal_current_y < current_y + (rows - 1) * (size_y // rows):
                        internal_current_y += size_y // rows
                        internal_current_x = cached_current_x
                        x_coord = internal_current_x
                        y_coord += size_y // rows
                    elif orientation == "vertical" and y_coord + icon_height > y_border \
                            and columns is not None and \
                            internal_current_x < current_x + (columns - 1) * (size_y // columns):
                        internal_current_x += size_x // rows
                        internal_current_y = cached_current_y
                    result.paste(icon, (x_coord, y_coord))
                    if orientation == "horizontal":
                        internal_current_x = x_coord + icon_width
                    elif orientation == "vertical":
                        internal_current_y = y_coord + icon_height
                elif "text" in draw_property["type"]:
                    text_width, text_height = draw.textsize(item, theme_font)
                    if draw_property["wrap"] is not None:
                        item = textwrap.fill(item, draw_property["wrap"])
                        text_width, text_height = draw.multiline_textsize(item, theme_font)
                    x_coord = internal_current_x
                    y_coord = internal_current_y
                    text_color = self.properties.get(draw_property["text_color_property"]) or \
                        draw_property["text_color_default"]
                    if draw_property["bulleted"]:
                        draw.ellipse((internal_current_x + spacing,
                                      internal_current_y + (text_height - draw_property["font_size"]) // 2,
                                      internal_current_x + spacing + draw_property["font_size"],
                                      internal_current_y + (text_height + draw_property["spacing"]) // 2),
                                     fill=text_color)
                        x_coord += spacing*2 + draw_property["font_size"]
                    if orientation == "horizontal":
                        if not first:
                            x_coord += spacing
                        first = False
                        if draw_property["centered_height"]:
                            y_coord += (size_y // (rows or 1) - text_height) // 2
                    if orientation == "vertical":
                        if not first:
                            y_coord += spacing
                        first = False
                        if draw_property["centered_width"]:
                            x_coord += (size_x // (columns or 1) - text_width) // 2
                    print(x_coord, text_width, x_border, cached_current_x, internal_current_y)
                    if orientation == "horizontal" and x_coord + text_width > x_border \
                            and rows is not None and internal_current_y < current_y + (rows - 1) * (size_y // rows):
                        internal_current_y += size_y // rows
                        internal_current_x = cached_current_x
                        x_coord = internal_current_x
                        y_coord += size_y // rows
                    elif orientation == "vertical" and y_coord + text_height > y_border \
                            and columns is not None and \
                            internal_current_x < current_x + (columns - 1) * (size_y // columns):
                        internal_current_x += size_x // rows
                        internal_current_y = cached_current_y
                    if draw_property["wrap"] is None:
                        draw.text((x_coord, y_coord), item, fill=text_color, font=theme_font)
                    else:
                        draw.multiline_text((x_coord, y_coord), item, fill=text_color, font=theme_font)

                    if orientation == "horizontal":
                        internal_current_x = x_coord + text_width
                    elif orientation == "vertical":
                        internal_current_y = y_coord + text_height
                else:
                    raise Exception(f"Could not find handler for {item} for {draw_property['type']}")
            if not backwards:
                current_x += size_x
            if orientation == "vertical":
                current_y += size_y
        else:
            if draw_property["required"]:
                raise Exception(f"Missing required property: {draw_property['property']} from card {self.properties}")
        return current_x, current_y

    def render_colorbar(self, _: Image, draw: ImageDraw, draw_property: Mapping,
                        _2: Tuple[Tuple[int, int], Tuple[int, int]], current_x: int, current_y: int,
                        backwards: bool) -> Tuple[int, int]:
        colors = self.properties.get(draw_property["property"])
        if colors is not None:
            color_distribution = Counter(colors)
            total_color = sum(amount for amount in color_distribution.values())
            if total_color > 0:
                color_value = {"Y": 0, "U": 1, "B": 2, "R": 3, "G": 4, "YU": 5, "UB": 6, "BR": 7, "RG": 8, "GY": 9,
                               "YB": 10, "UR": 11, "BG": 12, "RY": 13, "GU": 14, "E": 15, "W": 16
                               }
                color_to_color = {"Y": "#dea319", "U": "#01a1d5", "B": "#a6a8ab", "R": "#b32f40", "G": "#46b650",
                                  "E": "#7e8184", "W": "White"
                                  }
                colors = sorted(color_distribution.keys(), key=lambda c: color_value[c])
                # CodeReview: Support auto sizing
                if backwards:
                    current_x -= draw_property["size"][0]
                print(self.properties["name"], current_x, draw_property["size"])
                for color in colors:
                    bar_width = color_distribution[color] * draw_property["size"][0] // total_color
                    if len(color) == 1:
                        draw.rectangle(((current_x, current_y),
                                        (current_x + bar_width, current_y + draw_property["size"][1])),
                                       fill=color_to_color[color])
                        print(current_x, bar_width, color, draw_property["size"][1])
                    elif len(color) == 2:
                        color1, color2 = color
                        draw.rectangle(((current_x, current_y),
                                        (current_x + bar_width, current_y + draw_property["size"][1] // 2)),
                                       fill=color_to_color[color1])
                        draw.rectangle(((current_x, current_y + draw_property["size"][1] // 2),
                                        (current_x + bar_width, current_y + draw_property["size"][1])),
                                       fill=color_to_color[color2])
                        print(current_x, bar_width, color1, color2, draw_property["size"][1])
                    current_x += bar_width
            if backwards:
                current_x -= draw_property["size"][0]
        return current_x, current_y

    def render_image(self, result: Image, _: ImageDraw, draw_property: Mapping,
                     bounding_box: Tuple[Tuple[int, int], Tuple[int, int]], current_x: int, current_y: int,
                     backwards: bool) -> Tuple[int, int]:
        current_x, current_y = self.resolve_position(draw_property["position"], bounding_box, current_x, current_y)
        image_name = self.properties.get(draw_property["property"])
        if image_name is not None:
            path = f"resources/images/{image_name}.png"
            if os.path.exists(path):
                image = Image.open(path)
                result.paste(image, (current_x - draw_property["size"][0] if backwards else 0, current_y))
                current_x += image.size[0]
            else:
                raise Exception(f"Could not find image for {image_name} searched {path}")
        elif draw_property["required"]:
            raise Exception(f"Missing required property: {draw_property['property']} from card {self.properties}")
        if backwards:
            current_x -= draw_property["size"][0]
        else:
            current_x += draw_property["size"][0]
        return current_x, current_y

    def render_property(self, result: Image, draw: ImageDraw, draw_property: Mapping,
                        bounding_box: Tuple[Tuple[int, int], Tuple[int, int]], current_x: int, current_y: int,
                        backwards: bool) -> Tuple[int, int]:
        if draw_property["type"] == "container":
            return self.render_container(result, draw, draw_property, bounding_box, current_x, current_y, backwards)
        elif draw_property["type"] == "text":
            return self.render_text(result, draw, draw_property, bounding_box, current_x, current_y, backwards)
        elif draw_property["type"].startswith("list["):
            return self.render_list(result, draw, draw_property, bounding_box, current_x, current_y, backwards)
        elif draw_property["type"] == "colorbar":
            return self.render_colorbar(result, draw, draw_property, bounding_box, current_x, current_y, backwards)
        elif draw_property["type"] == "image":
            return self.render_image(result, draw, draw_property, bounding_box, current_x, current_y, backwards)
        else:
            raise Exception(f"Unsupported type {draw_property['type']} in property {draw_property}")

    def render(self) -> Image:
        result = Image.new("RGBA", (self.format["width"], self.format["height"]), "White")
        draw = ImageDraw.Draw(result)
        for draw_property in self.format["properties"]:
            self.render_property(result, draw, draw_property, ((0, 0), (self.format["width"], self.format["height"])),
                                 0, 0, False)
        return result


def main(input_file: str):
    dividers, global_properties = Divider.load(input_file)
    pages = Divider.render_pages(dividers, global_properties)
    pdf = FPDF('P', "in", "Letter")
    flipped_pdf = FPDF('P', "in", "Letter")
    if not os.path.exists("output"):
        os.makedirs("output")
    for i, page in enumerate(pages):
        print(f"Generating page {i}")
        page.save(f"output/page{i}.png")
        if global_properties["double_sided"] and global_properties["separate_docs"] and i % 2 == 1:
            flipped_pdf.add_page()
            flipped_pdf.image(f"output/page{i}.png", 0, 0, 8.5, 11)
        else:
            pdf.add_page()
            pdf.image(f"output/page{i}.png", 0, 0, 8.5, 11)
    pdf.output("output/dividers.pdf")
    if global_properties["separate_docs"] and global_properties["double_sided"]:
        flipped_pdf.output("output/dividers_flipped.pdf")


if __name__ == "__main__":
    main("cards2.yaml")
