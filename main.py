"""Render the A2 world brief as a standalone 1024-pixel submission."""

import os
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


SIZE = 1024
SCALE = 2
FONT_DIR = Path("/usr/share/fonts/truetype/noto")
DISPLAY = "NotoSerifDisplay-Black"
SERIF = "NotoSerifDisplay-Bold"
BLACK = "NotoSans-Black"
BOLD = "NotoSans-Bold"
SEMIBOLD = "NotoSans-SemiBold"
REGULAR = "NotoSans-Regular"

PAPER = "#f9f5ec"
CARD = "#fffdf8"
INK = "#202c2c"
MUTED = "#455650"
BORDER = "#cec4b1"
RULE = "#d9d2c4"
RED = "#aa3023"
BLUE = "#205971"
BERRY = "#833b55"
OCHRE = "#805021"
PURPLE = "#624e84"
TEAL = "#236763"

# Category colors pair the small text with two tints for the card header.
CONFLICT = (BERRY, "#e9dbdb", "#d4b9be")
SECURITY = (BLUE, "#d7e0e0", "#b2c6ca")
POLITICS = (OCHRE, "#e9dfd2", "#d8c6b1")
TECH = (PURPLE, "#e2dde6", "#c8bed0")
DEALS = (RED, "#efdad5", "#dcb0a8")
SCIENCE = (TEAL, "#d7e0db", "#b3c8c1")

# Each card has its own line breaks to preserve the reference's editorial layout.
LEADS = (
    ("TARIFFS  /  NORTH AMERICA", "14:30", RED,
     ("Trump hits 14 partners", "with fresh tariffs"),
     "China +20% · India up to 25% · EU, Japan in net"),
    ("ENERGY  /  MIDDLE EAST", "17:30", "#115c58",
     ("Tankers ablaze after", "Hormuz mine blasts"),
     "Three vessels hit; Iran warns ships off lanes"),
    ("CONFLICT  /  EUROPE", "18:09", BERRY,
     ("Ukraine hits Russian air", "base, five jets out"),
     "MiG-31s and Su-34s damaged at Savasleyka"),
)

MINIS = (
    ("CONFLICT", "04:45", CONFLICT, "burst",
     ("Putin vows payback for", "refinery raids"), "Retaliation 'inevitable'"),
    ("CONFLICT", "23:40", CONFLICT, "tower",
     ("Houthis hit Riyadh and", "Jazan ports"), "Saudi intercepts missiles"),
    ("CONFLICT", "02:15", CONFLICT, "burst",
     ("Gaza strikes kill 11,", "incl. two girls"), "Hamas security chief dead"),
    ("SECURITY", "08:00", SECURITY, "shield",
     ("NATO boosts air watch", "on east flank"), "After missile crashes"),
    ("SECURITY", "10:56", SECURITY, "shield",
     ("US weighs killing Iran's", "leaders"), "NBC: White House debate"),
    ("SECURITY", "07:00", SECURITY, "shield",
     ("Seoul warns after Russian", "jets approach"), "Border isles on alert"),
    ("POLITICS", "09:00", POLITICS, "capitol",
     ("North Korea expels Swiss", "diplomat"), "Pyongyang office to shut"),
    ("DEALS", "10:30", DEALS, "deal",
     ("Bangladesh garment pay", "up 36%"), "Minimum wage win"),
    ("DEALS", "08:00", DEALS, "deal",
     ("Flipkart chief to step", "down in Dec"), "Krishnamurthy exits"),
    ("TECH", "06:00", TECH, "chip",
     ("Nvidia's Huang back", "as CEO"), "Reinstated after 11 days"),
    ("MARKETS", "15:00", TECH, "chip",
     ("Chip stocks down 50%", "since June"), "SOX -21% in November"),
    ("SPORT", "19:26", SCIENCE, "medal",
     ("South Africa sweep", "Bangladesh 2-0"), "Mulder takes 7-31"),
    ("SPORT", "21:00", SCIENCE, "medal",
     ("Real Madrid rout PSV", "5-1 in UCL"), "City 2-2 Napoli"),
    ("DISASTERS", "05:00", SECURITY, "flame",
     ("Cairo tanker fire kills", "31"), "Fuel truck crash"),
    ("DISASTERS", "04:00", SECURITY, "flame",
     ("Six die in US plane", "crash off coast"), "Coast Guard recovers"),
)

