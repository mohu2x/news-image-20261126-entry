"""Draw the 26 November 2026 world front page with Pillow."""

import os
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SCALE = 2
INK, RED, BLUE = "#202c2c", "#aa3023", "#205971"
BERRY, OCHRE, PURPLE, TEAL = "#833b55", "#805021", "#624e84", "#236763"
PAPER, CARD, MUTED = "#f9f5ec", "#fffdf8", "#455650"
BORDER, RULE = "#cec4b1", "#d9d2c4"

LEADS = [
    ("TARIFFS  /  NORTH AMERICA", "14:30", RED, ("Trump hits 14 partners", "with fresh tariffs"), "China +20% · India up to 25% · EU, Japan in net"),
    ("ENERGY  /  MIDDLE EAST", "17:30", "#115c58", ("Tankers ablaze after", "Hormuz mine blasts"), "Three vessels hit; Iran warns ships off lanes"),
    ("CONFLICT  /  EUROPE", "18:09", BERRY, ("Ukraine hits Russian air", "base, five jets out"), "MiG-31s and Su-34s damaged at Savasleyka"),
]

KINDS = {
    "conflict": (BERRY, "#e9dbdb", "#d4b9be"),
    "security": (BLUE, "#d7e0e0", "#b2c6ca"),
    "politics": (OCHRE, "#e9dfd2", "#d8c6b1"),
    "deals": (RED, "#efdad5", "#dcb0a8"),
    "tech": (PURPLE, "#e2dde6", "#c8bed0"),
    "sport": (TEAL, "#d7e0db", "#b3c8c1"),
}

MINIS = [
    ("CONFLICT", "04:45", "conflict", "burst", ("Putin vows payback for", "refinery raids"), "Retaliation 'inevitable'"),
    ("CONFLICT", "23:40", "conflict", "tower", ("Houthis hit Riyadh and", "Jazan ports"), "Saudi intercepts missiles"),
    ("CONFLICT", "02:15", "conflict", "burst", ("Gaza strikes kill 11,", "incl. two girls"), "Hamas security chief dead"),
    ("SECURITY", "08:00", "security", "shield", ("NATO boosts air watch", "on east flank"), "After missile crashes"),
    ("SECURITY", "10:56", "security", "shield", ("US weighs killing Iran's", "leaders"), "NBC: White House debate"),
    ("SECURITY", "07:00", "security", "shield", ("Seoul warns after Russian", "jets approach"), "Border isles on alert"),
    ("POLITICS", "09:00", "politics", "capitol", ("North Korea expels Swiss", "diplomat"), "Pyongyang office to shut"),
    ("DEALS", "10:30", "deals", "deal", ("Bangladesh garment pay", "up 36%"), "Minimum wage win"),
    ("DEALS", "08:00", "deals", "deal", ("Flipkart chief to step", "down in Dec"), "Krishnamurthy exits"),
    ("TECH", "06:00", "tech", "chip", ("Nvidia's Huang back", "as CEO"), "Reinstated after 11 days"),
    ("MARKETS", "15:00", "tech", "chip", ("Chip stocks down 50%", "since June"), "SOX -21% in November"),
    ("SPORT", "19:26", "sport", "medal", ("South Africa sweep", "Bangladesh 2-0"), "Mulder takes 7-31"),
    ("SPORT", "21:00", "sport", "medal", ("Real Madrid rout PSV", "5-1 in UCL"), "City 2-2 Napoli"),
    ("DISASTERS", "05:00", "security", "flame", ("Cairo tanker fire kills", "31"), "Fuel truck crash"),
    ("DISASTERS", "04:00", "security", "flame", ("Six die in US plane", "crash off coast"), "Coast Guard recovers"),
]

