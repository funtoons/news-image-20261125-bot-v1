#!/usr/bin/env python3
"""THE DAILY GLOBE - one-page newspaper for Wednesday 25 November 2026.

Draws a 1024x1024 newspaper front page summarising the day's world news.
Pure Python standard library only: no Pillow, no network, no randomness,
no timestamps. Two runs write byte-identical PNG files.

Usage: python3 -P -s main.py [output-path]
Default output: /output/entry.png
"""

import os
import struct
import sys
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- font
# 5x7 bitmap font. Each glyph is 7 rows; each row is a 5-bit value
# (bit 4 = leftmost pixel). Written from scratch for this program.
FONT = {
    ' ': (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00),
    '!': (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
    '"': (0x0A, 0x0A, 0x0A, 0x00, 0x00, 0x00, 0x00),
    '#': (0x0A, 0x0A, 0x1F, 0x0A, 0x1F, 0x0A, 0x0A),
    '$': (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    '%': (0x18, 0x19, 0x02, 0x04, 0x08, 0x13, 0x03),
    '&': (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "'": (0x04, 0x04, 0x08, 0x00, 0x00, 0x00, 0x00),
    '(': (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ')': (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    '*': (0x00, 0x04, 0x15, 0x0E, 0x15, 0x04, 0x00),
    '+': (0x00, 0x04, 0x04, 0x1F, 0x04, 0x04, 0x00),
    ',': (0x00, 0x00, 0x00, 0x00, 0x0C, 0x04, 0x08),
    '-': (0x00, 0x00, 0x00, 0x1F, 0x00, 0x00, 0x00),
    '.': (0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C),
    '/': (0x01, 0x02, 0x02, 0x04, 0x08, 0x10, 0x10),
    '0': (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    '1': (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    '2': (0x0E, 0x11, 0x01, 0x02, 0x04, 0x08, 0x1F),
    '3': (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    '4': (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    '5': (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    '6': (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    '7': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    '8': (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    '9': (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    ':': (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x0C, 0x00),
    ';': (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x04, 0x08),
    '<': (0x02, 0x04, 0x08, 0x10, 0x08, 0x04, 0x02),
    '=': (0x00, 0x00, 0x1F, 0x00, 0x1F, 0x00, 0x00),
    '>': (0x08, 0x04, 0x02, 0x01, 0x02, 0x04, 0x08),
    '?': (0x0E, 0x11, 0x01, 0x02, 0x04, 0x00, 0x04),
    '@': (0x0E, 0x11, 0x01, 0x0D, 0x15, 0x15, 0x0E),
    'A': (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'B': (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    'C': (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    'D': (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    'E': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    'F': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    'G': (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    'H': (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'I': (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    'J': (0x01, 0x01, 0x01, 0x01, 0x01, 0x11, 0x0E),
    'K': (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    'L': (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    'M': (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    'N': (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    'O': (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'P': (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    'Q': (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    'R': (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    'S': (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    'T': (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    'U': (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'V': (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    'W': (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    'X': (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    'Y': (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    'Z': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    '[': (0x0E, 0x08, 0x08, 0x08, 0x08, 0x08, 0x0E),
    '\\': (0x10, 0x08, 0x08, 0x04, 0x02, 0x02, 0x01),
    ']': (0x0E, 0x02, 0x02, 0x02, 0x02, 0x02, 0x0E),
    '^': (0x04, 0x0A, 0x11, 0x00, 0x00, 0x00, 0x00),
    '_': (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1F),
    '`': (0x04, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00),
    'a': (0x00, 0x00, 0x0E, 0x01, 0x0F, 0x11, 0x0F),
    'b': (0x10, 0x10, 0x1E, 0x11, 0x11, 0x11, 0x1E),
    'c': (0x00, 0x00, 0x0E, 0x11, 0x10, 0x11, 0x0E),
    'd': (0x01, 0x01, 0x0F, 0x11, 0x11, 0x11, 0x0F),
    'e': (0x00, 0x00, 0x0E, 0x11, 0x1F, 0x10, 0x0E),
    'f': (0x06, 0x08, 0x1E, 0x08, 0x08, 0x08, 0x08),
    'g': (0x00, 0x0F, 0x11, 0x11, 0x0F, 0x01, 0x0E),
    'h': (0x10, 0x10, 0x1E, 0x11, 0x11, 0x11, 0x11),
    'i': (0x04, 0x00, 0x0C, 0x04, 0x04, 0x04, 0x0E),
    'j': (0x02, 0x00, 0x06, 0x02, 0x02, 0x12, 0x0C),
    'k': (0x10, 0x10, 0x12, 0x14, 0x18, 0x14, 0x12),
    'l': (0x0C, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    'm': (0x00, 0x00, 0x1A, 0x15, 0x15, 0x15, 0x15),
    'n': (0x00, 0x00, 0x1E, 0x11, 0x11, 0x11, 0x11),
    'o': (0x00, 0x00, 0x0E, 0x11, 0x11, 0x11, 0x0E),
    'p': (0x00, 0x00, 0x1E, 0x11, 0x11, 0x1E, 0x10),
    'q': (0x00, 0x00, 0x0F, 0x11, 0x11, 0x0F, 0x01),
    'r': (0x00, 0x00, 0x16, 0x19, 0x10, 0x10, 0x10),
    's': (0x00, 0x00, 0x0F, 0x10, 0x0E, 0x01, 0x1E),
    't': (0x04, 0x04, 0x1F, 0x04, 0x04, 0x05, 0x06),
    'u': (0x00, 0x00, 0x11, 0x11, 0x11, 0x13, 0x0D),
    'v': (0x00, 0x00, 0x11, 0x11, 0x11, 0x0A, 0x04),
    'w': (0x00, 0x00, 0x11, 0x15, 0x15, 0x15, 0x0A),
    'x': (0x00, 0x00, 0x11, 0x0A, 0x04, 0x0A, 0x11),
    'y': (0x00, 0x00, 0x11, 0x11, 0x0F, 0x01, 0x0E),
    'z': (0x00, 0x00, 0x1F, 0x02, 0x04, 0x08, 0x1F),
    '{': (0x06, 0x08, 0x08, 0x1C, 0x08, 0x08, 0x06),
    '|': (0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    '}': (0x0C, 0x02, 0x02, 0x07, 0x02, 0x02, 0x0C),
    '~': (0x00, 0x00, 0x00, 0x0B, 0x16, 0x00, 0x00),
    '°': (0x0E, 0x11, 0x11, 0x0E, 0x00, 0x00, 0x00),
}

# Normalise characters we do not have glyphs for.
NORMALISE = {
    '—': '-', '–': '-', '·': '.', '’': "'", '‘': "'",
    '“': '"', '”': '"', '…': '.', '×': 'x', '€': 'E', '£': 'L',
}

# ---------------------------------------------------------------- colours
PAPER = (253, 251, 244)
INK = (17, 17, 17)
RED = (163, 22, 33)
GREY = (232, 230, 222)
MIDGREY = (120, 118, 110)
DARKGREY = (70, 68, 62)
BLUE = (28, 58, 96)


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.pix = bytearray(w * h * 3)
        r, g, b = bg
        for i in range(0, len(self.pix), 3):
            self.pix[i] = r
            self.pix[i + 1] = g
            self.pix[i + 2] = b

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.pix[i], self.pix[i + 1], self.pix[i + 2] = color

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        r, g, b = color
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.pix[i] = r
                self.pix[i + 1] = g
                self.pix[i + 2] = b

    def hline(self, x, y, w, color, thick=1):
        self.fill_rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.fill_rect(x, y, thick, h, color)

    def rect(self, x, y, w, h, color, thick=1):
        self.hline(x, y, w, color, thick)
        self.hline(x, y + h - thick, w, color, thick)
        self.vline(x, y, h, color, thick)
        self.vline(x + w - thick, y, h, color, thick)

    def disc(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                    self.set(xx, yy, color)

    def ring(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy)
                if (r - 1) * (r - 1) <= d <= r * r:
                    self.set(xx, yy, color)

    # ---- text ----
    def text_width(self, s, scale):
        s = ''.join(NORMALISE.get(c, c) for c in s)
        return len(s) * 6 * scale - scale if s else 0

    def draw_text(self, x, y, s, scale, color):
        s = ''.join(NORMALISE.get(c, c) for c in s)
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT['?'])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits & (1 << (4 - col)):
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       scale, scale, color)
            cx += 6 * scale
        return cx

    def draw_text_centered(self, cx, y, s, scale, color):
        w = self.text_width(s, scale)
        return self.draw_text(cx - w // 2, y, s, scale, color)

    def wrap(self, s, max_width, scale):
        """Word-wrap to a list of lines, each at most max_width px wide."""
        words = s.split(' ')
        lines = []
        cur = ''
        for word in words:
            trial = (cur + ' ' + word).strip() if cur else word
            if self.text_width(trial, scale) <= max_width:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines


# ---------------------------------------------------------------- png
def write_png(canvas, path):
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)  # filter: none
        start = y * stride
        raw += canvas.pix[start:start + stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(ctype, data):
        out = struct.pack('>I', len(data)) + ctype + data
        out += struct.pack('>I', zlib.crc32(ctype + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack('>IIBBBBB', canvas.w, canvas.h, 8, 2, 0, 0, 0)
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', ihdr)
    png += chunk(b'IDAT', comp)
    png += chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(png)
    return len(png)


# ---------------------------------------------------------------- data
# Every story below was verified on 25 November 2026 against at least two
# independent outlets whose publication dates agree on 25 Nov 2026, or is
# an event scheduled for that day (marked DUE / TONIGHT). Stories from
# other days appear ONLY in the DATE CHECK box.

# (number, region, headline, body, sources, status)
FEATURES = [
    (1, 'ASIA',
     'SHENZHOU-24 LIFTS OFF WITH FIRST FOREIGN ASTRONAUT TO TIANGONG',
     "A Long March 2F lifted off from Jiuquan at 00:18 UTC with Tang "
     'Hongbo, Wu Yi and Muhammad Zeeshan Ali - the first Pakistani in '
     'orbit and the first foreign astronaut at Tiangong.',
     'REUTERS + XINHUA', 'CONFIRMED'),
    (2, 'OCEANIA',
     'AUSTRALIA SIGNS SOLOMON ISLANDS TREATY',
     "Albanese and Solomon Islands PM Matthew Wale signed a treaty in "
     "Canberra making Australia the islands' 'security partner of choice'. "
     "Media say the Solomons' China pact is scrapped.",
     'AAP + REUTERS', 'CONFIRMED'),
    (3, 'OCEANIA',
     'SENATE PASSES DIGITAL DUTY OF CARE',
     "Australia's Senate passed the Online Safety Amendment Bill, forcing "
     'platforms to take reasonable care against harm. Fines reach 5% of '
     'global revenue or at least A$109m; users can sue.',
     'ACCAN + THE SQUIZ', 'CONFIRMED'),
    (4, 'ASIA',
     'KOSPI PLUNGES, SIDECAR TRIPS',
     "South Korea's Kospi sank about 4.6% to 4,777 as chip stocks crashed - "
     'Samsung down 6.7%, SK hynix 6.6% - triggering a sell-side sidecar at '
     '09:08 KST.',
     'KOREA JOONGANG DAILY + AJU PRESS', 'CONFIRMED'),
    (5, 'ASIA',
     'NIKKEI SLIDES AFTER US TECH ROUT',
     "Japan's Nikkei fell 2.6% to 57,152 in morning trade, tracking "
     "Wall Street's tech selloff - Nvidia had plunged 5.9% on Tuesday. "
     'Advantest led losers, down 12%.',
     'REUTERS + DOW JONES', 'CONFIRMED'),
    (6, 'ASIA',
     'M5.1 QUAKE SHAKES ANTIQUE',
     'A magnitude 5.1 earthquake struck 14 km southeast of Valderrama, '
     'Antique, at 07:29 local time, 10 km deep. Intensity V was felt in '
     'Valderrama; aftershocks and damage were expected, PHIVOLCS said.',
     'PHIVOLCS + STRATA NEWS', 'CONFIRMED'),
    (7, 'OCEANIA',
     'M5.9 QUAKE NEAR ANTARCTICA',
     'A magnitude 5.9 earthquake struck the remote Balleny Islands region '
     'at 01:38 UTC, 10 km deep at 63.2S 171.1E. No tsunami warning was '
     'issued and no damage was reported.',
     'USGS + EMSC', 'CONFIRMED'),
    (8, 'AFRICA',
     'PHALA PHALA RULING DUE TODAY',
     "South Africa's Western Cape High Court is expected to rule today on "
     "President Ramaphosa's bid to scrap the 2022 Section 89 panel report "
     'over the $580,000 Phala Phala farm theft.',
     'OPERA NEWS + CAPE TOWN ETC', 'DUE TODAY'),
    (9, 'AMERICAS',
     'PERU CUTS 2026 GROWTH FORECAST',
     "Peru's economy ministry cut its 2026 growth forecast to 3.1% and "
     'raised its 2027 fiscal deficit projection to 2.0% of GDP, from 1.4%, '
     'while trimming the 2026 deficit outlook to 1.2%.',
     'REUTERS + DEVDISCOURSE', 'CONFIRMED'),
    (10, 'GLOBAL',
     'UN MARKS DAY AGAINST VIOLENCE TOWARD WOMEN',
     'The UN marks the International Day for the Elimination of Violence '
     'against Women, opening 16 Days of Activism. UN Women and UNODC '
     'release new femicide data; orange flags fly at UN headquarters in '
     'New York.',
     'UN WOMEN + UNODC', 'OFFICIAL'),
]

# (number, lead, text, sources)
ALSO_ON = [
    (11, 'EU-WESTERN BALKANS SUMMIT',
     'Costa and von der Leyen host six Balkan leaders in Brussels.',
     'EU INSIDER + EU COUNCIL'),
    (12, 'CHAMPIONS LEAGUE TONIGHT',
     'Matchday 5: Sabah v Barcelona, Slavia v Villarreal at 17:45 GMT, '
     'seven ties at 20:00.',
     'UEFA + NBC'),
    (13, 'CHESS: GAME 2 TODAY',
     'Gukesh, with White, faces Sindarov in Geneva at 15:00 CET after '
     'Game 1 was drawn.',
     'WORLD CHESS + CHESS.COM'),
    (14, 'HERA TO UNVEIL DIMORPHOS CLOSE-UPS',
     'ESA livestreams the first close-up images of Dimorphos at 19:45 CET.',
     'ESA + EARTHSKY'),
    (15, 'RFE/RL BACK ON SHORTWAVE',
     'New educational radio for Afghan girls barred from school returns '
     'to shortwave.',
     'RFE/RL'),
    (16, 'NIKKEI POLL: 65,000 BY JUNE 2027',
     'Reuters poll of 22 strategists sees Nikkei at 65,000 by June 2027.',
     'REUTERS'),
    (17, 'US GDP AND PCE DUE 13:30 UTC',
     'Second estimate of Q3 GDP and October PCE land at 08:30 ET.',
     'FED + EXENT'),
    (18, 'FED BEIGE BOOK DUE 19:00 UTC',
     "The Fed's Beige Book is released at 14:00 ET; markets shut Thursday.",
     'FEDERAL RESERVE'),
    (19, 'AIRTASKER REAFFIRMS FY27 GUIDANCE',
     'Australian marketplace Airtasker reaffirmed full-year 2027 guidance.',
     'REUTERS'),
    (20, 'GOLD 3,564, OIL 81.62 THIS MORNING',
     'Spot gold near $3,564 an ounce in early Asia trade; WTI near $81.62.',
     'KUCOIN + FXSTREET'),
    (21, 'AUSTRALIA CPI JUMPS TO 4.9%',
     'October inflation rose to 4.9% from 4.3%; trimmed mean 3.8%. '
     'Perth 5.5%.',
     'ABS + FXSTREET'),
    (22, 'US REAFFIRMS ALLIANCE AFTER SEOUL RESHUFFLE',
     'Washington backed close cooperation after Lee replaced top officials.',
     'AJU PRESS + SCMP'),
    (23, 'SEOUL JUSTICE NOMINEE DODGES QUESTION',
     'Lee Yong-cheol refused to rule out dropping charges against '
     'President Lee.',
     'KOREA JOONGANG + YONHAP'),
]

# (big number, label)
NUMBERS = [
    ('00:18', 'SHENZHOU-24 LAUNCH'),
    ('5.9', 'BALLENY QUAKE MAGNITUDE'),
    ('-4.6%', "KOSPI'S DAY IN SEOUL"),
    ('4.9%', 'AUSTRALIA CPI, OCTOBER'),
    ('3', 'ASTRONAUTS ABOARD'),
    ('65,000', 'NIKKEI TARGET, JUNE 2027'),
]

# (utc time, event) for the time rail
RAIL = [
    ('00:08', 'KOSPI SIDECAR'),
    ('00:18', 'SHENZHOU-24 LAUNCH'),
    ('00:20', 'SOLOMON TREATY'),
    ('00:30', 'AU CPI'),
    ('~01:36', 'DUTY OF CARE'),
    ('01:38', 'BALLENY QUAKE'),
    ('07:29', 'ANTIQUE QUAKE (LOCAL)'),
    ('13:30', 'US GDP + PCE'),
    ('14:00', 'CHESS GAME 2'),
    ('17:45', 'UCL EARLY KICK-OFFS'),
    ('18:45', 'HERA REVEAL'),
    ('19:00', 'BEIGE BOOK'),
    ('20:00', 'UCL LATE KICK-OFFS'),
]

DATE_CHECK = (
    'CIA/ODNI systems hacked (24 Nov) - Huawei guilty on 10 of 12 counts '
    '(24 Nov) - Houthis hit Riyadh tower, 11 hurt (24 Nov) - Hasina plans '
    'Dec 16 return (24 Nov) - Huckabee doubts Israel aid cut (24 Nov) - '
    'England level T20 series (24 Nov) - BJP-SAD alliance returns (24 Nov) '
    '- Nepal M5.3 quake (24 Nov) - Gaza toll claim 6,405 (24 Nov) - Hormuz: '
    '4th tanker mined (24 Nov) - Trump pardons turkeys (24 Nov) - Giuliani '
    'gets Medal of Freedom (24 Nov) - Sudan: 1,850 killed in N. Darfur '
    '(23 Nov) - 700,000 Russian soldiers killed, analysis (23 Nov) - '
    "Denmark 'ghetto law' upheld (23 Nov) - Kyiv bridges hit (20 Nov) - "
    'Araqchi: nuclear doctrine unchanged (21 Nov)')

REGION_COUNTS = [('ASIA', 8), ('OCEANIA', 5), ('AMERICAS', 3),
                 ('EUROPE', 3), ('GLOBAL', 3), ('AFRICA', 1)]

# ---------------------------------------------------------------- map
# Stylised dotted world map. 96 columns (lon -180..180) x 25 rows
# (lat 84..-66, 6 deg per row). Each row lists land intervals as
# (first_col, last_col) inclusive, drawn from a world atlas outline.
MAP_ROWS = [
    [(5, 15), (33, 41), (54, 56), (63, 67), (70, 74)],
    [(3, 16), (33, 40), (48, 52), (58, 95)],
    [(2, 18), (33, 39), (47, 52), (55, 95)],
    [(2, 20), (34, 38), (46, 53), (55, 95)],
    [(3, 22), (36, 38), (44, 46), (47, 54), (55, 95)],
    [(4, 26), (44, 47), (48, 56), (57, 95)],
    [(5, 30), (44, 48), (49, 58), (59, 95)],
    [(6, 31), (44, 49), (50, 60), (61, 95)],
    [(7, 30), (44, 47), (50, 55), (59, 63), (64, 95)],
    [(8, 28), (60, 66), (67, 80), (83, 86)],
    [(9, 26), (61, 64), (68, 78)],
    [(10, 24), (62, 64), (70, 80)],
    [(12, 22), (27, 33), (72, 82)],
    [(28, 36), (74, 84)],
    [(28, 37), (76, 85)],
    [(29, 38), (80, 88)],
    [(30, 38), (78, 89)],
    [(30, 37), (79, 88)],
    [(31, 36), (79, 87), (92, 94)],
    [(32, 35), (80, 86), (92, 94)],
    [(32, 34), (81, 84), (87, 88), (93, 94)],
    [(32, 33), (93, 94)],
    [(32, 33)],
    [(32, 33)],
    [(93, 94)],
]
MAP_COLS = 96
MAP_LAT_TOP = 84.0
MAP_LAT_BOT = -66.0

# (story number, latitude, longitude)
PINS = [
    (1, 40.96, 100.29),    # Jiuquan
    (2, -35.28, 149.13),   # Canberra
    (3, -35.28, 149.13),   # Canberra
    (4, 37.57, 126.98),    # Seoul
    (5, 35.68, 139.69),    # Tokyo
    (6, 10.89, 122.20),    # Antique
    (7, -63.23, 171.05),   # Balleny Islands
    (8, -33.92, 18.42),    # Cape Town
    (9, -12.05, -77.04),   # Lima
    (10, 40.71, -74.01),   # New York
    (11, 50.85, 4.35),     # Brussels
    (12, 46.37, 6.24),     # Nyon (UEFA HQ)
    (13, 46.20, 6.14),     # Geneva
    (14, 49.87, 8.65),     # Darmstadt (ESA ESOC)
    (15, 34.53, 69.17),    # Kabul
    (16, 35.68, 139.69),   # Tokyo
    (17, 38.90, -77.04),   # Washington DC
    (18, 38.90, -77.04),   # Washington DC
    (19, -33.87, 151.21),  # Sydney
    (21, -35.28, 149.13),  # Canberra
    (22, 37.57, 126.98),   # Seoul
    (23, 37.57, 126.98),   # Seoul
]


# ---------------------------------------------------------------- layout
MARGIN = 14
CW = W - 2 * MARGIN  # 996


def draw_masthead(c):
    c.hline(MARGIN, 8, CW, INK, 2)
    c.hline(MARGIN, 12, CW, INK, 1)
    c.draw_text(MARGIN, 20, 'EST. 2026', 1, DARKGREY)
    s = 'WEDNESDAY EDITION'
    c.draw_text(W - MARGIN - c.text_width(s, 1), 20, s, 1, DARKGREY)
    c.draw_text_centered(W // 2, 18, 'THE DAILY GLOBE', 4, INK)
    c.draw_text_centered(W // 2, 52, 'WEDNESDAY 25 NOVEMBER 2026', 3, RED)
    c.draw_text_centered(
        W // 2, 78,
        'ONE PAGE - THE WHOLE DAY - 23 STORIES, ALL VERIFIED FOR '
        'WEDNESDAY 25 NOVEMBER 2026', 1, DARKGREY)
    c.hline(MARGIN, 90, CW, INK, 2)


def draw_region_tabs(c, y):
    labels = ['%s %d' % (name, n) for name, n in REGION_COUNTS]
    labels.append('23 STORIES')
    box_w = 140
    gap = 3
    x = MARGIN
    for i, lab in enumerate(labels):
        col = RED if i == len(labels) - 1 else INK
        c.rect(x, y, box_w, 20, col, 1)
        c.draw_text_centered(x + box_w // 2, y + 7, lab, 1, col)
        x += box_w + gap
    return y + 20


def draw_numbers(c, y):
    box_w = 163
    gap = 4
    x = MARGIN
    for big, lab in NUMBERS:
        c.fill_rect(x, y, box_w, 36, GREY)
        c.rect(x, y, box_w, 36, INK, 1)
        c.draw_text_centered(x + box_w // 2, y + 3, big, 2, RED)
        lines = c.wrap(lab, box_w - 8, 1)
        ly = y + 21
        for ln in lines[:2]:
            c.draw_text_centered(x + box_w // 2, ly, ln, 1, INK)
            ly += 8
        x += box_w + gap
    return y + 36


def draw_feature(c, x, y, w, h, feat):
    num, region, head, body, src, status = feat
    c.rect(x, y, w, h, INK, 1)
    c.fill_rect(x + 2, y + 2, 30, 30, RED)
    c.draw_text_centered(x + 17, y + 11, str(num), 2, PAPER)
    tx = x + 40
    tw = w - 48
    c.draw_text(tx, y + 3, region, 1, RED)
    lines = c.wrap(head, tw, 2)
    hy = y + 13
    for ln in lines[:2]:
        c.draw_text(tx, hy, ln, 2, INK)
        hy += 14
    by = y + 13 + 2 * 14 + 4
    blines = c.wrap(body, tw, 1)
    for ln in blines[:4]:
        c.draw_text(tx, by, ln, 1, INK)
        by += 8
    c.draw_text(tx, y + h - 11, '%s - 25 NOV - %s' % (src, status), 1, DARKGREY)


def draw_features(c, y):
    col_w = 491
    row_h = 92
    step = 94
    for i, feat in enumerate(FEATURES):
        col = i % 2
        row = i // 2
        x = MARGIN + col * (col_w + 14)
        draw_feature(c, x, y + row * step, col_w, row_h, feat)
    return y + 4 * step + row_h


def draw_also_on(c, y):
    c.hline(MARGIN, y, CW, INK, 2)
    c.draw_text(MARGIN, y + 5, 'ALSO ON - THE REST OF THE DAY', 2, RED)
    c.draw_text(W - MARGIN - c.text_width('NUMBERED 11-23', 1),
                y + 8, 'NUMBERED 11-23', 1, DARKGREY)
    top = y + 24
    col_w = 491
    left = ALSO_ON[:7]
    right = ALSO_ON[7:]

    def column(items, x):
        yy = top
        for num, lead, text, src in items:
            full = '%d. %s - %s (%s)' % (num, lead, text, src)
            lines = c.wrap(full, col_w - 4, 1)
            for ln in lines[:3]:
                c.draw_text(x, yy, ln, 1, INK)
                yy += 8
            yy += 1
        return yy

    y1 = column(left, MARGIN)
    y2 = column(right, MARGIN + col_w + 14)
    return max(y1, y2)


def draw_rail(c, y):
    c.hline(MARGIN, y, CW, INK, 1)
    c.draw_text(MARGIN, y + 4, 'THE DAY IN UTC', 1, RED)
    parts = ['%s %s' % (t, ev) for t, ev in RAIL]
    text = '  |  '.join(parts)
    lines = c.wrap(text, CW, 1)
    yy = y + 15
    for ln in lines[:3]:
        c.draw_text(MARGIN, yy, ln, 1, INK)
        yy += 8
    return yy


def draw_map(c, y, h):
    c.hline(MARGIN, y, CW, INK, 2)
    c.draw_text(MARGIN, y + 5, 'WHERE IT HAPPENED', 2, RED)
    note = 'DOTS = LAND - NUMBERED PINS MATCH THE STORIES ABOVE'
    c.draw_text(W - MARGIN - c.text_width(note, 1), y + 8, note, 1, DARKGREY)
    my = y + 22
    mh = h - 22
    # dotted land
    for r, intervals in enumerate(MAP_ROWS):
        cy = my + int((r + 0.5) * mh / len(MAP_ROWS))
        for a, b in intervals:
            for col in range(a, b + 1):
                cx = MARGIN + int((col + 0.5) * CW / MAP_COLS)
                c.fill_rect(cx - 2, cy - 1, 4, 3, BLUE)
    # pins, clustered by proximity
    pts = []
    for num, lat, lon in PINS:
        px = MARGIN + (lon + 180.0) / 360.0 * CW
        py = my + (MAP_LAT_TOP - lat) / (MAP_LAT_TOP - MAP_LAT_BOT) * mh
        px = max(MARGIN + 10, min(MARGIN + CW - 10, px))
        py = max(my + 10, min(my + mh - 10, py))
        pts.append((num, px, py))
    clusters = []
    for p in pts:
        placed = False
        for cl in clusters:
            if abs(p[1] - cl[0][1]) < 26 and abs(p[2] - cl[0][2]) < 26:
                cl.append(p)
                placed = True
                break
        if not placed:
            clusters.append([p])

    def span(cl):
        cx = sum(p[1] for p in cl) / len(cl)
        return cx - len(cl) * 9, cx + len(cl) * 9

    # merge clusters whose numbered-disc rows would overlap
    changed = True
    while changed:
        changed = False
        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                a, b = clusters[i], clusters[j]
                cy_a = sum(p[2] for p in a) / len(a)
                cy_b = sum(p[2] for p in b) / len(b)
                ax0, ax1 = span(a)
                bx0, bx1 = span(b)
                if abs(cy_a - cy_b) < 18 and ax0 < bx1 and bx0 < ax1:
                    clusters[i] = a + b
                    del clusters[j]
                    changed = True
                    break
            if changed:
                break
    for cl in clusters:
        cl = sorted(cl)
        cx = sum(p[1] for p in cl) / len(cl)
        cy = sum(p[2] for p in cl) / len(cl)
        total = len(cl) * 18
        sx = cx - total / 2 + 9
        for i, (num, _px, _py) in enumerate(cl):
            px = sx + i * 18
            c.disc(int(px), int(cy), 8, RED)
            c.ring(int(px), int(cy), 8, PAPER)
            s = str(num)
            c.draw_text(int(px) - c.text_width(s, 1) // 2, int(cy) - 3,
                        s, 1, PAPER)
    return y + h


def draw_date_check(c, y):
    c.fill_rect(MARGIN, y, CW, 62, GREY)
    c.rect(MARGIN, y, CW, 62, INK, 1)
    c.draw_text(MARGIN + 6, y + 5, 'DATE CHECK - BIG NEWS, WRONG DAY',
                1, RED)
    lines = c.wrap(DATE_CHECK, CW - 12, 1)
    yy = y + 17
    for ln in lines[:4]:
        c.draw_text(MARGIN + 6, yy, ln, 1, INK)
        yy += 9
    return y + 62


def draw_footer(c, y):
    c.draw_text_centered(
        W // 2, y,
        'SOURCES: REUTERS, AAP, XINHUA, PHIVOLCS, USGS, EMSC, ABS, UEFA, '
        'ESA, UN WOMEN, RFE/RL, KOREA JOONGANG DAILY, AJU PRESS, FEDERAL '
        'RESERVE.', 1, DARKGREY)
    c.draw_text_centered(
        W // 2, y + 10,
        'ALL STORIES FIRST PUBLISHED OR OCCURRED ON WEDNESDAY 25 NOVEMBER '
        '2026 UNLESS MARKED DUE OR TONIGHT. DRAWN ENTIRELY BY CODE - NO '
        'PHOTOGRAPHS.', 1, DARKGREY)


def render():
    c = Canvas(W, H, PAPER)
    draw_masthead(c)
    y = draw_region_tabs(c, 94)
    y = draw_numbers(c, y + 4)
    y = draw_features(c, y + 4)
    y = draw_also_on(c, y + 4)
    y = draw_rail(c, y + 4)
    y = draw_map(c, y + 4, 128)
    y = draw_date_check(c, y + 4)
    draw_footer(c, y + 6)
    return c


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else '/output/entry.png'
    parent = os.path.dirname(out)
    if parent:
        os.makedirs(parent, exist_ok=True)
    canvas = render()
    size = write_png(canvas, out)
    print('wrote %s (%d bytes, %dx%d)' % (out, size, W, H))


if __name__ == '__main__':
    main()
