#!/usr/bin/env python3
"""Draw the news-23 b183 numbers-led front page (1024x1024)."""
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (253, 253, 248)
INK = (17, 17, 17)
RED = (185, 28, 28)
DARKRED = (140, 20, 20)
NAVY = (30, 58, 95)
GOLD = (176, 124, 0)
GRAY = (102, 102, 102)
LIGHT = (238, 238, 232)
RULE = (200, 200, 192)
BLUE_BG = (214, 228, 240)
LAND = (190, 200, 180)

F_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
F_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
F_SANSB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def fit(draw, text, fnt, max_w, ellip="..."):
    """Truncate text to max_w (pixels), adding ellipsis if needed."""
    if draw.textlength(text, font=fnt) <= max_w:
        return text
    lo, hi = 0, len(text)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if draw.textlength(text[:mid] + ellip, font=fnt) <= max_w:
            lo = mid
        else:
            hi = mid - 1
    return text[:lo] + ellip


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap into lines fitting max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def chip(draw, x, y, label, kind):
    """REPORTED (navy) / CLAIM (red) chip on its own line. Returns width."""
    f = font(F_SANSB, 8)
    w = int(draw.textlength(label, font=f)) + 8
    h = 12
    col = NAVY if kind == "REPORTED" else RED
    draw.rounded_rectangle([x, y, x + w, y + h], radius=2, fill=col)
    draw.text((x + 4, y + 2), label, font=f, fill=(255, 255, 255))
    return w


def draw_numbers(draw):
    """BIG number grid first: 2 rows x 5 cells, y 8..118."""
    nums = [
        ("-3.3%", "KOSPI ROUT"),
        ("5.3", "US-CHINA GAP"),
        ("11,762", "EBOLA CASES DRC"),
        ("10T won", "SEOUL RESCUE FUND"),
        ("2%", "BILLIONAIRE TAX"),
        ("$450M", "SKUBAL METS DEAL"),
        ("165", "RUSSIAN MISSILES / WEEK"),
        ("12,000", "CLEARED, MANCHESTER"),
        ("264 kg", "EXPLOSIVES, LEBANON"),
        ("$107.3B", "ANTHROPIC IPO"),
    ]
    x0, y0 = 8, 8
    cw, ch = 201, 54
    f_num = font(F_SANSB, 24)
    f_lab = font(F_SANSB, 8)
    for i, (num, lab) in enumerate(nums):
        r, c = divmod(i, 5)
        x = x0 + c * (cw + 1)
        y = y0 + r * (ch + 2)
        draw.rectangle([x, y, x + cw, y + ch], outline=RULE, width=1)
        col = RED if i in (0, 1, 6) else INK
        draw.text((x + 6, y + 4), num, font=f_num, fill=col)
        draw.text((x + 6, y + 34), fit(draw, lab, f_lab, cw - 12), font=f_lab, fill=GRAY)
    draw.rectangle([x0, y0, x0 + 5 * cw + 4, y0 + 2 * ch + 2], outline=INK, width=2)


def draw_masthead(draw):
    """Masthead + date + kicker, y 124..200."""
    draw.text((512, 128), "THE WORLD TODAY", font=font(F_SERIF, 40),
              fill=INK, anchor="ma")
    draw.text((512, 172), "MONDAY 23 NOVEMBER 2026  |  ONE DAY, ONE PAGE, EVERY STORY THAT MATTERED",
              font=font(F_SANSB, 11), fill=NAVY, anchor="ma")
    draw.line([8, 196, 1016, 196], fill=INK, width=2)
    draw.text((512, 202), "Asia's AI sell-off, a call to regulate AI before it is too late, and America's narrowest lead over China since 2018.",
              font=font(F_SANS, 11), fill=GRAY, anchor="ma")


