#!/usr/bin/env python3
"""Render "The World Today" — Tuesday, 24 November 2026.

Draws a dense newspaper front page (1024x1024 PNG) summing up the
world's news of 24 November 2026 from 37 sourced stories in
RESEARCH.md. Pillow only, no network, fully deterministic (seeded
speckle): running it twice writes byte-identical output.
"""

import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
PAPER = (246, 241, 229)
INK = (22, 21, 19)
RED = (160, 30, 30)
GREY = (90, 86, 78)
RULE = (120, 112, 96)
SPECKLE = (214, 206, 188)
SEED = 20261124
N_SPECKLE = 2600

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
MARGIN = 36
RIGHT = 988
COL_X = (36, 361, 686)
COL_W = 301


def font(name, size):
    return ImageFont.truetype(FONT_DIR + name, size)


F_MASTHEAD = lambda: font("DejaVuSerif-Bold.ttf", 76)
F_DATELINE = lambda: font("DejaVuSerif-Bold.ttf", 20)
F_KICKER = lambda: font("DejaVuSans-Bold.ttf", 13)
F_LEAD_HEAD = lambda: font("DejaVuSerif-Bold.ttf", 38)
F_LEAD_SUB = lambda: font("DejaVuSerif.ttf", 14)
F_SECTION = lambda: font("DejaVuSans-Bold.ttf", 13)
F_SECTION_STRIP = lambda: font("DejaVuSans-Bold.ttf", 12)
F_HEAD = lambda: font("DejaVuSerif-Bold.ttf", 14)
F_SUMMARY = lambda: font("DejaVuSans.ttf", 11)
F_FOOTER = lambda: font("DejaVuSans.ttf", 10)