BRIEF_COLUMNS = (
    (
        (OCHRE, "WHO chief urges end to US fuel blockade on Cuba"),
        (OCHRE, "India marks Constitution Day; Nepal aid package"),
        (PURPLE, "Gukesh faces Sindarov for chess crown"),
        (BLUE, "Thanksgiving travel chaos; long airport lines"),
        (RED, "Vance's Thanksgiving F-bomb at Ohio base"),
        (RED, "Turkey pardon: bird named Feathers bolts"),
        (OCHRE, "Israeli judges urge dropping top Netanyahu charges"),
        (BLUE, "Record 2,000 migrants reach Canary Islands in a day"),
        (PURPLE, "Kuala Lumpur sues Google for $146m"),
    ),
    (
        (OCHRE, "Australia, Solomon Islands sign pact to thwart China"),
        (BLUE, "China, Cambodia stage joint military drills"),
        (BERRY, "UN: five women killed every hour by partner or kin"),
        (TEAL, "UN chief urges talks on global AI safety framework"),
        (BLUE, "ECOWAS approves regional force roadmap to 2027"),
        (OCHRE, "India urges human control over military AI"),
        (RED, "IPL 2027 auction draws 1,220 players"),
        (TEAL, "Melania helps reunite nine Ukrainian, Russian kids"),
    ),
)

TIMELINE = (
    ("00:50", OCHRE, "Australia–Solomon pact"),
    ("02:15", BERRY, "Gaza strikes"),
    ("04:45", BERRY, "Putin vows retaliation"),
    ("05:00", BLUE, "Cairo tanker fire"),
    ("06:00", PURPLE, "Huang back at Nvidia"),
    ("07:00", BLUE, "Seoul jet warning"),
    ("08:00", BLUE, "NATO air watch"),
    ("09:00", OCHRE, "N. Korea expels Swiss"),
    ("10:30", RED, "Bangladesh wage hike"),
    ("12:00", BERRY, "UN: women killed hourly"),
    ("14:30", RED, "Trump tariff sweep"),
    ("15:00", RED, "Chip stocks slide"),
    ("17:30", RED, "Hormuz tanker blasts"),
    ("18:09", BERRY, "Savasleyka air strike"),
    ("19:26", TEAL, "S. Africa sweep Bangladesh"),
    ("21:00", TEAL, "Real Madrid 5-1 PSV"),
)

MARKETS = (
    ("Nasdaq", "-2.0%", RED),
    ("KOSPI", "-6.2%", RED),
    ("Nikkei", "-3.0%", RED),
    ("SOX Nov", "-21%", RED),
    ("US 10-yr", "4.84%", INK),
    ("VIX Nov", "+60%", RED),
    ("Dollar", "103.6", INK),
)

# Pairs of start and exclusive end columns encode runs of land dots.
LAND_ROWS = (
    (20, 40),
    (16, 19, 22, 27, 29, 40),
    (12, 19, 22, 25, 30, 40, 65, 74),
    (3, 28, 29, 38, 49, 52, 57, 85),
    (0, 1, 3, 34, 39, 42, 48, 90),
    (4, 21, 25, 29, 31, 34, 47, 51, 52, 86),
    (3, 7, 11, 21, 25, 28, 43, 44, 47, 80, 84, 85),
    (12, 23, 24, 28, 42, 44, 49, 52, 53, 57, 58, 79, 83, 85),
    (14, 30, 48, 52, 55, 80),
    (14, 30, 44, 47, 48, 52, 55, 56, 58, 79),
    (14, 25, 42, 43, 48, 49, 50, 51, 52, 57, 58, 73, 76, 77, 80, 81),
    (15, 25, 42, 44, 53, 57, 58, 73, 74, 75),
    (15, 25, 43, 48, 56, 57, 58, 75, 78, 79),
    (15, 16, 17, 21, 23, 25, 42, 53, 54, 56, 57, 58, 59, 75),
    (17, 21, 24, 25, 41, 53, 54, 56, 60, 72),
    (18, 21, 24, 26, 41, 59, 62, 70),
    (20, 23, 41, 54, 55, 59, 63, 65, 71, 72),
    (22, 24, 41, 57, 63, 65, 69, 70, 71, 72),
    (23, 25, 27, 30, 42, 57, 64, 65, 69, 70, 75, 76),
    (24, 32, 43, 57, 69, 70, 73, 74),
    (24, 32, 47, 56, 69, 70, 72, 74),
    (25, 34, 47, 55, 70, 71, 72, 74, 78, 80),
    (25, 36, 47, 55, 71, 73, 79, 82),
    (25, 36, 48, 50, 51, 55),
    (26, 35, 48, 55, 56, 57, 75, 79, 80, 81),
    (27, 35, 48, 54, 56, 57, 73, 81),
    (27, 34, 48, 53, 56, 57, 73, 82),
    (27, 33, 49, 53, 73, 83),
    (27, 32, 49, 52, 73, 83),
    (26, 31, 79, 81),
    (26, 30, 80, 81),
    (26, 30, 81, 82, 87, 88),
    (26, 29, 86, 87),
    (26, 28),
)