def draw_region_bar(draw):
    """Region bar with counts, y 222..244."""
    regions = [("ASIA-PACIFIC", 7), ("AMERICAS", 8), ("MIDDLE EAST", 6),
               ("EUROPE", 5), ("AFRICA", 3), ("WORLD", 2)]
    x = 8
    f = font(F_SANSB, 10)
    total_w = 1008
    per = total_w // len(regions)
    for i, (name, n) in enumerate(regions):
        cx = x + i * per + per // 2
        draw.text((cx, 226), f"{name} {n}", font=f, fill=INK, anchor="ma")
    draw.line([8, 244, 1016, 244], fill=RULE, width=1)


def draw_hero_kospi(draw, x, y, w, h):
    """Scene 1: Seoul skyline + falling chart."""
    # sky band
    draw.rectangle([x, y, x + w, y + h], fill=(235, 240, 248))
    # buildings with lit windows
    import random
    rnd = random.Random(23)
    bx = x + 6
    while bx < x + w - 30:
        bw = rnd.randint(22, 34)
        bh = rnd.randint(46, 78)
        by = y + h - 58 - bh
        draw.rectangle([bx, by, bx + bw, y + h - 58], fill=(52, 68, 92))
        for wy in range(by + 6, y + h - 62, 10):
            for wx in range(bx + 4, bx + bw - 4, 8):
                if rnd.random() < 0.5:
                    draw.rectangle([wx, wy, wx + 3, wy + 4], fill=(255, 214, 90))
        bx += bw + 4
    # falling orange chart line (clear of the -3.3% label area, top-left)
    pts = [(x + 10, y + 12), (x + 60, y + 22), (x + 110, y + 18),
           (x + 160, y + 34), (x + 210, y + 30), (x + 260, y + 48),
           (x + 300, y + 44), (x + w - 8, y + 62)]
    draw.line(pts, fill=(230, 110, 20), width=4)
    draw.text((x + 10, y + 70), "-3.3%", font=font(F_SANSB, 26), fill=RED)
    draw.text((x + 108, y + 78), "KOSPI 4,708.54", font=font(F_SANSB, 13), fill=INK)