BRIEF = [
    (OCHRE, "WHO chief urges end to US fuel blockade on Cuba"),
    (OCHRE, "India marks Constitution Day; Nepal aid package"),
    (PURPLE, "Gukesh faces Sindarov for chess crown"),
    (BLUE, "Thanksgiving travel chaos; long airport lines"),
    (RED, "Vance's Thanksgiving F-bomb at Ohio base"),
    (RED, "Turkey pardon: bird named Feathers bolts"),
    (OCHRE, "Israeli judges urge dropping top Netanyahu charges"),
    (BLUE, "Record 2,000 migrants reach Canary Islands in a day"),
    (PURPLE, "Kuala Lumpur sues Google for $146m"),
    (OCHRE, "Australia, Solomon Islands sign pact to thwart China"),
    (BLUE, "China, Cambodia stage joint military drills"),
    (BERRY, "UN: five women killed every hour by partner or kin"),
    (TEAL, "UN chief urges talks on global AI safety framework"),
    (BLUE, "ECOWAS approves regional force roadmap to 2027"),
    (OCHRE, "India urges human control over military AI"),
    (RED, "IPL 2027 auction draws 1,220 players"),
    (TEAL, "Melania helps reunite nine Ukrainian, Russian kids"),
]

TIMELINE = [
    ("00:50", OCHRE, "Australia–Solomon pact"), ("02:15", BERRY, "Gaza strikes"),
    ("04:45", BERRY, "Putin vows retaliation"), ("05:00", BLUE, "Cairo tanker fire"),
    ("06:00", PURPLE, "Huang back at Nvidia"), ("07:00", BLUE, "Seoul jet warning"),
    ("08:00", BLUE, "NATO air watch"), ("09:00", OCHRE, "N. Korea expels Swiss"),
    ("10:30", RED, "Bangladesh wage hike"), ("12:00", BERRY, "UN: women killed hourly"),
    ("14:30", RED, "Trump tariff sweep"), ("15:00", RED, "Chip stocks slide"),
    ("17:30", RED, "Hormuz tanker blasts"), ("18:09", BERRY, "Savasleyka air strike"),
    ("19:26", TEAL, "S. Africa sweep Bangladesh"), ("21:00", TEAL, "Real Madrid 5-1 PSV"),
]

MARKETS = [("Nasdaq", "-2.0%", RED), ("KOSPI", "-6.2%", RED),
           ("Nikkei", "-3.0%", RED), ("SOX Nov", "-21%", RED),
           ("US 10-yr", "4.84%", INK), ("VIX Nov", "+60%", RED),
           ("Dollar", "103.6", INK)]

REGIONS = [
    ("North America", "#235483", [(116, 665), (150, 664), (166, 660)]),
    ("Latin America", "#947319", [(161, 691)]),
    ("Europe", "#734581", [(231, 663), (241, 653), (248, 660), (282, 650)]),
    ("Middle East", "#b53026", [(268, 671), (274, 668), (279, 677), (284, 668), (289, 676)]),
    ("Africa", "#406e37", [(257, 712), (242, 671), (221, 687)]),
    ("East Asia", "#a4421d", [(343, 679), (347, 663), (353, 664), (357, 669), (369, 667)]),
    ("Southeast Asia", "#12665f", [(327, 685), (336, 682)]),
    ("Pacific", "#2f6b98", [(389, 710)]),
    ("Global", "#5a6070", []),
]

FONTS = {
    "display": "NotoSerifDisplay-Black.ttf",
    "serif": "NotoSerifDisplay-Bold.ttf",
    "heavy": "NotoSans-Black.ttf",
    "bold": "NotoSans-Bold.ttf",
    "semi": "NotoSans-SemiBold.ttf",
    "regular": "NotoSans-Regular.ttf",
}


@lru_cache(maxsize=None)
def typeface(name, size):
    path = Path("/usr/share/fonts/truetype/noto") / FONTS[name]
    return ImageFont.truetype(str(path), round(size * SCALE))