REGIONS = (
    ("North America", "#235483", ((116, 665), (150, 664), (166, 660))),
    ("Latin America", "#947319", ((161, 691),)),
    ("Europe", "#734581", ((231, 663), (241, 653), (248, 660), (282, 650))),
    ("Middle East", "#b53026",
     ((268, 671), (274, 668), (279, 677), (284, 668), (289, 676))),
    ("Africa", "#406e37", ((257, 712), (242, 671), (221, 687))),
    ("East Asia", "#a4421d",
     ((343, 679), (347, 663), (353, 664), (357, 669), (369, 667))),
    ("Southeast Asia", "#12665f", ((327, 685), (336, 682))),
    ("Pacific", "#2f6b98", ((389, 710),)),
    ("Global", "#5a6070", ()),
)


def px(value):
    return round(value * SCALE)


@lru_cache(maxsize=None)
def font(face, size):
    return ImageFont.truetype(str(FONT_DIR / (face + ".ttf")), px(size))


class Canvas:
    """Draw in final-image coordinates, optionally relative to a panel."""

    def __init__(self, draw, x=0, y=0):
        self.draw = draw
        self.x = x
        self.y = y

    def at(self, x, y):
        return Canvas(self.draw, self.x + x, self.y + y)

    def point(self, x, y):
        return px(self.x + x), px(self.y + y)

    def box(self, x, y, w, h):
        left, top = self.point(x, y)
        right, bottom = self.point(x + w, y + h)
        return left, top, right - 1, bottom - 1

    def rect(self, x, y, w, h, fill, outline=None):
        self.draw.rectangle(self.box(x, y, w, h), fill=fill, outline=outline,
                            width=SCALE)

    def dot(self, x, y, radius, fill, outline=None):
        self.ellipse(x - radius, y - radius, 2 * radius, 2 * radius, fill, outline)

    def ellipse(self, x, y, w, h, fill, outline=None):
        self.draw.ellipse(self.box(x, y, w, h), fill=fill, outline=outline, width=SCALE)

    def poly(self, points, color):
        self.draw.polygon([self.point(x, y) for x, y in points], fill=color)

    def line(self, points, color, width=1):
        self.draw.line([self.point(x, y) for x, y in points],
                       fill=color, width=max(1, px(width)), joint="curve")

    def text(self, x, baseline, value, face, size, color=INK, align="l"):
        self.draw.text(self.point(x, baseline), value, fill=color,
                       font=font(face, size), anchor=align + "s")

    def text_size(self, lines, face, size, max_width):
        """Keep matching lines in the same size while fitting their allotted width."""
        while any(font(face, size).getlength(line) > px(max_width) for line in lines):
            size -= 0.5
        return size


def masthead(c):
    c.rect(28, 23.5, 968.5, 2, INK)
    c.text(28, 43.5, "WORLD IN ONE IMAGE", BLACK, 12, "#7c403a")
    c.text(996.5, 42.5, "DAILY WORLD BRIEF", BOLD, 10, MUTED, "r")
    c.text(26.5, 98, "Thursday 26 November 2026", DISPLAY, 60)
    c.text(28.5, 124.5, "35 dated stories · 9 regions · 14 fields",
           SEMIBOLD, 13, MUTED)
    tabs = (("MARKETS", "#a63e34"), ("WORLD", "#235a71"),
            ("CONFLICT", "#853e55"), ("POLITICS", "#835526"),
            ("TECHNOLOGY", "#665085"), ("SCIENCE", "#276964"))
    for index, (label, color) in enumerate(tabs):
        left = 28 + index * 161.4
        c.rect(left, 135, 161.4, 24.5, color)
        c.text(left + 80.7, 149.5, label, BLACK, 9.5, "#ffffff", "m")
        if index:
            c.line(((left, 135), (left, 159)), "#d0b9ae", 0.5)


