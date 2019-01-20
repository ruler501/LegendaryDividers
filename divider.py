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
                for property_name, source in populate_from_rarities["properties"].items():
                    if source not in card:
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
        separate_docs = global_properties["separate_docs"]
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

    def resolve_position(self, position: Tuple[Union[int, str], Union[int, str]],
                         bounding_box: Tuple[Tuple[int, int], Tuple[int, int]], current_x: int, current_y: int) -> \
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
                         bounding_box: Tuple[Tuple[int, int], Tuple[int, int]], current_x: int, current_y: int) ->\
            Tuple[int, int]:
        new_bounding_box = (self.resolve_position(draw_property["position"], bounding_box, current_x, current_y),
                            draw_property["size"])
        for recursive_draw_property in draw_property["properties"]:
            prev_current_x = current_x
            prev_current_y = current_y
            current_x, current_y = self.render_property(result, draw, recursive_draw_property, new_bounding_box, current_x, current_y)
            if prev_current_x != current_x:
                current_x += draw_property["spacing"]
            if prev_current_y != current_y:
                current_y += draw_property["spacing"]
        return current_x, current_y

    def render_text(self, result: Image, draw: ImageDraw, draw_property: Mapping,
                         bounding_box: Tuple[Tuple[int, int], Tuple[int, int]], current_x: int, current_y: int) ->\
            Tuple[int, int]:
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
            draw.rectangle(((current_x, current_y), (current_x + desired_width, current_y + desired_height)),
                           fill=background)
            # CodeReview: center between current_y and bottom of bounding box
            x_coord = (current_x + (desired_width - text_width) // 2) if draw_property["centered_width"] else current_x
            y_coord = (current_y + (desired_height - text_height) // 2) if draw_property["centered_height"] else current_y
            draw.text((x_coord, y_coord), text, fill=text_color, font=font)
            current_x += desired_width
        elif draw_property["required"]:
            raise Exception(f"Missing required property: {draw_property['property']} from card {self.properties}")
        return current_x, current_y

    def render_list(self, result: Image, draw: ImageDraw, draw_property: Mapping,
                         bounding_box: Tuple[Tuple[int, int], Tuple[int, int]], current_x: int, current_y: int) ->\
            Tuple[int, int]:
        ...

    def render_colorbar(self, result: Image, draw: ImageDraw, draw_property: Mapping,
                         bounding_box: Tuple[Tuple[int, int], Tuple[int, int]], current_x: int, current_y: int) ->\
            Tuple[int, int]:
        ...

    def render_image(self, result: Image, draw: ImageDraw, draw_property: Mapping,
                         bounding_box: Tuple[Tuple[int, int], Tuple[int, int]], current_x: int, current_y: int) ->\
            Tuple[int, int]:
        ...

    def render_property(self, result: Image, draw: ImageDraw, draw_property: Mapping,
                        bounding_box: Tuple[Tuple[int, int], Tuple[int, int]], current_x: int, current_y: int) -> \
            Tuple[int, int]:
        if draw_property["type"] == "container":
            return self.render_container(result, draw, draw_property, bounding_box, current_x, current_y)
        elif draw_property["type"] == "text":
            return self.render_text(result, draw, draw_property, bounding_box, current_x, current_y)
        elif draw_property["type"].startswith("list["):
            return self.render_list(result, draw, draw_property, bounding_box, current_x, current_y)
        elif draw_property["type"] == "colorbar":
            return self.render_colorbar(result, draw, draw_property, bounding_box, current_x, current_y)
        elif draw_property["type"] == "image":
            return self.render_image(result, draw, draw_property, bounding_box, current_x, current_y)

    def render(self) -> Image:
        result = Image.new("RGBA", (self.format["width"], self.format["height"]), "White")
        draw = ImageDraw.Draw(result)
        for draw_property in self.format["properties"]:
            self.render_property(result, draw, draw_property, ((0, 0), (self.format["width"], self.format["height"])),
                                 0, 0)
        if self.image is not None:
            result.paste(self.image, (0, LABEL_HEIGHT))
        team_x = divider_width - COLOR_BAR_WIDTH - ICON_SPACING - ICON_WIDTH
        if self.teams is None or len(self.teams) == 0:
            team_x += ICON_WIDTH + ICON_SPACING
        total_color = sum(amount for amount in self.color_distribution.values())
        if total_color == 0:
            team_x += COLOR_BAR_WIDTH
        theme_font = ImageFont.truetype("resources/KOMIKAX_.ttf", THEME_FONT_SIZE)
        if self.themes is not None:
            current_y = 0
            cached_current_x = current_x
            # CodeReview: Break into 2 rows
            # CodeReview: Specify an order that all will conform to
            for theme in self.themes:
                resource_name = f"resources/icons/{theme}.png"
                if os.path.isfile(resource_name):
                    icon = Image.open(resource_name)
                    icon_width, icon_height = icon.size
                    icon = icon.resize((ICON_HEIGHT * icon_width // icon_height, ICON_HEIGHT), Image.HAMMING)
                    icon_width, icon_height = icon.size
                    if current_x + ICON_SPACING + icon_width > team_x and current_y == 0:
                        current_y += LABEL_HEIGHT // 2
                        current_x = cached_current_x
                    result.paste(icon, (current_x + ICON_SPACING, current_y + (LABEL_HEIGHT // 2 - icon_height) // 2))
                    current_x += ICON_SPACING + icon_width
                else:
                    text_width, text_height = draw.textsize(theme, theme_font)
                    if current_x + ICON_SPACING + text_width > team_x and current_y == 0:
                        current_y += LABEL_HEIGHT // 2
                        current_x = cached_current_x
                    draw.text((current_x + ICON_SPACING, current_y + (LABEL_HEIGHT // 2 - text_height) // 2), theme,
                              fill="Black", font=theme_font)
                    current_x += ICON_SPACING + text_width
        current_x = team_x
        if self.teams is not None and len(self.teams) > 0:
            if len(self.teams) == 1:
                team = self.teams[0]
                icon = Image.open(f"resources/icons/{team}.png")
                icon = icon.resize((ICON_WIDTH, ICON_HEIGHT), Image.HAMMING)
                result.paste(icon, (current_x, (LABEL_HEIGHT - ICON_HEIGHT) // 2))
            if len(self.teams) == 2:
                team = self.teams[0]
                icon = Image.open(f"resources/icons/{team}.png")
                icon = icon.resize((ICON_WIDTH, ICON_HEIGHT), Image.HAMMING)
                result.paste(icon, (current_x, (LABEL_HEIGHT // 2 - ICON_HEIGHT) // 2))
                team = self.teams[1]
                icon = Image.open(f"resources/icons/{team}.png")
                icon = icon.resize((ICON_WIDTH, ICON_HEIGHT), Image.HAMMING)
                result.paste(icon, (current_x, LABEL_HEIGHT // 2 + (LABEL_HEIGHT // 2 - ICON_HEIGHT) // 2))
        current_x = divider_width - COLOR_BAR_WIDTH
        if total_color > 0:
            color_value = {"Y": 0, "U": 1, "B": 2, "R": 3, "G": 4, "YU": 5, "UB": 6, "BR": 7, "RG": 8, "GY": 9,
                           "YB": 10, "UR":11, "BG": 12, "RY": 13, "GU": 14, "E": 15, "W": -1}
            color_to_theme = {"Y": "instinct", "U": "ranged", "B": "tech", "R": "covert", "G": "strength",
                              "E": "shield", "W": "blank"}
            color_to_color = {"Y": "#dea319", "U": "#01a1d5", "B": "#a6a8ab", "R": "#b32f40", "G": "#46b650",
                              "E": "#7e8184", "W": "White"}
            colors = sorted(self.color_distribution.keys(), key=lambda c: color_value[c])
            for color in colors:
                bar_width = self.color_distribution[color] * COLOR_BAR_WIDTH // total_color
                if len(color) == 1:
                    draw.rectangle(((current_x, 0), (current_x + bar_width, LABEL_HEIGHT)), fill=color_to_color[color])
                    """
                    theme = color_to_theme[color]
                    icon = Image.open(f"resources/icons/{theme}.png")
                    icon = icon.resize((3 * ICON_WIDTH // 4, 3 * ICON_HEIGHT // 4), Image.HAMMING)
                    result.paste(icon, (current_x + (bar_width - 3 * ICON_WIDTH // 4) // 2,
                                        (LABEL_HEIGHT - 3 * ICON_HEIGHT // 4) // 2))
                    """
                elif len(color) == 2:
                    color1, color2 = color
                    draw.rectangle(((current_x, 0), (current_x + bar_width, LABEL_HEIGHT // 2)),
                                   fill=color_to_color[color1])
                    draw.rectangle(((current_x, LABEL_HEIGHT/2), (current_x + bar_width, LABEL_HEIGHT)),
                                   fill=color_to_color[color2])
                    """
                    theme = color_to_theme[color1]
                    icon = Image.open(f"resources/icons/{theme}.png")
                    icon = icon.resize((3 * ICON_WIDTH // 4, 3 * ICON_HEIGHT // 4), Image.HAMMING)
                    result.paste(icon, (current_x + (bar_width - 3 * ICON_WIDTH // 4) // 2,
                                        (LABEL_HEIGHT // 2 - 3 * ICON_HEIGHT // 4) // 2))
                    theme = color_to_theme[color2]
                    icon = Image.open(f"resources/icons/{theme}.png")
                    icon = icon.resize((3 * ICON_WIDTH // 4, ICON_HEIGHT // 2), Image.HAMMING)
                    result.paste(icon, (current_x + (bar_width - 3 * ICON_WIDTH // 4) // 2, LABEL_HEIGHT // 2 +
                                        (LABEL_HEIGHT // 2 - 3 * ICON_HEIGHT // 4) // 2))
                    """
                current_x += bar_width
        theme_font = ImageFont.truetype("resources/KOMIKAX_.ttf", NOTE_FONT_SIZE)
        if self.notes is not None and len(self.notes) > 0:
            current_y = LABEL_HEIGHT + 8
            for note in self.notes:
                resource_name = f"resources/icons/{note}.png"
                if os.path.isfile(resource_name):
                    icon = Image.open(resource_name)
                    icon_width, icon_height = icon.size
                    icon = icon.resize((ICON_HEIGHT * icon_width // icon_height, ICON_HEIGHT), Image.HAMMING)
                    icon_width, icon_height = icon.size
                    result.paste(icon, (32, current_y + (LABEL_HEIGHT // 2 - icon_height) // 2))
                    line_height = icon_height
                else:
                    note = textwrap.fill(note, 70)
                    _, text_height = draw.multiline_textsize(note, theme_font)
                    draw.multiline_text((32, current_y), note, "Black", theme_font)
                    line_height = text_height
                draw.ellipse((8, current_y + (line_height - 16) // 2, 24, current_y + (line_height + 16) // 2),
                             fill="Black")
                current_y += text_height + 8
        return result

if __name__ == "__main__":
    dividers, grid, double_sided, separate_docs = Divider.load("cards.yaml")
    pages = Divider.render_pages(dividers, 2, 3, 1700, 2200, grid, double_sided)
    pdf = FPDF('P', "in", "Letter")
    flipped_pdf = FPDF('P', "in", "Letter")
    if not os.path.exists("output"):
        os.makedirs("output")
    for i, page in enumerate(pages):
        print(f"Generating page {i}")
        page.save(f"output/page{i}.png")
        if separate_docs and i % 2 == 1:
            flipped_pdf.add_page()
            flipped_pdf.image(f"output/page{i}.png", 0, 0, 8.5, 11)
        else:
            pdf.add_page()
            pdf.image(f"output/page{i}.png", 0, 0, 8.5, 11)
    pdf.output("output/dividers.pdf")
    if separate_docs:
        flipped_pdf.output("output/dividers_flipped.pdf")