class Painter:
    """Draw using final-image coordinates on a supersampled canvas."""

    def __init__(self, target, x=0, y=0):
        self.draw = target
        self.x, self.y = x, y

    def child(self, x, y):
        return Painter(self.draw, self.x + x, self.y + y)

    def xy(self, x, y):
        return round((x + self.x) * SCALE), round((y + self.y) * SCALE)

    def rectangle(self, x, y, w, h, fill, outline=None):
        left, top = self.xy(x, y)
        right, bottom = self.xy(x + w, y + h)
        self.draw.rectangle((left, top, right - 1, bottom - 1), fill=fill,
                            outline=outline, width=SCALE)

    def circle(self, x, y, r, fill, outline=None):
        left, top = self.xy(x - r, y - r)
        right, bottom = self.xy(x + r, y + r)
        self.draw.ellipse((left, top, right - 1, bottom - 1), fill=fill,
                          outline=outline, width=SCALE)

    def polygon(self, points, color):
        self.draw.polygon([self.xy(x, y) for x, y in points], fill=color)

    def stroke(self, points, color, width=1):
        self.draw.line([self.xy(x, y) for x, y in points], fill=color,
                       width=max(1, round(width * SCALE)), joint="curve")

    def text(self, x, y, value, face, size, color=INK, align="l"):
        self.draw.text(self.xy(x, y), value, font=typeface(face, size),
                       fill=color, anchor=align + "s")

    def fit(self, strings, face, size, width):
        while max(typeface(face, size).getlength(s) for s in strings) > width * SCALE:
            size -= 0.5
        return size


def masthead(p):
    p.rectangle(28, 23.5, 968.5, 2, INK)
    p.text(28, 43.5, "WORLD IN ONE IMAGE", "heavy", 12, "#7c403a")
    p.text(996.5, 42.5, "DAILY WORLD BRIEF", "bold", 10, MUTED, "r")
    p.text(26.5, 98, "Thursday 26 November 2026", "display", 60)
    p.text(28.5, 124.5, "35 dated stories · 9 regions · 14 fields", "semi", 13, MUTED)
    sections = [("MARKETS", "#a63e34"), ("WORLD", "#235a71"),
                ("CONFLICT", "#853e55"), ("POLITICS", "#835526"),
                ("TECHNOLOGY", "#665085"), ("SCIENCE", "#276964")]
    for i, (name, color) in enumerate(sections):
        x = 28 + i * 161.4
        p.rectangle(x, 135, 161.4, 24.5, color)
        p.text(x + 80.7, 149.5, name, "heavy", 9.5, "#ffffff", "m")
        if i:
            p.stroke([(x, 135), (x, 159)], "#d0b9ae", .5)


def icon(p, kind, color, background):
    if kind == "burst":
        p.polygon([(7, 0), (8, 4), (13, 2), (10, 6), (13, 9), (9, 8),
                   (7, 13), (5, 9), (0, 11), (3, 7), (0, 5), (5, 5)], color)
    elif kind == "tower":
        p.polygon([(1, 12), (1, 10), (3, 10), (4, 2), (5, 2), (5, 0),
                   (7, 0), (7, 2), (8, 2), (9, 10), (11, 10), (11, 12)], color)
    elif kind == "shield":
        p.polygon([(1, 2), (6, 0), (12, 2), (11, 7), (9, 10), (6, 12), (3, 10), (1, 7)], color)
        p.polygon([(2.5, 3), (6, 1.5), (10.5, 3), (10, 6), (6, 10), (3, 7)], background)
        p.stroke([(3.5, 5.7), (5.6, 7.2), (9.5, 4)], color, 1.3)
    elif kind == "capitol":
        p.polygon([(0, 4), (6, 0), (12, 4)], color)
        p.rectangle(1, 10, 11, 1.5, color)
        for x in (3, 5.5, 8):
            p.rectangle(x, 5, 1.5, 4, color)
    elif kind == "deal":
        p.polygon([(0, 4), (4, 1), (6, 2), (4, 5), (6, 7), (9, 5),
                   (11, 7), (8, 11), (5, 12), (1, 8)], color)
        p.polygon([(5, 4), (8, 1), (11, 1), (13, 4), (11, 6), (8, 4), (6, 6)], color)
    elif kind == "chip":
        p.rectangle(3, 3, 7, 7, color)
        p.rectangle(5, 5, 3, 3, background)
        for n in (4, 6, 8):
            p.stroke([(1, n), (3, n)], color)
            p.stroke([(10, n), (12, n)], color)
            p.stroke([(n, 1), (n, 3)], color)
            p.stroke([(n, 10), (n, 12)], color)
    elif kind == "medal":
        p.stroke([(2, 1), (5, 5), (7, 5), (11, 1)], color, 1.5)
        p.circle(6, 8, 3.2, color)
        p.circle(6, 8, 1.2, background)
    elif kind == "flame":
        p.polygon([(7, 0), (10, 5), (12, 4), (11, 10), (9, 12), (4, 12),
                   (1, 10), (1, 6), (3, 7), (4, 4), (6, 6)], color)