def market_scene(c):
    c.rect(0, 0, 314, 86, "#f1dbd2")
    c.text(22, 13, "TARIFF SHOCK", BLACK, 7.5, RED)
    for x in (22, 66, 100, 134, 169, 204, 238, 273, 298):
        c.line(((x, 15), (x, 74)), "#dcb5a7", 0.5)
    for y in (17, 31, 45, 59, 73):
        c.line(((19, y), (299, y)), "#dcb5a7", 0.5)
    chart = ((22, 29), (43, 23), (69, 27), (91, 18), (116, 36),
             (138, 33), (160, 40), (178, 33), (204, 54), (222, 48),
             (242, 60), (264, 57), (292, 72))
    for x, top in ((212, 54), (230, 42), (249, 48), (268, 52)):
        c.rect(x, top, 10, 61 - top, "#d3a497")
    for x in (239, 251, 263, 276):
        c.line(((x, 52), (x + 5, 52)), "#f3dcd2", 0.5)
    c.poly((*chart, (292, 74), (22, 74)), "#e9cac0")
    c.line(chart, RED, 2)
    for index in (0, 3, 6, 9, 12):
        x, y = chart[index]
        c.dot(x, y, 3.5, RED)
        c.dot(x, y, 2, "#fff1e8")


def tanker_scene(c):
    c.rect(0, 0, 314, 86, "#d6e9e5")
    c.poly(((0, 0), (145, 0), (132, 7), (114, 9), (107, 15), (79, 21),
            (67, 32), (47, 37), (38, 44), (0, 52)), "#81b1aa")
    c.poly(((314, 31), (314, 86), (261, 86), (248, 78), (255, 69),
            (277, 61), (286, 54), (276, 49), (289, 39)), "#9ac3bc")
    c.text(17, 13.5, "STRAIT OF HORMUZ", BLACK, 7.5, "#185956")
    for x, y, end in ((122, 17, 170), (188, 17, 248), (203, 23, 254),
                      (75, 39, 105), (41, 63, 87), (31, 72, 106),
                      (107, 79, 164), (141, 71, 198), (221, 66, 255)):
        c.line(((x, y), (end, y)), "#65a59e", 0.7)
    c.poly(((59, 50), (249, 50), (232, 65), (92, 65), (73, 58)), "#18514f")
    c.line(((89, 59), (235, 59)), "#59948c", 0.7)
    for x, w in ((91, 16), (108.5, 20), (130, 20), (151.5, 20), (173, 19)):
        c.rect(x, 42, w, 8, "#e3b979")
    c.rect(198, 34.5, 34, 16, "#19625d")
    c.rect(202, 37, 23, 3, "#f0d9a5")
    c.line(((214, 35), (214, 26.5), (223, 26.5)), "#1c645f")
    c.line(((214, 30), (229, 30)), "#1c645f")
    for radius, color in ((7, "#b88d66"), (4.5, "#c29f76")):
        c.dot(258, 37, radius, None, color)
    c.dot(258, 37, 2.25, "#b75d37")


def airbase_scene(c):
    c.rect(0, 0, 314, 86, "#eadbd7")
    c.text(17, 13, "SAVASLEYKA AIR BASE", BLACK, 7.5, BERRY)
    c.poly(((0, 48), (54, 40), (104, 44), (150, 36), (204, 42),
            (257, 35), (314, 40), (314, 86), (0, 86)), "#c3a9a6")
    c.poly(((0, 72), (314, 49), (314, 75), (0, 86)), "#776c70")
    c.line(((14, 79), (300, 60)), "#e9d4bf", 1)
    for x, y in ((31, 74), (91, 70), (151, 66), (211, 62), (271, 58)):
        c.line(((x, y), (x + 17, y - 1)), "#f2dfca", 1.3)
    for x, y in ((86, 47), (207, 39)):
        c.poly(((x - 33, y + 1), (x - 8, y - 2), (x + 1, y - 9),
                (x + 6, y - 9), (x + 5, y - 2), (x + 29, y + 1),
                (x + 31, y + 4), (x + 4, y + 4), (x, y + 9),
                (x - 5, y + 9), (x - 6, y + 4), (x - 32, y + 4)), "#554b56")
    for x, y, radius in ((147, 34, 9), (156, 28, 11), (167, 34, 8),
                         (258, 29, 7), (266, 24, 9), (276, 29, 7)):
        c.dot(x, y, radius, "#a67c78")
    c.poly(((145, 39), (151, 27), (155, 35), (161, 23), (166, 39)), "#c7765b")
    c.poly(((257, 34), (262, 25), (265, 31), (270, 22), (275, 34)), "#c7765b")