def draw_hero_guterres(draw, x, y, w, h):
    """Scene 2: globe + flags, Bridgetown summit."""
    draw.rectangle([x, y, x + w, y + h], fill=(232, 240, 232))
    cx, cy, r = x + w // 2, y + 56, 40
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(120, 170, 210),
                 outline=NAVY, width=2)
    # latitude chords clipped inside the circle
    import math
    for dy in (-20, 0, 20):
        half = int(math.sqrt(max(r * r - dy * dy, 0)))
        draw.line([cx - half, cy + dy, cx + half, cy + dy], fill=(255, 255, 255), width=2)
    draw.ellipse([cx - 11, cy - r, cx + 11, cy + r], outline=(255, 255, 255), width=2)
    # 4 small flags below the globe
    flag_cols = [(200, 40, 40), (40, 90, 200), (240, 200, 40), (40, 140, 80)]
    fx = x + w // 2 - 66
    for col in flag_cols:
        draw.rectangle([fx, y + 102, fx + 28, y + 114], fill=col, outline=INK)
        draw.line([fx, y + 102, fx, y + 122], fill=INK, width=2)
        fx += 36
    draw.text((x + w // 2, y + 124), "BRIDGETOWN SUMMIT", font=font(F_SANSB, 10),
              fill=INK, anchor="ma")


def draw_hero_power(draw, x, y, w, h):
    """Scene 3: Asia Power Index bars."""
    draw.rectangle([x, y, x + w, y + h], fill=(248, 240, 220))
    bars = [("US", 78.9, NAVY), ("CHINA", 73.6, RED), ("INDIA", 40.5, GOLD)]
    by = y + 14
    f_lab = font(F_SANSB, 11)
    f_val = font(F_SANSB, 12)
    for name, val, col in bars:
        draw.text((x + 10, by), name, font=f_lab, fill=INK)
        bw = int((val / 80.0) * (w - 90))
        draw.rectangle([x + 74, by + 2, x + 74 + bw, by + 16], fill=col)
        draw.text((x + 78 + bw, by + 1), f"{val}", font=f_val, fill=INK)
        by += 26
    draw.text((x + 10, by + 4), "GAP 5.3 — NARROWEST SINCE 2018",
              font=font(F_SANSB, 11), fill=RED)
    draw.text((x + 10, by + 24), "US DIPLOMATIC INFLUENCE -6 TO 76.7",
              font=font(F_SANS, 9), fill=GRAY)


def draw_heroes(draw):
    """3 hero scenes, y 250..470. Headlines sit BELOW each scene with a gap."""
    heroes = [
        ("AI ROUT HITS ASIA",
         "Kospi sheds 161 points as AI stocks plunge; Samsung -3.1%, SK Hynix -2.5%.",
         "YONHAP", "REPORTED", draw_hero_kospi),
        ("GUTERRES: REGULATE AI BEFORE IT'S TOO LATE",
         "Bridgetown summit backs a risk framework; a blueprint, not a treaty.",
         "UN NEWS", "REPORTED", draw_hero_guterres),
        ("US LEAD OVER CHINA AT RECORD LOW",
         "Asia Power Index 2026: US 78.9, China 73.6; India third at 40.5.",
         "LOWY INSTITUTE", "REPORTED", draw_hero_power),
    ]
    x0, y0 = 8, 250
    cw = 328
    f_head = font(F_SANSB, 15)
    f_body = font(F_SANS, 10)
    f_src = font(F_SANSB, 8)
    for i, (head, body, src, kind, scene_fn) in enumerate(heroes):
        x = x0 + i * (cw + 6)
        scene_h = 142
        draw.rectangle([x, y0, x + cw, y0 + scene_h], outline=INK, width=1)
        scene_fn(draw, x + 1, y0 + 1, cw - 2, scene_h - 2)
        # headline below scene, clear gap (strip is above the scene, not the text)
        hy = y0 + scene_h + 6
        lines = wrap(draw, head, f_head, cw - 4)
        for ln in lines[:2]:
            draw.text((x, hy), ln, font=f_head, fill=INK)
            hy += 18
        for ln in wrap(draw, body, f_body, cw - 4)[:2]:
            draw.text((x, hy), ln, font=f_body, fill=(40, 40, 40))
            hy += 13
        # source + chip on their own line, below body
        sy = y0 + 214
        draw.text((x, sy), src, font=f_src, fill=GRAY)
        chip(draw, x + 92, sy, kind, kind)
    draw.line([8, 478, 1016, 478], fill=RULE, width=1)


def draw_cards(draw):
    """10 cards, 2 rows x 5, y 478..644."""
    cards = [
        ("BESSENT DEMANDS NVIDIA ANSWERS", "Treasury presses chipmaker over China sales.", "REUTERS", "REPORTED"),
        ("FBI PROBES NCIC POLICE-DATABASE HACK", "Breach of law-enforcement records under review.", "AP", "REPORTED"),
        ("TRUMP: IRAN STRIKES MAY RESUME IN NEW YEAR", "President warns of renewed action if talks fail.", "AP", "REPORTED"),
        ("NASDAQ FUTURES +3% IN HOLIDAY WEEK", "Tech leads a short-week rally into Thanksgiving.", "BLOOMBERG", "REPORTED"),
        ("SKUBAL SIGNS $450M METS DEAL", "Two-time Cy Young winner, nine-year deal.", "ESPN", "REPORTED"),
        ("TOM JACKSON DIES AT 75", "Former linebacker and broadcaster remembered.", "NFL", "REPORTED"),
        ("STATES SUE SPACEX OVER AI SAFETY CLAIMS", "Attorneys general challenge marketing of AI tools.", "REUTERS", "REPORTED"),
        ("ANTHROPIC IPO AT $107.3B", "Raised at $83 a share; debut close $97.17.", "BLOOMBERG", "REPORTED"),
        ("POLAND: 3 RUSSIAN MISSILES CROSSED AIRSPACE", "Warsaw says Kh-101s entered its skies.", "POLISH GOVT", "CLAIM"),
        ("INTEL WARNS OF RUSSIAN NUCLEAR SATELLITE", "US agencies flag orbital weapon concerns.", "US INTEL", "CLAIM"),
    ]
    x0, y0 = 8, 482
    cw, ch = 200, 80
    f_head = font(F_SANSB, 10)
    f_body = font(F_SANS, 9)
    f_src = font(F_SANSB, 7)
    for i, (head, body, src, kind) in enumerate(cards):
        r, c = divmod(i, 5)
        x = x0 + c * (cw + 2)
        y = y0 + r * (ch + 4)
        draw.rectangle([x, y, x + cw, y + ch], outline=RULE, width=1)
        hy = y + 5
        for ln in wrap(draw, head, f_head, cw - 10)[:2]:
            draw.text((x + 5, hy), ln, font=f_head, fill=INK)
            hy += 12
        for ln in wrap(draw, body, f_body, cw - 10)[:2]:
            draw.text((x + 5, hy), ln, font=f_body, fill=(40, 40, 40))
            hy += 11
        # source + chip on their own bottom line
        sy = y + ch - 15
        draw.text((x + 5, sy), src, font=f_src, fill=GRAY)
        chip(draw, x + 62, sy, kind, kind)


def draw_map(draw):
    """World map + numbered pins + legend, x 8..512, y 650..880."""
    x0, y0, w, h = 8, 650, 504, 152
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=BLUE_BG, outline=INK, width=1)
    draw.text((x0 + 8, y0 + 4), "WHERE IT HAPPENED", font=font(F_SANSB, 10), fill=NAVY)
    # rough continent blobs
    draw.polygon([(x0 + 30, y0 + 60), (x0 + 120, y0 + 40), (x0 + 150, y0 + 70),
                  (x0 + 120, y0 + 105), (x0 + 60, y0 + 110), (x0 + 28, y0 + 85)], fill=LAND)
    draw.polygon([(x0 + 160, y0 + 45), (x0 + 330, y0 + 35), (x0 + 380, y0 + 60),
                  (x0 + 350, y0 + 105), (x0 + 250, y0 + 115), (x0 + 170, y0 + 90)], fill=LAND)
    draw.polygon([(x0 + 390, y0 + 45), (x0 + 480, y0 + 55), (x0 + 470, y0 + 120),
                  (x0 + 420, y0 + 135), (x0 + 395, y0 + 90)], fill=LAND)
    draw.polygon([(x0 + 200, y0 + 110), (x0 + 260, y0 + 108), (x0 + 250, y0 + 140),
                  (x0 + 210, y0 + 138)], fill=LAND)
    pins = [(1, 400, 60), (2, 95, 95), (3, 60, 62), (4, 320, 62), (5, 345, 78),
            (6, 235, 52), (7, 215, 45), (8, 285, 48), (9, 265, 62), (10, 250, 72),
            (11, 275, 78), (12, 245, 118), (13, 255, 128)]
    f_pin = font(F_SANSB, 9)
    for n, px, py in pins:
        cx, cy = x0 + px, y0 + py
        draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=RED, outline=(255, 255, 255), width=1)
        draw.text((cx, cy - 6), str(n), font=f_pin, fill=(255, 255, 255), anchor="ma")
    # legend: 13 items, 3 columns x 5 rows
    legend = ["1 SEOUL", "2 BRIDGETOWN", "3 WASHINGTON", "4 BEIJING", "5 NEW DELHI",
              "6 PARIS", "7 MANCHESTER", "8 KYIV", "9 ANTALYA", "10 GAZA",
              "11 BEIRUT", "12 KHARTOUM", "13 KINSHASA"]
    f_leg = font(F_SANS, 9)
    ly = y0 + h + 6
    for i, item in enumerate(legend):
        c, r = divmod(i, 5)
        draw.text((x0 + 4 + c * 168, ly + r * 14), item, font=f_leg, fill=INK)
    return ly + 5 * 14 + 4


