import math
import os
import textwrap

import yaml

from collections import Counter
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont
from typing import List, Tuple


DIVIDER_WIDTH = 728
DIVIDER_HEIGHT = 592
DIVIDER_OFFSET_HEIGHT = 100
DIVIDER_OFFSET_WIDTH = 90
DIVIDER_MARGIN_WIDTH = 80
DIVIDER_MARGIN_HEIGHT = 101
LABEL_HEIGHT = 72
TYPE_BOX_WIDTH = 185
NAME_MARGIN_WIDTH = 16
ICON_SPACING = 8
ICON_WIDTH = 37 * (LABEL_HEIGHT - 8) // 82
ICON_HEIGHT = (LABEL_HEIGHT - 8) // 2
COLOR_BAR_WIDTH = DIVIDER_WIDTH // 3
IMAGE_HEIGHT = 520
NAME_TYPE_FONT_SIZE = 24
THEME_FONT_SIZE = 12
GRID_WIDTH = 1
GRID_SPACING = 18
NOTE_FONT_SIZE = 16


class Divider:
    def __init__(self, name: str, color_distribution: Counter, image: Image, card_type: str = None,
                 type_background: str = "#766f92", type_color: str = "White", teams: List[str] = None,
                 themes: List[str] = None, notes: List[str] = None):
        self.name = name
        self.color_distribution = color_distribution
        self.image = image
        self.card_type = card_type
        self.type_background = type_background
        self.type_color = type_color
        self.teams = teams
        self.themes = themes
        self.notes = notes

    @staticmethod
    def load(filename: str) -> Tuple[List["Divider"], bool, bool, bool]:
        with open(filename) as source_file:
            data = yaml.load(source_file)
        grid = data["grid"]
        double_sided = data["double_sided"]
        separate_docs = data["separate_docs"]
        results: List[Divider] = []
        for card in data["cards"]:
            name = card["name"]
            color_distribution = Counter()
            if "color" in card:
                color_distribution = Counter([card["color"]])
            elif "colors" in card:
                color_distribution = Counter(card["colors"])
            elif "common1" in card and "common2" in card and "uncommon" in card and "rare" in card:
                color = card["common1"]["color"]
                cost = card["common1"]["cost"]
                recruit = None
                if "recruit" in card["common1"]:
                    recruit = card["common1"]["recruit"]
                combat = None
                if "combat" in card["common1"]:
                    combat = card["common1"]["combat"]
                piercing = None
                if "piercing" in card["common1"]:
                    piercing = card["common1"]["piercing"]
                color_distribution[color] += 5
                color = card["common2"]["color"]
                cost = card["common2"]["cost"]
                recruit = None
                if "recruit" in card["common2"]:
                    recruit = card["common2"]["recruit"]
                combat = None
                if "combat" in card["common2"]:
                    combat = card["common2"]["combat"]
                piercing = None
                if "piercing" in card["common2"]:
                    piercing = card["common2"]["piercing"]
                color_distribution[color] += 5
                color = card["uncommon"]["color"]
                cost = card["uncommon"]["cost"]
                recruit = None
                if "recruit" in card["uncommon"]:
                    recruit = card["uncommon"]["recruit"]
                combat = None
                if "combat" in card["uncommon"]:
                    combat = card["uncommon"]["combat"]
                piercing = None
                if "piercing" in card["uncommon"]:
                    piercing = card["uncommon"]["piercing"]
                color_distribution[color] += 3
                color = card["rare"]["color"]
                cost = card["rare"]["cost"]
                recruit = None
                if "recruit" in card["rare"]:
                    recruit = card["rare"]["recruit"]
                combat = None
                if "combat" in card["rare"]:
                    combat = card["rare"]["combat"]
                piercing = None
                if "piercing" in card["rare"]:
                    piercing = card["rare"]["piercing"]
                color_distribution[color] += 1
            image = None
            if "image" in card:
                image = Image.open(f"resources/images/{card['image']}.png")
            card_type = None
            if "card_type" in card:
                card_type = card["card_type"]
            type_background = None
            if "type_background" in card:
                type_background = card["type_background"]
            type_color = None
            if "type_background" in card:
                type_color = card["type_color"]
            teams = None
            if "teams" in card:
                teams = card["teams"]
            themes = None
            if "themes" in card:
                themes = card["themes"]
            notes = None
            if "notes" in card:
                notes = card["notes"]
            results.append(Divider(name, color_distribution, image, card_type, type_background, type_color, teams,
                                   themes, notes))
        return results, grid, double_sided, separate_docs

    @staticmethod
    def render_pages(dividers: List["Divider"], width: int, height: int, page_width: int, page_height: int,
                     grid_lines: bool = True, double_sided: bool = False):
        pages: List[Image] = []
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
                    x = DIVIDER_OFFSET_WIDTH + x_index * (DIVIDER_WIDTH + DIVIDER_MARGIN_WIDTH)
                    y = DIVIDER_OFFSET_HEIGHT + y_index * (DIVIDER_HEIGHT + DIVIDER_MARGIN_HEIGHT)
                    div_image = divider.render()
                    page.paste(div_image, (x, y))
                    if grid_lines:
                        draw.line(((x - DIVIDER_MARGIN_WIDTH + GRID_SPACING, y-1), (x - GRID_SPACING, y-1)),
                                  fill="Black", width=GRID_WIDTH)
                        draw.line(((x-1, y - DIVIDER_MARGIN_HEIGHT + GRID_SPACING), (x-1, y - GRID_SPACING)),
                                  fill="Black", width=GRID_WIDTH)
                        draw.line(((x - DIVIDER_MARGIN_WIDTH + GRID_SPACING, y + DIVIDER_HEIGHT),
                                   (x - GRID_SPACING, y + DIVIDER_HEIGHT)), fill="Black", width=GRID_WIDTH)
                        draw.line(((x - 1, y + DIVIDER_HEIGHT + GRID_SPACING),
                                   (x - 1, y + DIVIDER_HEIGHT + DIVIDER_MARGIN_HEIGHT - GRID_SPACING)),
                                  fill="Black", width=GRID_WIDTH)
                        draw.line(((x + DIVIDER_WIDTH + GRID_SPACING, y - 1),
                                   (x + DIVIDER_WIDTH + DIVIDER_MARGIN_WIDTH - GRID_SPACING, y - 1)),
                                  fill="Black", width=GRID_WIDTH)
                        draw.line(((x + DIVIDER_WIDTH, y - DIVIDER_MARGIN_HEIGHT + GRID_SPACING),
                                   (x + DIVIDER_WIDTH, y - GRID_SPACING)), fill="Black", width=GRID_WIDTH)
                        draw.line(((x + DIVIDER_WIDTH, y + DIVIDER_HEIGHT + GRID_SPACING),
                                   (x + DIVIDER_WIDTH, y + DIVIDER_HEIGHT + DIVIDER_MARGIN_HEIGHT - GRID_SPACING)),
                                  fill="Black", width=GRID_WIDTH)
                        draw.line(((x + DIVIDER_WIDTH + GRID_SPACING, y + DIVIDER_HEIGHT),
                                   (x + DIVIDER_WIDTH + DIVIDER_MARGIN_WIDTH - GRID_SPACING, y + DIVIDER_HEIGHT)),
                                  fill="Black", width=GRID_WIDTH)
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
                        x = DIVIDER_OFFSET_WIDTH + (width - x_index - 1) * (DIVIDER_WIDTH + DIVIDER_MARGIN_WIDTH)
                        y = DIVIDER_OFFSET_HEIGHT + y_index * (DIVIDER_HEIGHT + DIVIDER_MARGIN_HEIGHT)
                        div_image = divider.render()
                        page.paste(div_image, (x, y))
                        if grid_lines:
                            draw.line(((x - DIVIDER_MARGIN_WIDTH + GRID_SPACING, y-1), (x - GRID_SPACING, y-1)),
                                      fill="Black", width=GRID_WIDTH)
                            draw.line(((x-1, y - DIVIDER_MARGIN_HEIGHT + GRID_SPACING), (x-1, y - GRID_SPACING)),
                                      fill="Black", width=GRID_WIDTH)
                            draw.line(((x - DIVIDER_MARGIN_WIDTH + GRID_SPACING, y + DIVIDER_HEIGHT),
                                       (x - GRID_SPACING, y + DIVIDER_HEIGHT)), fill="Black", width=GRID_WIDTH)
                            draw.line(((x - 1, y + DIVIDER_HEIGHT + GRID_SPACING),
                                       (x - 1, y + DIVIDER_HEIGHT + DIVIDER_MARGIN_HEIGHT - GRID_SPACING)),
                                      fill="Black", width=GRID_WIDTH)
                            draw.line(((x + DIVIDER_WIDTH + GRID_SPACING, y - 1),
                                       (x + DIVIDER_WIDTH + DIVIDER_MARGIN_WIDTH - GRID_SPACING, y - 1)),
                                      fill="Black", width=GRID_WIDTH)
                            draw.line(((x + DIVIDER_WIDTH, y - DIVIDER_MARGIN_HEIGHT + GRID_SPACING),
                                       (x + DIVIDER_WIDTH, y - GRID_SPACING)), fill="Black", width=GRID_WIDTH)
                            draw.line(((x + DIVIDER_WIDTH, y + DIVIDER_HEIGHT + GRID_SPACING),
                                       (x + DIVIDER_WIDTH, y + DIVIDER_HEIGHT + DIVIDER_MARGIN_HEIGHT - GRID_SPACING)),
                                      fill="Black", width=GRID_WIDTH)
                            draw.line(((x + DIVIDER_WIDTH + GRID_SPACING, y + DIVIDER_HEIGHT),
                                       (x + DIVIDER_WIDTH + DIVIDER_MARGIN_WIDTH - GRID_SPACING, y + DIVIDER_HEIGHT)),
                                      fill="Black", width=GRID_WIDTH)
                    if should_break:
                        break
                pages.append(page)
        return pages


    def render(self) -> Image:
        result = Image.new("RGBA", (DIVIDER_WIDTH, DIVIDER_HEIGHT), "White")
        draw = ImageDraw.Draw(result)
        if self.image is not None:
            result.paste(self.image, (0, LABEL_HEIGHT))
        current_x: int = 0
        font = ImageFont.truetype("resources/KOMIKAX_.ttf", NAME_TYPE_FONT_SIZE)
        if self.card_type is not None:
            draw.rectangle(((current_x, 0), (current_x + TYPE_BOX_WIDTH, LABEL_HEIGHT)), fill=self.type_background)
            text_width, text_height = draw.textsize(self.card_type, font)
            draw.text((current_x + (TYPE_BOX_WIDTH - text_width)//2, (LABEL_HEIGHT - text_height)//2), self.card_type,
                      fill=self.type_color, font=font)
            current_x += TYPE_BOX_WIDTH
        text_width, text_height = draw.textsize(self.name, font)
        draw.text((current_x + NAME_MARGIN_WIDTH, (LABEL_HEIGHT - text_height)//2), self.name, fill="Black", font=font)
        current_x += text_width + NAME_MARGIN_WIDTH
        team_x = DIVIDER_WIDTH - COLOR_BAR_WIDTH - ICON_SPACING - ICON_WIDTH
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
        current_x = DIVIDER_WIDTH - COLOR_BAR_WIDTH
        if total_color > 0:
            color_value = {"Y": 0, "U": 1, "B": 2, "R": 3, "G": 4, "YU": 5, "UB": 6, "BR": 7, "RG": 8, "GY": 9,
                           "YB": 10, "UR":11, "BG": 12, "RY": 13, "GU": 14, "E": 15}
            color_to_theme = {"Y": "instinct", "U": "ranged", "B": "tech", "R": "covert", "G": "strength",
                              "E": "shield"}
            color_to_color = {"Y": "#dea319", "U": "#01a1d5", "B": "#a6a8ab", "R": "#b32f40", "G": "#46b650",
                              "E": "#7e8184"}
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
                    note = textwrap.fill(note, 80)
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
    if not os.path.exists("temp"):
        os.makedirs("temp")
    for i, page in enumerate(pages):
        page.save(f"temp/page{i}.png")
        if separate_docs and i % 2 == 1:
            flipped_pdf.add_page()
            flipped_pdf.image(f"temp/page{i}.png", 0, 0, 8.5, 11)
        else:
            pdf.add_page()
            pdf.image(f"temp/page{i}.png", 0, 0, 8.5, 11)
    if not os.path.exists("output"):
        os.makedirs("output")
    pdf.output("output/dividers.pdf")
    if separate_docs:
        flipped_pdf.output("output/dividers_flipped.pdf")