def lead_cards(c):
    for x, scene, story in zip((28, 354, 680), (market_scene, tanker_scene, airbase_scene),
                               LEADS):
        lead = c.at(x, 170)
        lead.rect(0, 0, 316.5, 178.5, CARD, BORDER)
        scene(lead.at(1, 1))
        kicker, time, color, headline, summary = story
        lead.text(10, 100.5, kicker, BLACK, 8.5, color)
        lead.text(306, 100.5, time, BOLD, 8.5, MUTED, "r")
        size = lead.text_size(headline, SERIF, 23.5, 296)
        for index, line in enumerate(headline):
            lead.text(10, 128 + index * 24, line, SERIF, size)
        lead.text(10, 169, summary, SEMIBOLD,
                  lead.text_size((summary,), SEMIBOLD, 10, 296), MUTED)


def icon(c, name, color, pale):
    if name == "burst":
        c.poly(((7, 0), (8, 4), (13, 2), (10, 6), (13, 9), (9, 8), (7, 13),
                (5, 9), (0, 11), (3, 7), (0, 5), (5, 5)), color)
    elif name == "tower":
        c.poly(((1, 12), (1, 10), (3, 10), (4, 2), (5, 2), (5, 0),
                (7, 0), (7, 2), (8, 2), (9, 10), (11, 10), (11, 12)), color)
    elif name == "shield":
        c.poly(((1, 2), (6, 0), (12, 2), (11, 7), (9, 10), (6, 12), (3, 10),
                (1, 7)), color)
        c.poly(((2.5, 3), (6, 1.5), (10.5, 3), (10, 6), (6, 10), (3, 7)), pale)
        c.line(((3.5, 5.7), (5.6, 7.2), (9.5, 4)), color, 1.3)
    elif name == "capitol":
        c.poly(((0, 4), (6, 0), (12, 4)), color)
        c.rect(1, 10, 11, 1.5, color)
        for x in (3, 5.5, 8):
            c.rect(x, 5, 1.5, 4, color)
    elif name == "chip":
        c.rect(3, 3, 7, 7, color, color)
        c.rect(5, 5, 3, 3, pale)
        for offset in (4, 6, 8):
            c.line(((1, offset), (3, offset)), color)
            c.line(((10, offset), (12, offset)), color)
            c.line(((offset, 1), (offset, 3)), color)
            c.line(((offset, 10), (offset, 12)), color)
    elif name == "deal":
        c.poly(((0, 4), (4, 1), (6, 2), (4, 5), (6, 7), (9, 5), (11, 7),
                (8, 11), (5, 12), (1, 8)), color)
        c.poly(((5, 4), (8, 1), (11, 1), (13, 4), (11, 6), (8, 4), (6, 6)), color)
    elif name == "medal":
        c.line(((2, 1), (5, 5), (7, 5), (11, 1)), color, 1.5)
        c.dot(6, 8, 3.2, color)
        c.dot(6, 8, 1.2, pale)
    elif name == "flame":
        c.poly(((7, 0), (10, 5), (12, 4), (11, 10), (9, 12), (4, 12),
                (1, 10), (1, 6), (3, 7), (4, 4), (6, 6)), color)
    elif name == "document":
        c.poly(((2, 0), (8, 0), (11, 3), (11, 12), (2, 12)), color)
        c.poly(((3.5, 1.5), (7, 1.5), (9.5, 4), (9.5, 10.5), (3.5, 10.5)), pale)
        for y in (5, 7, 9):
            c.line(((4.5, y), (8.5, y)), color, 0.75)
    elif name == "gem":
        c.poly(((0, 4), (3, 1), (9, 1), (12, 4), (6, 12)), color)
        c.line(((2, 4), (10, 4)), pale, 0.5)
    elif name == "mine":
        c.rect(0, 7, 12, 4, color)
        c.poly(((1, 7), (4, 3), (8, 3), (11, 7)), color)
        c.rect(5, 1, 2, 3, color)


def mini_cards(c):
    for index, story in enumerate(MINIS):
        label, time, (color, pale, stripe), symbol, headline, summary = story
        row, col = divmod(index, 5)
        mini = c.at((28, 223, 418, 613, 808)[col], 355 + row * 70)
        mini.rect(0, 0, 188.5, 64.5, CARD, BORDER)
        mini.rect(1, 1, 186.5, 18.5, pale)
        mini.poly(((100, 19), (125, 1), (137, 1), (112, 19)), stripe)
        mini.poly(((116, 19), (141, 1), (145, 1), (120, 19)), stripe)
        icon(mini.at(7, 3.5), symbol, color, pale)
        mini.text(26, 11.5, label, BLACK, 8.5, color)
        mini.text(181, 11.5, time, BOLD, 8.5, color, "r")
        size = mini.text_size(headline, BOLD, 13, 175)
        for line_index, line in enumerate(headline):
            mini.text(7, 32.5 + line_index * 14, line, BOLD, size)
        mini.text(7, 58, summary, SEMIBOLD, 9, MUTED)