def draw_also(draw):
    """ALSO list, x 520..1016, y 650..880."""
    x0, y0, w = 520, 650, 496
    draw.text((x0, y0 + 2), "ALSO ON MONDAY", font=font(F_SANSB, 11), fill=INK)
    draw.line([x0, y0 + 20, x0 + w, y0 + 20], fill=INK, width=1)
    items = [
        "Paris: 100+ nations back 2% billionaire tax",
        "Manchester: 12,000 cleared after substance scare",
        "Zelenskyy: 165 Russian missiles in a week",
        "COP31: the day after — 194 nations reject Antalya pact",
        "Israel unity talks resume",
        "Gaza: two killed in Israeli strike",
        "West Bank settler attacks continue",
        "Iran war: no deal in sight",
        "Lebanon seizes 264 kg of explosives",
        "Bahrain Sat: Iranian strike hits plant, 2 hurt",
        "Benghazi: UN demands probe of port attacks [CLAIM]",
        "Sudan: air defences down drones over Khartoum [CLAIM]",
        "DRC: fighting traps Ebola teams (11,762 cases)",
        "Bangladesh: Hasina jailed if she returns",
        "Seoul minister quits over AI exam chaos",
        "SK Telecom -7.3%",
        "China eases margin rules, cuts to 80%",
        "Seoul readies 10T-won stabilisation fund",
    ]
    f = font(F_SANS, 10)
    y = y0 + 26
    for it in items:
        draw.text((x0, y), fit(draw, "• " + it, f, w), font=f, fill=INK)
        y += 11


