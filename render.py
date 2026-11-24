#!/usr/bin/env python3
"""Render the front page for make.fun news-image-20261124.

Pillow only, no network, deterministic (seeded speckle).
Canvas 1024x1024, broadsheet layout per BUILD-LOG.md layout spec and
the story data in RESEARCH.md (37 items: lead + 27 column + 9 strip).
"""
import random

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
PAPER = (246, 241, 229)
INK = (22, 21, 19)
RED = (160, 30, 30)
GREY = (90, 86, 78)
RULE = (120, 112, 96)
SPECKLE = (214, 206, 188)
SEED = 20261124
NSPECKLE = 2600

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(f"{FONT_DIR}/{name}.ttf", size)


F_MASTHEAD = font("DejaVuSerif-Bold", 76)
F_DATELINE = font("DejaVuSerif-Bold", 20)
F_KICKER = font("DejaVuSans-Bold", 13)
F_LEAD_HEAD = font("DejaVuSerif-Bold", 38)
F_LEAD_SUB = font("DejaVuSerif", 14)
F_SECTION = font("DejaVuSans-Bold", 13)
F_SECTION_STRIP = font("DejaVuSans-Bold", 12)
F_HEAD = font("DejaVuSerif-Bold", 14)
F_SUM = font("DejaVuSans", 11)
F_FOOT = font("DejaVuSans", 10)

COL_X = (36, 361, 686)
COL_W = 301
PAGE_LEFT = 36
PAGE_RIGHT = 988

LEAD_KICKER = "WAR IN UKRAINE \u2014 OFF LIBYA"
LEAD_HEAD = "UKRAINE SINKS RUSSIAN WARSHIP OFF LIBYA"
LEAD_SUB = ("Seven sea drones sink the corvette Merkury at Benghazi and hit "
            "the cargo ship Angara, Kyiv says; Libya confirms severe damage.")

COLUMNS = [
    [("WAR IN UKRAINE", [
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
        ("Israel hits Syria\u2013Lebanon border routes",
         "IDF targets Hezbollah smuggling routes."),
     ])],
    [("ASIA-PACIFIC", [
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
     ])],
    [("BUSINESS & TECH", [
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
     ])],
]

# Bottom strip: 9 items, round-robin 3 per mini-column (RESEARCH.md order).
STRIP = [
    [("MIDDLE EAST", "Israeli strike kills UNRWA worker in Gaza"),
     ("AFRICA", "Ebola responders trapped by Congo fighting"),
     ("SPACE, WEATHER & SPORT", "49ers win in Mexico City; Cowboys hit 51")],
    [("AFRICA", "Somalia chief justice presses court ruling"),
     ("AFRICA", "Kenya, DR Congo restore full ties"),
     ("SPACE, WEATHER & SPORT", "Jokic posts 202nd triple-double in OT win")],
    [("AFRICA", "Khartoum drone strikes kill four"),
     ("SPACE, WEATHER & SPORT", "New Zealand draw with India in Wellington"),
     ("SPACE, WEATHER & SPORT", "Leeds stun Chelsea 4\u20131; Arsenal held")],
]

FOOTER = ("All stories reported on Monday, 23 November 2026, for Tuesday, "
          "24 November 2026 \u00b7 Sources: Reuters, AP, AFP, BBC, CNN, "
          "UN News, UNFCCC, Arianespace, NWS, CoinDesk, Barron\u2019s, Korea "
          "JoongAng Daily, Focus Taiwan, ESPN Cricinfo, Ukrinform, Xinhua")


def wrap(draw, text, fnt, width, max_lines=None):
    """Greedy word wrap; returns at most max_lines lines."""
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    if max_lines is not None:
        lines = lines[:max_lines]
    return lines