def world_map(c):
    c.text(0.5, 21, "The world at a glance", SERIF, 24)
    c.text(561.5, 16.5, "STORY LOCATIONS", BOLD, 8.5, MUTED, "r")
    c.rect(0, 32, 561.5, 158, "#e8eee8", "#a8c1b6")
    for x in range(60, 380, 29):
        c.line(((x, 44), (x, 179)), "#d7e2db", 0.5)
    for y in (52, 66, 81, 95, 110, 124, 139, 153, 168):
        c.line(((32, y), (380, y)), "#d4e1da", 0.5)
    for row, runs in enumerate(LAND_ROWS):
        for start, end in zip(runs[::2], runs[1::2]):
            for col in range(start, end):
                c.dot(35.3 + col * 3.86, 46.35 + row * 3.86, 0.95, "#648b7c")
    c.line(((412.5, 44), (412.5, 179)), "#a8c1b6", 0.75)
    for index, (region, color, locations) in enumerate(REGIONS):
        for x, y in locations:
            c.dot(x - 28, y - 577, 3.6, CARD)
            c.dot(x - 28, y - 577, 2.75, color)
        y = 51.5 + index * 15.65
        c.dot(426.5, y, 3.5, CARD)
        c.dot(426.5, y, 2.7, color)
        c.text(435.5, y + 3.75, region, BOLD, 9.5)


def markets_snapshot(c):
    c.rect(0, 0, 561.5, 53.5, "#f4eee2", BORDER)
    c.text(10, 12, "MARKETS SNAPSHOT", BLACK, 7.75, RED)
    for index, (label, value, color) in enumerate(MARKETS):
        x = 10 + index * 79
        if index:
            c.line(((x - 7, 20), (x - 7, 46)), RULE, 0.5)
        c.text(x, 28, label, BOLD, 8.5, MUTED)
        c.text(x, 41.5, value, BLACK, 12, color)


def also_in_brief(c):
    c.text(0, 11, "ALSO IN THE BRIEF", BLACK, 9.5)
    for column, stories in enumerate(BRIEF_COLUMNS):
        left = column * 288
        for row, (color, headline) in enumerate(stories):
            y = 19 + row * 14.65
            c.line(((left, y), (left + 273.5, y)), RULE, 0.5)
            c.dot(left + 3, y + 6.8, 2.2, color)
            size = c.text_size((headline,), SEMIBOLD, 10.5, 265)
            c.text(left + 9, y + 10, headline, SEMIBOLD, size)


def timeline(c):
    c.text(0.5, 21, "The day in UTC", SERIF, 24)
    for row, (time, color, label) in enumerate(TIMELINE):
        y = 32 + row * 23.5
        c.line(((0, y), (386.5, y)), RULE, 0.5)
        c.text(0, y + 13.5, time, BLACK, 10.5, color)
        c.dot(45.5, y + 12.5, 2, color)
        c.text(54, y + 15, label, SEMIBOLD, 13)
    c.line(((0, 408), (386.5, 408)), RULE, 0.5)


def render():
    image = Image.new("RGB", (SIZE * SCALE, SIZE * SCALE), PAPER)
    c = Canvas(ImageDraw.Draw(image))
    masthead(c)
    lead_cards(c)
    mini_cards(c)
    c.rect(28, 567.5, 968.5, 1.5, INK)
    c.line(((599.5, 581), (599.5, 988)), BORDER, 0.75)
    world_map(c.at(28, 577))
    markets_snapshot(c.at(28, 777))
    also_in_brief(c.at(28, 837))
    timeline(c.at(610, 577))
    c.rect(28, 990.5, 968.5, 1.5, INK)
    return image.resize((SIZE, SIZE), Image.Resampling.LANCZOS)


def main():
    output_dir = Path(os.environ.get("OUT_DIR", "/output"))
    output_dir.mkdir(parents=True, exist_ok=True)
    render().save(output_dir / "entry.png", format="PNG", optimize=True)


if __name__ == "__main__":
    main()