def draw_datecheck(draw):
    """Red DATE CHECK box, y 886..972."""
    x0, y0, w, h = 8, 886, 1008, 86
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(252, 235, 235),
                   outline=DARKRED, width=2)
    draw.text((x0 + 10, y0 + 5), "DATE CHECK — LEFT OUT: NOT 23 NOVEMBER",
              font=font(F_SANSB, 11), fill=DARKRED)
    left = ["Democrats reach 258 (22 Nov)", "Sparta II fire (22 Nov)",
            "El Chapo Isidro captured (22 Nov)", "EU–Indonesia pact (21 Nov)",
            "Nigeria boat (21 Nov)", "ICJ Myanmar ruling (19 Nov)"]
    f = font(F_SANS, 10)
    y = y0 + 24
    for i, it in enumerate(left):
        c, r = divmod(i, 3)
        draw.text((x0 + 10 + c * 330, y + r * 14), "✕ " + it, font=f, fill=DARKRED)
    draw.text((x0 + 10, y0 + 66), "NOT YET: Dymer search continues (14 missing)  ·  4 House races uncalled  ·  COP32 venue not set  ·  WHO evacuating trapped Ebola staff",
              font=f, fill=DARKRED)


def draw_footer(draw):
    """Footer, y 978..1018."""
    draw.line([8, 978, 1016, 978], fill=INK, width=1)
    f = font(F_SANS, 9)
    draw.text((8, 984), "SOURCES: YONHAP · UN NEWS · LOWY INSTITUTE · REUTERS · AP · BLOOMBERG · ESPN · NFL",
              font=f, fill=GRAY)
    draw.text((8, 998), "LEGEND:  REPORTED = confirmed by wires   |   CLAIM = one side's claim, not independently confirmed",
              font=f, fill=GRAY)
    draw.text((1016, 998), "THE WORLD TODAY · 23 NOV 2026", font=f, fill=GRAY, anchor="ra")


def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    draw_numbers(draw)
    draw_masthead(draw)
    draw_region_bar(draw)
    draw_heroes(draw)
    draw_cards(draw)
    draw_map(draw)
    draw_also(draw)
    draw_datecheck(draw)
    draw_footer(draw)
    img.save("entry.png", optimize=True)


if __name__ == "__main__":
    main()
