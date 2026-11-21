# SPDX-License-Identifier: MIT
# The Passport Page of a Country That Isn't There.
# Draws one invented passport spread for the Republic of Vulkara
# (volcanic island nation, capital Port Ember) as a PNG at
# /output/entry.png. Pure Python 3.13 stdlib, deterministic, no network.
# Every date is fixed: issued 12 MAR 2024, all stamps after that date.

import os
import struct
import zlib

W, H = 1024, 720

# --- palette (restrained, document-like) -----------------------------------
PAPER = (247, 242, 228)
PAPER2 = (238, 231, 210)
INK = (30, 42, 74)
INK_SOFT = (74, 84, 112)
GOLD = (166, 124, 46)
RED = (138, 42, 42)
BLUE = (38, 74, 122)
GREEN = (46, 92, 66)
SKIN = (217, 165, 131)
SKIN_D = (198, 142, 106)
HAIR = (88, 42, 30)
JACKET = (52, 84, 66)
PHOTO_BG = (168, 178, 168)
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)

# --- canvas -----------------------------------------------------------------
buf = bytearray([0]) * (W * H * 3)


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i], buf[i + 1], buf[i + 2] = c


def fill_rect(x0, y0, x1, y1, c):
    x0 = max(0, x0)
    y0 = max(0, y0)
    x1 = min(W - 1, x1)
    y1 = min(H - 1, y1)
    for y in range(y0, y1 + 1):
        base = (y * W + x0) * 3
        for x in range(x0, x1 + 1):
            buf[base], buf[base + 1], buf[base + 2] = c
            base += 3


def hline(x0, x1, y, c):
    for x in range(min(x0, x1), max(x0, x1) + 1):
        px(x, y, c)


def vline(x, y0, y1, c):
    for y in range(min(y0, y1), max(y0, y1) + 1):
        px(x, y, c)


def line(x0, y0, x1, y1, c):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        px(x0, y0, c)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def fill_ellipse(cx, cy, rx, ry, c, clip=None):
    for y in range(cy - ry, cy + ry + 1):
        if y < 0 or y >= H:
            continue
        if clip is not None and not (clip[1] <= y <= clip[3]):
            continue
        t = 1.0 - ((y - cy) / ry) ** 2
        if t < 0:
            continue
        dx = int(rx * (t ** 0.5))
        for x in range(cx - dx, cx + dx + 1):
            if clip is not None and not (clip[0] <= x <= clip[2]):
                continue
            px(x, y, c)


def ellipse_outline(cx, cy, rx, ry, c):
    import math
    for deg in range(0, 360):
        a = math.radians(deg)
        px(int(cx + rx * math.cos(a)), int(cy + ry * math.sin(a)), c)


# --- 5x7 bitmap font (uppercase; lowercase maps to uppercase) ---------------
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
}


def text_width(s, scale):
    return len(s) * (6 * scale) - scale


def draw_text(x, y, s, scale, color, align="left", adv=None):
    s = s.upper()
    step = (6 * scale) if adv is None else adv
    if align == "center":
        x = x - (len(s) * step - scale) // 2
    elif align == "right":
        x = x - (len(s) * step - scale)
    cx = x
    for ch in s:
        g = FONT.get(ch, FONT[" "])
        for row in range(7):
            bits = g[row]
            for col in range(5):
                if bits[col] == "1":
                    fill_rect(cx + col * scale, y + row * scale,
                              cx + col * scale + scale - 1,
                              y + row * scale + scale - 1, color)
        cx += step
    return cx


def rot(px_, py_, cx, cy, cos_a, sin_a):
    dx, dy = px_ - cx, py_ - cy
    return (int(cx + dx * cos_a - dy * sin_a),
            int(cy + dx * sin_a + dy * cos_a))


def draw_text_rot(x, y, s, scale, color, angle_deg):
    import math
    a = math.radians(angle_deg)
    ca, sa = math.cos(a), math.sin(a)
    s = s.upper()
    cx = x
    for ch in s:
        g = FONT.get(ch, FONT[" "])
        for row in range(7):
            for col in range(5):
                if g[row][col] == "1":
                    bx, by = cx + col * scale, y + row * scale
                    for dx in range(scale):
                        for dy in range(scale):
                            rx, ry = rot(bx + dx, by + dy, x, y, ca, sa)
                            px(rx, ry, color)
        cx += 6 * scale