def tariff_art(p):
    p.rectangle(0, 0, 314, 86, "#f1dbd2")
    p.text(22, 13, "TARIFF SHOCK", "heavy", 7.5, RED)
    for x in (22, 66, 100, 134, 169, 204, 238, 273, 298):
        p.stroke([(x, 15), (x, 74)], "#dcb5a7", .5)
    for y in (17, 31, 45, 59, 73):
        p.stroke([(19, y), (299, y)], "#dcb5a7", .5)
    points = [(22, 29), (43, 23), (69, 27), (91, 18), (116, 36),
              (138, 33), (160, 40), (178, 33), (204, 54), (222, 48),
              (242, 60), (264, 57), (292, 72)]
    for x, y in [(212, 54), (230, 42), (249, 48), (268, 52)]:
        p.rectangle(x, y, 10, 61 - y, "#d3a497")
    p.polygon(points + [(292, 74), (22, 74)], "#e9cac0")
    p.stroke(points, RED, 2)
    for i in (0, 3, 6, 9, 12):
        x, y = points[i]
        p.circle(x, y, 3.5, RED)
        p.circle(x, y, 2, "#fff1e8")


def hormuz_art(p):
    p.rectangle(0, 0, 314, 86, "#d6e9e5")
    p.polygon([(0, 0), (145, 0), (132, 7), (114, 9), (107, 15), (79, 21),
               (67, 32), (47, 37), (38, 44), (0, 52)], "#81b1aa")
    p.polygon([(314, 31), (314, 86), (261, 86), (248, 78), (255, 69),
               (277, 61), (286, 54), (276, 49), (289, 39)], "#9ac3bc")
    p.text(17, 13.5, "STRAIT OF HORMUZ", "heavy", 7.5, "#185956")
    for x, y, end in [(122, 17, 170), (188, 17, 248), (203, 23, 254),
                      (75, 39, 105), (41, 63, 87), (31, 72, 106),
                      (107, 79, 164), (141, 71, 198), (221, 66, 255)]:
        p.stroke([(x, y), (end, y)], "#65a59e", .7)
    p.polygon([(59, 50), (249, 50), (232, 65), (92, 65), (73, 58)], "#18514f")
    p.stroke([(89, 59), (235, 59)], "#59948c", .7)
    for x, w in [(91, 16), (108.5, 20), (130, 20), (151.5, 20), (173, 19)]:
        p.rectangle(x, 42, w, 8, "#e3b979")
    p.rectangle(198, 34.5, 34, 16, "#19625d")
    p.rectangle(202, 37, 23, 3, "#f0d9a5")
    p.stroke([(214, 35), (214, 26.5), (223, 26.5)], "#1c645f")
    p.stroke([(214, 30), (229, 30)], "#1c645f")
    p.circle(258, 37, 7, None, "#b88d66")
    p.circle(258, 37, 4.5, None, "#c29f76")
    p.circle(258, 37, 2.25, "#b75d37")