def section_header(draw, x, y, label, fnt):
    """Red 9x9 square + red bold label; block height returned by caller."""
    draw.rectangle([x, y + 2, x + 8, y + 10], fill=RED)
    draw.text((x + 14, y), label, font=fnt, fill=RED)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    # Seeded paper speckle, drawn first so text stays clean.
    rng = random.Random(SEED)
    for _ in range(NSPECKLE):
        draw.point((rng.randrange(W), rng.randrange(H)), fill=SPECKLE)

    # Header: masthead, dateline, rules. Header ends y=145.
    draw.text((W // 2, 10), "THE WORLD TODAY", font=F_MASTHEAD,
              fill=INK, anchor="ma")
    draw.text((W // 2, 100), "Tuesday, 24 November 2026", font=F_DATELINE,
              fill=INK, anchor="ma")
    draw.line([(PAGE_LEFT, 130), (PAGE_RIGHT, 130)], fill=RULE, width=1)
    draw.line([(PAGE_LEFT, 135), (PAGE_RIGHT, 135)], fill=RED, width=2)

    # Lead.
    y = 153
    draw.text((PAGE_LEFT, y), LEAD_KICKER, font=F_KICKER, fill=RED)
    head_lines = wrap(draw, LEAD_HEAD, F_LEAD_HEAD, PAGE_RIGHT - PAGE_LEFT,
                      max_lines=2)
    hy = y + 20
    for line in head_lines:
        draw.text((PAGE_LEFT, hy), line, font=F_LEAD_HEAD, fill=INK)
        hy += 46
    sub_lines = wrap(draw, LEAD_SUB, F_LEAD_SUB, PAGE_RIGHT - PAGE_LEFT,
                     max_lines=2)
    sy = hy
    for line in sub_lines:
        draw.text((PAGE_LEFT, sy), line, font=F_LEAD_SUB, fill=GREY)
        sy += 19
    lead_rule_y = sy + 6
    draw.line([(PAGE_LEFT, lead_rule_y), (PAGE_RIGHT, lead_rule_y)],
              fill=RULE, width=1)
    col_start = lead_rule_y + 10
    lead_end = lead_rule_y

    # Columns.
    body_bottom = col_start
    for ci, sections in enumerate(COLUMNS):
        x = COL_X[ci]
        y = col_start
        for label, stories in sections:
            section_header(draw, x, y, label, F_SECTION)
            y += 20
            for head, summary in stories:
                lines = wrap(draw, head, F_HEAD, COL_W, max_lines=2)
                for line in lines:
                    draw.text((x, y), line, font=F_HEAD, fill=INK)
                    y += 17
                draw.text((x, y), summary, font=F_SUM, fill=GREY)
                y += 14 + 8
        body_bottom = max(body_bottom, y - 8)

    # Vertical rules between columns, lead rule to body bottom.
    for vx in (COL_X[0] + COL_W + 12, COL_X[1] + COL_W + 12):
        draw.line([(vx, col_start), (vx, body_bottom)], fill=RULE, width=1)

    # Bottom strip.
    strip_rule_y = body_bottom + 2
    draw.line([(PAGE_LEFT, strip_rule_y), (PAGE_RIGHT, strip_rule_y)],
              fill=RULE, width=1)
    strip_y = strip_rule_y + 10
    strip_bottom = strip_y
    for ci, items in enumerate(STRIP):
        x = COL_X[ci]
        y = strip_y
        for label, head in items:
            section_header(draw, x, y, label, F_SECTION_STRIP)
            y += 18
            lines = wrap(draw, head, F_HEAD, COL_W, max_lines=2)
            for line in lines:
                draw.text((x, y), line, font=F_HEAD, fill=INK)
                y += 16
            y += 5
        strip_bottom = max(strip_bottom, y - 5)

    # Footer: rule, +8, two centred lines (DejaVuSans 10 grey, 13px).
    foot_rule_y = strip_bottom + 8
    draw.line([(PAGE_LEFT, foot_rule_y), (PAGE_RIGHT, foot_rule_y)],
              fill=RULE, width=1)
    foot_lines = wrap(draw, FOOTER, F_FOOT, PAGE_RIGHT - PAGE_LEFT,
                      max_lines=2)
    fy = foot_rule_y + 10
    for line in foot_lines:
        draw.text((W // 2, fy), line, font=F_FOOT, fill=GREY, anchor="ma")
        fy += 13
    footer_end = fy - 13 + 10

    img.save("entry.png", optimize=True)
    print(f"lead_end={lead_end} body_bottom={body_bottom} "
          f"strip_bottom={strip_bottom} footer_end={footer_end}")
    assert footer_end <= 1020, f"footer overflows frame: {footer_end}"


if __name__ == "__main__":
    main()