def wrap(draw, text, fnt, width):
    """Greedy word wrap; returns a list of lines that fit `width`."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, lines, x, y, fnt, fill, lh, max_lines=None):
    """Draw up to max_lines lines; return the y just past the last line."""
    for line in lines[:max_lines]:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += lh
    return y


def centred(draw, text, y, fnt, fill):
    w = draw.textlength(text, font=fnt)
    draw.text(((W - w) / 2, y), text, font=fnt, fill=fill)


LEAD_KICKER = "WAR IN UKRAINE \u2014 OFF LIBYA"
LEAD_HEAD = "UKRAINE SINKS RUSSIAN WARSHIP OFF LIBYA"
LEAD_SUB = (
    "Seven sea drones sink the corvette Merkury at Benghazi and hit the "
    "cargo ship Angara, Kyiv says; Libya confirms severe damage."
)

# (section, [(headline, summary), ...]) per column.
COLUMNS = [
    [
        ("WAR IN UKRAINE", [
            ("NATO meets in emergency over Poland",
             "Missiles landed in Poland; AWACS to deploy."),
            ("Russia hits Ukraine energy 100 times",
             "350,000 without power in Dnipropetrovsk."),
            ("Dymer strike toll rises to 11",
             "Day of mourning in Kyiv region after blast."),
            ("Ukraine drones hit three Russian oil sites",
             "Fires at refineries in Perm and Rostov."),
            ("Zelensky offers four-way peace talks",
             "Ready \u201cliterally tomorrow\u201d, Kyiv says."),
        ]),
        ("CLIMATE", [
            ("COP31 collapses with no climate pact",
             "Guterres calls outcome \u201cdeeply disappointing\u201d."),
            ("COP31 still adopts side deals",
             "Just transition extended; finance agreed."),
        ]),
        ("EUROPE", [
            ("Burnham defends EU deal in Parliament",
             "Critics dispute the \u00a317bn growth claim."),
        ]),
        ("MIDDLE EAST", [
            ("Israel hits Syria-Lebanon border routes",
             "IDF targets Hezbollah smuggling routes."),
        ]),
    ],
    [
        ("ASIA-PACIFIC", [
            ("Indonesia factory fire kills 24",
             "~30 still missing at candy plant in Banten."),
            ("Prabowo faces VP deadline on Monday",
             "Two names due by 23:59, MPR says."),
            ("China rejects \u201csphere of influence\u201d",
             "Beijing speaks after Shenzhen summit."),
            ("Korea readies stock stabilisation fund",
             "Kospi falls 3.06% on Monday."),
            ("Taiwan bans short-selling after rout",
             "First blanket ban since 2015, FSC says."),
            ("China buys record $13.5bn in ETFs",
             "State funds step in as CSI 300 slides."),
        ]),
        ("AMERICAS", [
            ("Nvidia reinstates Huang as CEO",
             "Trump claims credit for board U-turn."),
            ("US seeks extradition of \u201cEl Chapo Isidro\u201d",
             "FBI Top 10 fugitive caught in Sinaloa."),
        ]),
        ("ASIA-PACIFIC", [
            ("Hong Kong completes election body",
             "1,500-seat lineup set; leader pick in March."),
        ]),
    ],
    [
        ("BUSINESS & TECH", [
            ("Bitcoin rebounds from two-year low",
             "Near $61,500 after $55,130 Saturday low."),
            ("S&P 500 in correction after worst week",
             "Worst week since March 2020, down 8.61%."),
            ("Nvidia surges 35% as Huang returns",
             "AI stocks rally; Dell up 24%, Tesla 13%."),
            ("Tesla AI5 chip goes to Optimus, not cars",
             "Musk says cars stay on AI4 for now."),
        ]),
        ("SPACE, WEATHER & SPORT", [
            ("Ariane 6 launch halted; retry Tuesday",
             "Next window Tuesday 10:45 UTC."),
            ("Thanksgiving storm heads for US East",
             "Heavy rain, gusts over 50 mph forecast."),
            ("Liverpool thrash Man Utd 4\u20130",
             "Pochettino loses debut; United 19th."),
            ("Skubal agrees record $450m Mets deal",
             "$50m a year, most ever for a pitcher."),
            ("No cyclone active anywhere on Earth",
             "NHC sees none forming in next 7 days."),
        ]),
    ],
]

# Bottom strip: 9 items, round-robin 3 per mini-column.
STRIP = [
    [
        ("MIDDLE EAST", "Israeli strike kills UNRWA worker in Gaza"),
        ("AFRICA", "Ebola responders trapped by Congo fighting"),
        ("SPACE, WEATHER & SPORT", "49ers win in Mexico City; Cowboys hit 51"),
    ],
    [
        ("AFRICA", "Somalia chief justice presses court ruling"),
        ("AFRICA", "Kenya, DR Congo restore full ties"),
        ("SPACE, WEATHER & SPORT", "Jokic posts 202nd triple-double in OT win"),
    ],
    [
        ("AFRICA", "Khartoum drone strikes kill four"),
        ("SPACE, WEATHER & SPORT", "New Zealand draw with India in Wellington"),
        ("SPACE, WEATHER & SPORT", "Leeds stun Chelsea 4\u20131; Arsenal held"),
    ],
]

FOOTER = (
    "All stories reported on Monday, 23 November 2026, for Tuesday, 24 "
    "November 2026 \u00b7 Sources: Reuters, AP, AFP, BBC, CNN, UN News, "
    "UNFCCC, Arianespace, NWS, CoinDesk, Barron\u2019s, Korea JoongAng Daily, "
    "Focus Taiwan, ESPN Cricinfo, Ukrinform, Xinhua"
)


def section_header(draw, x, y, label, fnt):
    draw.rectangle([x, y + 2, x + 8, y + 10], fill=RED)
    draw.text((x + 14, y), label, font=fnt, fill=RED)


def render():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    rng = random.Random(SEED)
    for _ in range(N_SPECKLE):
        draw.point((rng.randrange(W), rng.randrange(H)), fill=SPECKLE)

    # ---- Header ----
    centred(draw, "THE WORLD TODAY", 10, F_MASTHEAD(), INK)
    centred(draw, "Tuesday, 24 November 2026", 100, F_DATELINE(), INK)
    draw.line([(MARGIN, 130), (RIGHT, 130)], fill=RULE, width=1)
    draw.line([(MARGIN, 135), (RIGHT, 135)], fill=RED, width=2)

    # ---- Lead ----
    y = 145
    draw.text((MARGIN, y), LEAD_KICKER, font=F_KICKER(), fill=RED)
    y += 20
    head_lines = wrap(draw, LEAD_HEAD, F_LEAD_HEAD(), RIGHT - MARGIN)
    y = draw_lines(draw, head_lines, MARGIN, y, F_LEAD_HEAD(), INK, 46,
                    max_lines=2)
    sub_lines = wrap(draw, LEAD_SUB, F_LEAD_SUB(), RIGHT - MARGIN)
    y = draw_lines(draw, sub_lines, MARGIN, y, F_LEAD_SUB(), GREY, 19,
                    max_lines=2)
    y += 6
    draw.line([(MARGIN, y), (RIGHT, y)], fill=RULE, width=1)
    y += 10
    lead_end = y

    # ---- Columns ----
    body_bottom = lead_end
    for x, sections in zip(COL_X, COLUMNS):
        cy = lead_end
        for label, stories in sections:
            section_header(draw, x, cy, label, F_SECTION())
            cy += 20
            for headline, summary in stories:
                lines = wrap(draw, headline, F_HEAD(), COL_W)
                cy = draw_lines(draw, lines, x, cy, F_HEAD(), INK, 17,
                                max_lines=2)
                draw.text((x, cy), summary, font=F_SUMMARY(), fill=GREY)
                cy += 14 + 8
        body_bottom = max(body_bottom, cy)

    # Vertical rules between columns, lead-end to body bottom.
    for rx in (349, 674):
        draw.line([(rx, lead_end), (rx, body_bottom)], fill=RULE, width=1)

    # ---- Bottom strip ----
    y = body_bottom + 2
    draw.line([(MARGIN, y), (RIGHT, y)], fill=RULE, width=1)
    y += 10
    strip_bottom = y
    for x, items in zip(COL_X, STRIP):
        sy = y
        for label, headline in items:
            section_header(draw, x, sy, label, F_SECTION_STRIP())
            sy += 18
            lines = wrap(draw, headline, F_HEAD(), COL_W)
            sy = draw_lines(draw, lines, x, sy, F_HEAD(), INK, 16,
                            max_lines=2)
            sy += 5
        strip_bottom = max(strip_bottom, sy)

    # ---- Footer ----
    y = strip_bottom + 8
    draw.line([(MARGIN, y), (RIGHT, y)], fill=RULE, width=1)
    y += 8
    foot_lines = wrap(draw, FOOTER, F_FOOTER(), RIGHT - MARGIN)
    for line in foot_lines[:2]:
        centred(draw, line, y, F_FOOTER(), GREY)
        y += 13
    footer_end = y

    positions = {
        "lead_end": lead_end,
        "body_bottom": body_bottom,
        "strip_bottom": strip_bottom,
        "footer_end": footer_end,
    }
    return img, positions


def main():
    img, positions = render()
    out = Path(__file__).resolve().parent / "entry.png"
    img.save(out, optimize=True)
    print(f"wrote {out} ({out.stat().st_size} bytes)")
    for key, value in positions.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