def airfield_art(p):
    p.rectangle(0, 0, 314, 86, "#eadbd7")
    p.text(17, 13, "SAVASLEYKA AIR BASE", "heavy", 7.5, BERRY)
    p.polygon([(0, 48), (54, 40), (104, 44), (150, 36), (204, 42),
               (257, 35), (314, 40), (314, 86), (0, 86)], "#c3a9a6")
    p.polygon([(0, 72), (314, 49), (314, 75), (0, 86)], "#776c70")
    p.stroke([(14, 79), (300, 60)], "#e9d4bf")
    for x in range(31, 272, 60):
        y = 74 - (x - 31) / 15
        p.stroke([(x, y), (x + 17, y - 1)], "#f2dfca", 1.3)
    for x, y in [(86, 47), (207, 39)]:
        p.polygon([(x - 33, y + 1), (x - 8, y - 2), (x + 1, y - 9),
                   (x + 6, y - 9), (x + 5, y - 2), (x + 29, y + 1),
                   (x + 31, y + 4), (x + 4, y + 4), (x, y + 9),
                   (x - 5, y + 9), (x - 6, y + 4), (x - 32, y + 4)], "#554b56")
    for x, y, r in [(147, 34, 9), (156, 28, 11), (167, 34, 8),
                    (258, 29, 7), (266, 24, 9), (276, 29, 7)]:
        p.circle(x, y, r, "#a67c78")
    p.polygon([(145, 39), (151, 27), (155, 35), (161, 23), (166, 39)], "#c7765b")
    p.polygon([(257, 34), (262, 25), (265, 31), (270, 22), (275, 34)], "#c7765b")
    # Warm blast cores and wing highlights give the small dawn scene more depth.
    p.polygon([(151, 39), (155, 33), (158, 39)], "#e3ab79")
    p.polygon([(262, 34), (265, 29), (268, 34)], "#e3ab79")
    p.stroke([(61, 48), (79, 46)], "#8c7d80", .8)
    p.stroke([(182, 40), (200, 38)], "#8c7d80", .8)


def draw_leads(p):
    for x, story, artwork in zip([28, 354, 680], LEADS, [tariff_art, hormuz_art, airfield_art]):
        card = p.child(x, 170)
        card.rectangle(0, 0, 316.5, 178.5, CARD, BORDER)
        artwork(card.child(1, 1))
        kicker, when, color, lines, summary = story
        card.text(10, 100.5, kicker, "heavy", 8.5, color)
        card.text(306, 100.5, when, "bold", 8.5, MUTED, "r")
        size = card.fit(lines, "serif", 23.5, 296)
        for i, line in enumerate(lines):
            card.text(10, 128 + 24 * i, line, "serif", size)
        card.text(10, 169, summary, "semi", card.fit([summary], "semi", 10, 296), MUTED)


def draw_minis(p):
    for i, (label, when, kind, symbol, lines, summary) in enumerate(MINIS):
        row, col = divmod(i, 5)
        card = p.child(28 + col * 195, 355 + row * 70)
        color, tint, stripe = KINDS[kind]
        card.rectangle(0, 0, 188.5, 64.5, CARD, BORDER)
        card.rectangle(1, 1, 186.5, 18.5, tint)
        card.polygon([(100, 19), (125, 1), (137, 1), (112, 19)], stripe)
        card.polygon([(116, 19), (141, 1), (145, 1), (120, 19)], stripe)
        icon(card.child(7, 3.5), symbol, color, tint)
        card.text(26, 11.5, label, "heavy", 8.5, color)
        card.text(181, 11.5, when, "bold", 8.5, color, "r")
        size = card.fit(lines, "bold", 13, 175)
        for j, line in enumerate(lines):
            card.text(7, 32.5 + 14 * j, line, "bold", size)
        card.text(7, 58, summary, "semi", 9, MUTED)


# Dot coverage is sampled on the front page's world-map grid, west to east.
LAND_MASK = (
    "0000000000000fffff00000 0000000000000ffe7c70000 00003fe000000ffc1c7f000 "
    "01ffffffe0e003feffffff8 3ffffffffff0383fffffff9 03ffffffff780039e1ffff0 "
    "010ffffffff88000e1ff878 0187ffffcee0c000f7ff000 000ffffff8f00003fffc000 "
    "0007ffffc8e700037ffc000 00111fffdf40400013fc000 00005fffd200400013f8000 "
    "00047fffd00f80001ff8000 00007fffadffc00019e8000 00000fff0dffe00011e0000 "
    "00000ffc7fffe00031c0000 00000f187bfff0000700000 00000a181ffff0000c00000 "
    "000082101fffc0039800000 000022001fff800ff000000 000032000ff8000ff000000 "
    "000c340007f8003fe000000 0038180007f800ffe000000 0000000007f000ffe000000 "
    "0017800017f0007fc000000 001fe00013f0007f8000000 003fe00011f0003f8000000 "
    "007fe00001e0001f8000000 007fe00000e0000f8000000 0018000000000007c000000 "
    "0010000000000003c000000 0820000000000003c000000 0400000000000001c000000 "
    "0000000000000000c000000"
).split()