def stamp_rect(cx, cy, w, h, angle_deg, color, lines, scale=1):
    """Rotated rectangular stamp: double border + centred text lines."""
    import math
    a = math.radians(angle_deg)
    ca, sa = math.cos(a), math.sin(a)
    hw, hh = w // 2, h // 2
    corners = [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]
    pts = [rot(cx + dx, cy + dy, cx, cy, ca, sa) for dx, dy in corners]
    for i in range(4):
        line(pts[i][0], pts[i][1], pts[(i + 1) % 4][0], pts[(i + 1) % 4][1], color)
    iw, ih = hw - 5, hh - 5
    inner = [(-iw, -ih), (iw, -ih), (iw, ih), (-iw, ih)]
    pts2 = [rot(cx + dx, cy + dy, cx, cy, ca, sa) for dx, dy in inner]
    for i in range(4):
        line(pts2[i][0], pts2[i][1], pts2[(i + 1) % 4][0], pts2[(i + 1) % 4][1], color)
    total_h = len(lines) * (7 * scale + 4) - 4
    ly = cy - total_h // 2
    for ln in lines:
        tw = text_width(ln, scale)
        sx, sy = rot(cx - tw // 2, ly, cx, cy, ca, sa)
        draw_text_rot(sx, sy, ln, scale, color, angle_deg)
        ly += 7 * scale + 4


def stamp_oval(cx, cy, rx, ry, angle_deg, color, lines, scale=1):
    """Oval stamp: ellipse borders + rotated text lines."""
    import math
    a = math.radians(angle_deg)
    ca, sa = math.cos(a), math.sin(a)
    for deg in range(0, 360, 2):
        r = math.radians(deg)
        ox, oy = int(rx * math.cos(r)), int(ry * math.sin(r))
        rxp, ryp = rot(cx + ox, cy + oy, cx, cy, ca, sa)
        px(rxp, ryp, color)
        ox2, oy2 = int((rx - 4) * math.cos(r)), int((ry - 4) * math.sin(r))
        rxp2, ryp2 = rot(cx + ox2, cy + oy2, cx, cy, ca, sa)
        px(rxp2, ryp2, color)
    total_h = len(lines) * (7 * scale + 4) - 4
    ly = cy - total_h // 2
    for ln in lines:
        tw = text_width(ln, scale)
        sx, sy = rot(cx - tw // 2, ly, cx, cy, ca, sa)
        draw_text_rot(sx, sy, ln, scale, color, angle_deg)
        ly += 7 * scale + 4


# --- MRZ check digits (ICAO 9303) -------------------------------------------
def mrz_check(s):
    vals = {}
    for i in range(10):
        vals[str(i)] = i
    for i, ch in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        vals[ch] = 10 + i
    vals["<"] = 0
    total = 0
    for i, ch in enumerate(s):
        total += vals[ch] * (7, 3, 1)[i % 3]
    return str(total % 10)


def build_mrz():
    line1 = "P<VULVANE<<ANYA<SORREL"
    line1 = line1 + "<" * (44 - len(line1))
    doc = "VK4829173"
    dob = "880614"
    exp = "340312"
    pers = "<" * 14
    l2 = (doc + mrz_check(doc) + "VUL" + dob + mrz_check(dob) + "F"
          + exp + mrz_check(exp) + pers + mrz_check(pers))
    comp = mrz_check(l2)
    return line1, l2 + comp


# --- portrait (procedural) ---------------------------------------------------
def draw_portrait(x0, y0, x1, y1):
    fill_rect(x0, y0, x1, y1, PHOTO_BG)
    # faint guilloche bands behind the head
    for i in range(0, y1 - y0, 8):
        hline(x0, x1, y0 + i, (158, 168, 158))
    cx = (x0 + x1) // 2
    # shoulders / jacket, clipped to the photo box so nothing spills out
    fill_ellipse(cx, y1 + 18, 52, 42, JACKET, clip=(x0, y0, x1, y1))
    fill_rect(x0, y1 - 26, x1, y1, JACKET)
    # shirt collar
    fill_ellipse(cx, y1 - 22, 14, 10, WHITE)
    # neck
    fill_rect(cx - 9, y0 + 88, cx + 9, y0 + 112, SKIN_D)
    # head
    fill_ellipse(cx, y0 + 62, 34, 42, SKIN)
    # hair: auburn cap + side falls framing the face
    fill_ellipse(cx, y0 + 34, 36, 30, HAIR)
    fill_rect(cx - 36, y0 + 30, cx - 26, y0 + 92, HAIR)
    fill_rect(cx + 26, y0 + 30, cx + 36, y0 + 92, HAIR)
    fill_ellipse(cx, y0 + 44, 34, 18, HAIR)
    # face opening (skin shows through the hair cap)
    fill_ellipse(cx, y0 + 66, 27, 34, SKIN)
    # brows, eyes, nose, mouth
    hline(cx - 20, cx - 8, y0 + 58, HAIR)
    hline(cx + 8, cx + 20, y0 + 58, HAIR)
    fill_rect(cx - 17, y0 + 63, cx - 12, y0 + 67, BLACK)
    fill_rect(cx + 12, y0 + 63, cx + 17, y0 + 67, BLACK)
    vline(cx, y0 + 68, y0 + 82, SKIN_D)
    hline(cx - 2, cx + 2, y0 + 82, SKIN_D)
    hline(cx - 9, cx + 9, y0 + 92, (150, 70, 60))
    # earring: small gold dot, Vulkaran ember-gold
    px(cx - 27, y0 + 84, GOLD)
    px(cx + 27, y0 + 84, GOLD)
    # frame
    for xx in (x0, x1):
        vline(xx, y0, y1, INK)
    for yy in (y0, y1):
        hline(x0, x1, yy, INK)


def draw_emblem(cx, cy, r):
    ellipse_outline(cx, cy, r, r, GOLD)
    ellipse_outline(cx, cy, r - 3, r - 3, GOLD)
    # volcano: triangle with smoke plume and sun
    fill_ellipse(cx + 8, cy - r + 8, 5, 4, GOLD)
    line(cx - r + 8, cy + r - 8, cx, cy - r + 12, INK)
    line(cx + r - 8, cy + r - 8, cx, cy - r + 12, INK)
    hline(cx - 3, cx + 3, cy - r + 12, RED)
    # base line (sea)
    hline(cx - r + 8, cx + r - 8, cy + r - 10, BLUE)
    hline(cx - r + 12, cx + r - 12, cy + r - 7, BLUE)


# --- page --------------------------------------------------------------------
def main():
    fill_rect(0, 0, W - 1, H - 1, PAPER)
    # faint paper texture: sparse darker speckles, fixed pattern
    for y in range(0, H, 7):
        for x in range((y * 13) % 11, W, 53):
            px(x, y, PAPER2)
    # page borders and spine
    for xx in (6, 517):
        vline(xx, 6, H - 7, INK_SOFT)
    for xx in (505, 1017):
        vline(xx, 6, H - 7, INK_SOFT)
    for yy in (6, H - 7):
        hline(6, 505, yy, INK_SOFT)
        hline(517, 1017, yy, INK_SOFT)
    vline(511, 0, H - 1, INK)
    vline(512, 0, H - 1, INK)

    # ================= LEFT PAGE: DATA PAGE =================
    draw_text(256, 24, "REPUBLIC OF VULKARA", 2, INK, align="center")
    draw_text(256, 44, "PASSPORT", 3, INK, align="center")
    draw_text(256, 70, "PASSPORTO - EMBER ISLES", 1, INK_SOFT, align="center")
    draw_emblem(452, 52, 26)
    hline(28, 484, 92, GOLD)
    hline(28, 484, 94, GOLD)

    # portrait
    draw_portrait(36, 112, 154, 254)
    draw_text(95, 262, "HOLDER", 1, INK_SOFT, align="center")

    # data fields, two columns right of the portrait
    fx, fw = 172, 312
    rows = [
        ("TYPE", "P"),
        ("COUNTRY", "VUL"),
        ("PASSPORT NO.", "VK4829173"),
        ("SURNAME", "VANE"),
        ("GIVEN NAMES", "ANYA SORREL"),
        ("NATIONALITY", "VULKARAN"),
        ("DATE OF BIRTH", "14 JUN 1988"),
        ("PLACE OF BIRTH", "PORT EMBER"),
        ("SEX", "F"),
        ("DATE OF ISSUE", "12 MAR 2024"),
        ("DATE OF EXPIRY", "12 MAR 2034"),
        ("AUTHORITY", "MINISTRY OF THE"),
        ("", "INTERIOR, PORT EMBER"),
        ("LANGUAGES", "VULKARAN / ENGLISH"),
    ]
    y = 108
    for label, value in rows:
        if label:
            draw_text(fx, y, label, 1, INK_SOFT)
        draw_text(fx + 118, y, value, 1, INK)
        y += 22
        if label in ("PASSPORT NO.", "GIVEN NAMES", "PLACE OF BIRTH",
                     "DATE OF EXPIRY"):
            hline(fx, fx + fw, y - 6, PAPER2)

    # signature strip (kept inside the portrait column, clear of fields)
    draw_text(36, 424, "SIGNATURE OF HOLDER", 1, INK_SOFT)
    hline(36, 160, 438, INK)
    draw_text(36, 446, "ANYA S. VANE", 1, INK)
    # observations box: fills the lower data page like a real passport
    draw_text(220, 424, "NOTES", 1, INK_SOFT)
    hline(220, 484, 440, PAPER2)
    draw_text(220, 448, "THIS PASSPORT IS THE", 1, INK)
    draw_text(220, 462, "PROPERTY OF THE", 1, INK)
    draw_text(220, 476, "REPUBLIC OF VULKARA.", 1, INK)
    draw_text(220, 498, "IF FOUND, RETURN TO THE", 1, INK)
    draw_text(220, 512, "NEAREST VULKARAN CONSULATE.", 1, INK)
    draw_text(256, 536, "EMBER ISLES - EST. 1962", 1, INK_SOFT,
              align="center")

    # MRZ strip (44 chars at 10 px advance = 440 px, inside the page)
    fill_rect(28, 560, 484, 628, (232, 226, 208))
    hline(28, 484, 560, INK)
    hline(28, 484, 628, INK)
    l1, l2 = build_mrz()
    draw_text(36, 572, l1, 2, BLACK, adv=10)
    draw_text(36, 598, l2, 2, BLACK, adv=10)
    draw_text(256, 640, "MACHINE READABLE ZONE - DO NOT FOLD", 1, INK_SOFT,
              align="center")

    # ================= RIGHT PAGE: VISA / STAMP PAGE =================
    draw_text(768, 24, "VISAS", 3, INK, align="center")
    draw_text(768, 52, "VISA - STAMPS - ENDORSEMENTS", 1, INK_SOFT,
              align="center")
    hline(540, 996, 72, GOLD)
    hline(540, 996, 74, GOLD)

    # Stamp 1: Caldoria entry, 02 APR 2024 (oval, red)
    stamp_oval(660, 150, 92, 52, -10, RED,
               ["CALDORIA", "ENTRY", "02 APR 2024", "ALDERGATE"], 1)
    # Stamp 2: Caldoria exit, 18 APR 2024 (rect, blue)
    stamp_rect(880, 150, 150, 74, 8, BLUE,
               ["CALDORIA", "EXIT", "18 APR 2024"], 1)
    # Stamp 3: Isle of Merrow entry, 07 SEP 2024 (oval, green)
    stamp_oval(660, 300, 92, 52, 9, GREEN,
               ["ISLE OF MERROW", "ENTRY", "07 SEP 2024"], 1)
    # Stamp 4: Vulkara arrival, 22 SEP 2024 (rect, red)
    stamp_rect(880, 300, 150, 74, -7, RED,
               ["VULKARA", "ARRIVAL", "22 SEP 2024", "PORT EMBER"], 1)

    # travel history line, tying the stamps into one story
    draw_text(540, 380, "TRAVEL HISTORY", 1, INK_SOFT)
    hline(540, 996, 396, PAPER2)
    hist = [
        "02 APR 2024  DEPART PORT EMBER - ARRIVE CALDORIA",
        "18 APR 2024  DEPART CALDORIA - ARRIVE PORT EMBER",
        "07 SEP 2024  DEPART PORT EMBER - ARRIVE MERROW",
        "22 SEP 2024  DEPART MERROW - ARRIVE PORT EMBER",
    ]
    y = 404
    for htxt in hist:
        draw_text(540, y, htxt, 1, INK)
        y += 20

    # Telling detail: volcano-zone permit (the paperwork that reveals Vulkara)
    fill_rect(540, 500, 996, 640, (250, 244, 224))
    for xx in (540, 996):
        vline(xx, 500, 640, RED)
    for yy in (500, 640):
        hline(540, 996, yy, RED)
    draw_text(768, 512, "VOLCANO ZONE PERMIT", 2, RED, align="center")
    draw_text(768, 540,
              "HOLDER MAY ENTER THE ASHFALL EXCLUSION", 1, INK,
              align="center")
    draw_text(768, 556,
              "ZONE ONLY WITH A LICENSED GUIDE.", 1, INK, align="center")
    draw_text(768, 580, "FEE PAID: 40 EMBER - RECEIPT NO. 7719", 1, INK,
              align="center")
    draw_text(768, 604, "VALID WITH THIS PASSPORT - PORT EMBER", 1, INK_SOFT,
              align="center")
    draw_text(768, 622, "MINISTRY OF THE INTERIOR - EMBER ISLES", 1, INK_SOFT,
              align="center")

    # small fee stamp overlapping the permit box corner
    stamp_oval(940, 660, 52, 26, -14, RED, ["FEE PAID", "40 EMBER"], 1)

    draw_text(768, 690, "PAGE 2 OF 32 - REPUBLIC OF VULKARA", 1, INK_SOFT,
              align="center")

    # --- PNG encode ----------------------------------------------------------
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw.extend(buf[y * W * 3:(y + 1) * W * 3])
    comp = zlib.compress(bytes(raw), 9)

    def chunk(typ, data):
        c = struct.pack(">I", len(data)) + typ + data
        return c + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    os.makedirs("/output", exist_ok=True)
    with open("/output/entry.png", "wb") as f:
        f.write(png)


if __name__ == "__main__":
    main()