def draw_map(p):
    p.text(.5, 21, "The world at a glance", "serif", 24)
    p.text(561.5, 16.5, "STORY LOCATIONS", "bold", 8.5, MUTED, "r")
    p.rectangle(0, 32, 561.5, 158, "#e8eee8", "#a8c1b6")
    for x in range(60, 380, 29):
        p.stroke([(x, 44), (x, 179)], "#d7e2db", .5)
    for y in [52, 66, 81, 95, 110, 124, 139, 153, 168]:
        p.stroke([(32, y), (380, y)], "#d4e1da", .5)
    for row, encoded in enumerate(LAND_MASK):
        bits = int(encoded, 16)
        for col in range(90):
            if bits & (1 << col):
                p.circle(35.3 + col * 3.86, 46.35 + row * 3.86, .95, "#648b7c")
    p.stroke([(412.5, 44), (412.5, 179)], "#a8c1b6", .75)
    for i, (name, color, places) in enumerate(REGIONS):
        for x, y in places:
            p.circle(x - 28, y - 577, 3.6, CARD)
            p.circle(x - 28, y - 577, 2.75, color)
        y = 51.5 + 15.65 * i
        p.circle(426.5, y, 3.5, CARD)
        p.circle(426.5, y, 2.7, color)
        p.text(435.5, y + 3.75, name, "bold", 9.5)


def draw_markets(p):
    p.rectangle(0, 0, 561.5, 53.5, "#f4eee2", BORDER)
    p.text(10, 12, "MARKETS SNAPSHOT", "heavy", 7.75, RED)
    for i, (label, value, color) in enumerate(MARKETS):
        x = 10 + i * 79
        if i:
            p.stroke([(x - 7, 20), (x - 7, 46)], RULE, .5)
        p.text(x, 28, label, "bold", 8.5, MUTED)
        p.text(x, 41.5, value, "heavy", 12, color)


def draw_brief(p):
    p.text(0, 11, "ALSO IN THE BRIEF", "heavy", 9.5)
    for i, (color, headline) in enumerate(BRIEF):
        col = 0 if i < 9 else 1
        row = i if col == 0 else i - 9
        x, y = col * 288, 19 + row * 14.65
        p.stroke([(x, y), (x + 273.5, y)], RULE, .5)
        p.circle(x + 3, y + 6.8, 2.2, color)
        p.text(x + 9, y + 10, headline, "semi", p.fit([headline], "semi", 10.5, 265))


def draw_timeline(p):
    p.text(.5, 21, "The day in UTC", "serif", 24)
    for i, (when, color, label) in enumerate(TIMELINE):
        y = 32 + 23.5 * i
        p.stroke([(0, y), (386.5, y)], RULE, .5)
        p.text(0, y + 13.5, when, "heavy", 10.5, color)
        p.circle(45.5, y + 12.5, 2, color)
        p.text(54, y + 15, label, "semi", 13)
    p.stroke([(0, 408), (386.5, 408)], RULE, .5)


def render():
    image = Image.new("RGB", (1024 * SCALE, 1024 * SCALE), PAPER)
    p = Painter(ImageDraw.Draw(image))
    masthead(p)
    draw_leads(p)
    draw_minis(p)
    p.rectangle(28, 567.5, 968.5, 1.5, INK)
    p.stroke([(599.5, 581), (599.5, 988)], BORDER, .75)
    draw_map(p.child(28, 577))
    draw_markets(p.child(28, 777))
    draw_brief(p.child(28, 837))
    draw_timeline(p.child(610, 577))
    p.rectangle(28, 990.5, 968.5, 1.5, INK)
    return image.resize((1024, 1024), Image.Resampling.LANCZOS)


def main():
    destination = Path(os.environ.get("OUT_DIR", "/output"))
    destination.mkdir(parents=True, exist_ok=True)
    render().save(destination / "entry.png", format="PNG", optimize=True)


if __name__ == "__main__":
    main()
