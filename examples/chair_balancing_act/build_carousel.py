#!/usr/bin/env python3
"""Build a LinkedIn carousel PDF for Chair Balancing Act.

Format: 1080x1350 px (4:5 portrait) — optimized for mobile feed.
Uses reportlab for direct PDF generation. No LibreOffice dependency.
"""

import os
from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white, black
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

_DIR = os.path.dirname(os.path.abspath(__file__))

# -- Page size: 1080x1350 px at 72 dpi = 381 x 476.25 mm at 72 dpi --
# reportlab works in points (1 pt = 1/72 inch)
PW = 1080 * 72 / 150  # use 150 dpi equivalent for reasonable physical size
PH = 1350 * 72 / 150
# Actually, LinkedIn just cares about aspect ratio. Let's use mm for clean math.
PW = 190 * mm   # ~190mm wide
PH = 237.5 * mm # 4:5 ratio

# -- Colors --
DARK_BG = "#1A1A2E"
CARD_BG = "#22223A"
CARD_BG_ALT = "#1E1E34"
ACCENT_ORANGE = "#FF8C00"
ACCENT_GREEN = "#4EC978"
ACCENT_RED = "#FF4545"
ACCENT_BLUE = "#009BF5"
WHITE_HEX = "#FFFFFF"
LIGHT_GRAY = "#BBBBCC"
SOFT_WHITE = "#F0F0F5"

M = 10 * mm  # standard margin


def bg(c, color=DARK_BG):
    c.setFillColor(HexColor(color))
    c.rect(0, 0, PW, PH, fill=1, stroke=0)


def accent_strip(c, color=ACCENT_ORANGE):
    c.setFillColor(HexColor(color))
    c.rect(0, PH - 2 * mm, PW, 2 * mm, fill=1, stroke=0)


def card(c, x, y, w, h, color=CARD_BG):
    """Draw a card. y is from TOP of page (converted internally)."""
    c.setFillColor(HexColor(color))
    c.roundRect(x, PH - y - h, w, h, 3 * mm, fill=1, stroke=0)


def card_flat(c, x, y, w, h, color=CARD_BG):
    c.setFillColor(HexColor(color))
    c.rect(x, PH - y - h, w, h, fill=1, stroke=0)


def txt(c, x, y, text, size=14, color=WHITE_HEX, bold=False, align="left", max_w=None):
    """Draw text. y is from TOP of page."""
    c.setFillColor(HexColor(color))
    font = "Helvetica-Bold" if bold else "Helvetica"
    c.setFont(font, size)
    ry = PH - y - size * 0.35  # baseline
    if align == "center" and max_w:
        tw = c.stringWidth(text, font, size)
        c.drawString(x + (max_w - tw) / 2, ry, text)
    elif align == "right" and max_w:
        tw = c.stringWidth(text, font, size)
        c.drawString(x + max_w - tw, ry, text)
    else:
        c.drawString(x, ry, text)


def txt_wrap(c, x, y, text, size=11, color=WHITE_HEX, bold=False, line_h=None, max_w=None):
    """Draw wrapped text. Returns y after last line."""
    if line_h is None:
        line_h = size * 1.4
    font = "Helvetica-Bold" if bold else "Helvetica"
    c.setFillColor(HexColor(color))
    c.setFont(font, size)
    if max_w is None:
        max_w = PW - 2 * M
    words = text.split()
    lines = []
    current = ""
    for w in words:
        test = current + (" " if current else "") + w
        if c.stringWidth(test, font, size) > max_w:
            if current:
                lines.append(current)
            current = w
        else:
            current = test
    if current:
        lines.append(current)
    for line in lines:
        c.drawString(x, PH - y - size * 0.35, line)
        y += line_h
    return y


def bar(c, x, y, w, h, color):
    c.setFillColor(HexColor(color))
    c.rect(x, PH - y - h, w, h, fill=1, stroke=0)


def circle_num(c, x, y, num, color):
    r = 4 * mm
    c.setFillColor(HexColor(color))
    c.circle(x + r, PH - y - r, r, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 12)
    tw = c.stringWidth(str(num), "Helvetica-Bold", 12)
    c.drawString(x + r - tw / 2, PH - y - r - 4, str(num))


# -- Page number footer --
def footer(c, page, total):
    c.setFillColor(HexColor(LIGHT_GRAY))
    c.setFont("Helvetica", 8)
    label = f"{page}/{total}"
    tw = c.stringWidth(label, "Helvetica", 8)
    c.drawString(PW - M - tw, 4 * mm, label)


TOTAL_PAGES = 7
output = os.path.join(_DIR, "Chair_Balancing_Act_Carousel.pdf")
c = canvas.Canvas(output, pagesize=(PW, PH))

# ================================================================
# PAGE 1: Title
# ================================================================
bg(c)
accent_strip(c, ACCENT_ORANGE)

# -- Top section: title + tagline (top 40%) --
txt(c, M, 14 * mm, "Chair", size=44, color=WHITE_HEX, bold=True)
txt(c, M, 28 * mm, "Balancing Act", size=44, color=WHITE_HEX, bold=True)

bar(c, M, 38 * mm, 35 * mm, 1 * mm, ACCENT_ORANGE)

txt_wrap(c, M, 44 * mm,
         "Continuous audio escalation for tilting chairs",
         size=15, color=ACCENT_GREEN, max_w=PW - 2 * M)

txt(c, M, 56 * mm, "All legs down = silence.  Any leg lifts = rising tone.",
    size=11, color=LIGHT_GRAY)
txt(c, M, 63 * mm, "Part safety reminder, part office prank, part gift-shop impulse buy.",
    size=10, color=LIGHT_GRAY)

# -- Middle section: image (occupies ~70-200mm band) --
img_path = os.path.join(_DIR, "cBalance.png")
if os.path.exists(img_path):
    img_top_y = 75 * mm   # y from top of page where image starts
    img_max_w = PW - 2 * M
    img_max_h = 145 * mm  # max height for the image zone
    # place image at bottom-left of the zone, preserving aspect ratio
    c.drawImage(ImageReader(img_path),
                M, PH - img_top_y - img_max_h,
                width=img_max_w, height=img_max_h,
                preserveAspectRatio=True, anchor='sw', mask='auto')

# -- Bottom bar --
card_flat(c, 0, PH - 8 * mm, PW, 8 * mm, CARD_BG)
txt(c, M, PH - 5 * mm, "Product Overview  |  Concept Stage  |  2026",
    size=9, color=LIGHT_GRAY)

footer(c, 1, TOTAL_PAGES)
c.showPage()

# ================================================================
# PAGE 2: How It Works — Three Zones
# ================================================================
bg(c)
accent_strip(c, ACCENT_GREEN)

txt(c, M, 12 * mm, "How It Works", size=28, color=WHITE_HEX, bold=True)
bar(c, M, 22 * mm, 30 * mm, 0.8 * mm, ACCENT_GREEN)

zones = [
    ("Static Balance", "SILENCE", ACCENT_GREEN,
     ["All legs on the floor",
      "Device sleeps, no sound",
      "MCU in deep sleep (<1 uA)"]),
    ("Dynamic Balance", "CONTINUOUS RISING TONE", ACCENT_ORANGE,
     ["Any leg lifts off the floor",
      "Pleasant low tone begins",
      "Rises smoothly with tilt angle"]),
    ("Near Fall", "MAXIMUM ALARM", ACCENT_RED,
     ["Steep angle, near tipping",
      "Tone at peak urgency",
      "Everyone knows what's happening"]),
]

for i, (title, subtitle, color, bullets) in enumerate(zones):
    y_top = 30 * mm + i * 60 * mm
    card(c, M, y_top, PW - 2 * M, 54 * mm, CARD_BG)
    bar(c, M, y_top, PW - 2 * M, 1.5 * mm, color)
    txt(c, M + 5 * mm, y_top + 8 * mm, title, size=20, color=color, bold=True)
    txt(c, M + 5 * mm, y_top + 18 * mm, subtitle, size=10, color=LIGHT_GRAY, bold=True)
    by = y_top + 28 * mm
    for b in bullets:
        txt(c, M + 8 * mm, by, f"- {b}", size=12, color=SOFT_WHITE)
        by += 7 * mm

# Device summary
card_flat(c, M, 215 * mm, PW - 2 * M, 16 * mm, CARD_BG)
txt(c, M + 4 * mm, 218 * mm, "32mm round x 10mm  |  15g  |  CR2450 coin cell  |  Adhesive mount",
    size=10, color=LIGHT_GRAY)
txt(c, M + 4 * mm, 226 * mm, "Fixed-leg chairs only (school, dining)",
    size=10, color=LIGHT_GRAY)

footer(c, 2, TOTAL_PAGES)
c.showPage()

# ================================================================
# PAGE 3: Architecture
# ================================================================
bg(c)
accent_strip(c, ACCENT_BLUE)

txt(c, M, 12 * mm, "Architecture", size=28, color=WHITE_HEX, bold=True)
bar(c, M, 22 * mm, 30 * mm, 0.8 * mm, ACCENT_BLUE)

# Data flow
card(c, M, 28 * mm, PW - 2 * M, 22 * mm, CARD_BG)
txt(c, M + 4 * mm, 32 * mm, "Data Flow", size=11, color=ACCENT_BLUE, bold=True)
txt(c, M + 4 * mm, 40 * mm, "Accelerometer  -->  MCU  -->  Class-D Amp  -->  Piezo",
    size=13, color=WHITE_HEX, bold=True)
txt(c, M + 4 * mm, 47 * mm, "I2C + interrupt         PWM tone gen        sound out",
    size=9, color=LIGHT_GRAY)

# Subsystems
bar(c, M, 56 * mm, PW - 2 * M, 1 * mm, ACCENT_BLUE)
txt(c, M, 61 * mm, "SUBSYSTEMS", size=11, color=ACCENT_BLUE, bold=True)

subsystems = [
    ("Accelerometer (LIS2DH12)", "3-axis tilt, wake interrupt, I2C", ACCENT_GREEN),
    ("MCU (ATtiny1616)", "Filter, tone gen (PWM), calibration, sleep", ACCENT_GREEN),
    ("Class-D Amp (PAM8302)", "Amplifies MCU PWM to drive piezo", ACCENT_GREEN),
    ("Piezo Speaker (13mm)", "75-85 dB at 10cm, fits 10mm enclosure", ACCENT_GREEN),
    ("CR2450 Coin Cell", "600 mAh, months of life, user-replaceable", ACCENT_ORANGE),
    ("Button (1x tactile)", "Mode cycle + calibration + on/off", ACCENT_ORANGE),
]

for i, (name, desc, color) in enumerate(subsystems):
    y_top = 68 * mm + i * 18 * mm
    bg_c = CARD_BG if i % 2 == 0 else CARD_BG_ALT
    card(c, M, y_top, PW - 2 * M, 15 * mm, bg_c)
    txt(c, M + 4 * mm, y_top + 4 * mm, name, size=11, color=WHITE_HEX, bold=True)
    txt(c, M + 4 * mm, y_top + 11 * mm, desc, size=9, color=LIGHT_GRAY)
    # color bar left
    bar(c, M, y_top, 1.5 * mm, 15 * mm, color)

# No app, no cloud badge
card(c, M, 180 * mm, PW - 2 * M, 14 * mm, CARD_BG_ALT)
txt(c, M + 4 * mm, 184 * mm, "No app. No cloud. No BLE. No WiFi. No clips.",
    size=13, color=ACCENT_ORANGE, bold=True)
txt(c, M + 4 * mm, 191 * mm, "MCU generates tone in real-time. 60 seconds to first use.",
    size=10, color=LIGHT_GRAY)

# Firmware
bar(c, M, 200 * mm, PW - 2 * M, 1 * mm, ACCENT_GREEN)
txt(c, M, 205 * mm, "FIRMWARE", size=11, color=ACCENT_GREEN, bold=True)
fw_items = [
    "Bare-metal (no RTOS) on ATtiny1616 (16KB flash, 2KB SRAM)",
    "8 modules: sleep mgr, tilt reader, filter, tone gen,",
    "escalation curves, mode mgr, calibration, battery monitor",
    "Boot-to-ready: < 3 seconds. Tone generated via HW PWM.",
]
fy = 212 * mm
for item in fw_items:
    txt(c, M + 4 * mm, fy, item, size=9, color=SOFT_WHITE)
    fy += 5.5 * mm

footer(c, 3, TOTAL_PAGES)
c.showPage()

# ================================================================
# PAGE 4: Constraints & BOM
# ================================================================
bg(c)
accent_strip(c, ACCENT_ORANGE)

txt(c, M, 12 * mm, "Constraints & BOM", size=28, color=WHITE_HEX, bold=True)
bar(c, M, 22 * mm, 30 * mm, 0.8 * mm, ACCENT_ORANGE)

# Hard constraints
constraints = [
    ("BOM cost", "< $8 at 1k units", "Retail $15-25, gift/novelty price"),
    ("Battery life", "> 6 months (CR2450)", "20 tilt events/day, ~9 months typical"),
    ("Latency", "< 500ms tilt-to-sound", "Comedy timing is the product"),
    ("Size", "35mm dia x 10mm", "Hidden under chair seat"),
    ("Weight", "< 18g assembled", "Adhesive pad holds it up"),
    ("Drop survival", "1.5m onto hard floor", "Falls off chairs regularly"),
]

for i, (name, value, note) in enumerate(constraints):
    y_top = 28 * mm + i * 18 * mm
    bg_c = CARD_BG if i % 2 == 0 else CARD_BG_ALT
    card(c, M, y_top, PW - 2 * M, 15 * mm, bg_c)
    txt(c, M + 4 * mm, y_top + 4 * mm, name, size=12, color=ACCENT_ORANGE, bold=True)
    txt(c, M + 4 * mm, y_top + 11 * mm, note, size=9, color=LIGHT_GRAY)
    txt(c, M + 4 * mm, y_top + 4 * mm, value, size=12, color=WHITE_HEX, bold=True,
        align="right", max_w=PW - 2 * M - 8 * mm)

# BOM breakdown
bar(c, M, 140 * mm, PW - 2 * M, 1 * mm, ACCENT_GREEN)
txt(c, M, 145 * mm, "BOM ESTIMATE (1k units)", size=11, color=ACCENT_GREEN, bold=True)

bom = [
    ("ATtiny1616 MCU", "$0.60"),
    ("LIS2DH12 accelerometer", "$0.80"),
    ("Class-D amp (PAM8302)", "$0.30"),
    ("Piezo disc (13mm)", "$0.30"),
    ("CR2450 holder + battery", "$0.65"),
    ("PCB (30x25mm, 2-layer)", "$0.50"),
    ("Passives + button", "$0.25"),
    ("Enclosure (ABS molded)", "$1.50"),
    ("Adhesive pad + packaging", "$1.00"),
    ("Assembly + test", "$1.50"),
]

for i, (item, cost) in enumerate(bom):
    y_top = 152 * mm + i * 7.5 * mm
    bg_c = CARD_BG if i % 2 == 0 else CARD_BG_ALT
    card_flat(c, M + 2 * mm, y_top, PW - 2 * M - 4 * mm, 6.5 * mm, bg_c)
    txt(c, M + 6 * mm, y_top + 2 * mm, item, size=9, color=SOFT_WHITE)
    txt(c, M + 6 * mm, y_top + 2 * mm, cost, size=9, color=WHITE_HEX, bold=True,
        align="right", max_w=PW - 2 * M - 16 * mm)

# Total
card_flat(c, M + 2 * mm, 227 * mm, PW - 2 * M - 4 * mm, 7 * mm, ACCENT_ORANGE)
txt(c, M + 6 * mm, 229 * mm, "Total COGS", size=10, color=WHITE_HEX, bold=True)
txt(c, M + 6 * mm, 229 * mm, "~$7.40", size=10, color=WHITE_HEX, bold=True,
    align="right", max_w=PW - 2 * M - 16 * mm)

footer(c, 4, TOTAL_PAGES)
c.showPage()

# ================================================================
# PAGE 5: Hardest Problems
# ================================================================
bg(c)
accent_strip(c, ACCENT_RED)

txt(c, M, 12 * mm, "Hardest Problems", size=28, color=WHITE_HEX, bold=True)
bar(c, M, 22 * mm, 30 * mm, 0.8 * mm, ACCENT_RED)

problems = [
    ("Escalation curve across chair types",
     "School chairs and dining chairs have different fall points and tilt ranges. "
     "The continuous tone must start gently at first leg lift and "
     "peak just before the fall point -- not too early (annoying) or "
     "too late (useless). Needs auto-calibration + playtesting on 5+ types."),
    ("Filtering fidgeting from tilting",
     "Sitting down, crossing legs, leaning to grab something "
     "all produce accelerometer signals. The continuous model means "
     "any sustained tilt produces sound -- the dead-band (~2 deg) and "
     "300ms time filter are critical to avoid false alarms."),
    ("Designing the continuous tone",
     "The tilt-to-tone mapping IS the product. Must be agreeable "
     "at low tilt and urgent near the fall point. Three modes need "
     "distinct character. Needs sound designer + playtesting with kids."),
]

for i, (title, desc) in enumerate(problems):
    y_top = 30 * mm + i * 58 * mm
    card(c, M, y_top, PW - 2 * M, 52 * mm, CARD_BG)
    circle_num(c, M + 4 * mm, y_top + 4 * mm, i + 1, ACCENT_RED)
    txt(c, M + 16 * mm, y_top + 6 * mm, title, size=14, color=WHITE_HEX, bold=True)
    txt_wrap(c, M + 6 * mm, y_top + 18 * mm, desc,
             size=11, color=LIGHT_GRAY, max_w=PW - 2 * M - 12 * mm, line_h=14)

# Bottom takeaway
card_flat(c, M, 210 * mm, PW - 2 * M, 22 * mm, CARD_BG)
txt_wrap(c, M + 4 * mm, 214 * mm,
         "Hardware is simple. The product lives or dies on the "
         "escalation curve -- how tilt maps to tone. Playtesting > engineering.",
         size=12, color=ACCENT_ORANGE, max_w=PW - 2 * M - 8 * mm, line_h=15)

footer(c, 5, TOTAL_PAGES)
c.showPage()

# ================================================================
# PAGE 6: PRD Summary
# ================================================================
bg(c)
accent_strip(c, ACCENT_BLUE)

txt(c, M, 12 * mm, "PRD: 45 Requirements", size=28, color=WHITE_HEX, bold=True)
bar(c, M, 22 * mm, 30 * mm, 0.8 * mm, ACCENT_BLUE)

# Gate result badge
card(c, PW - M - 40 * mm, 8 * mm, 38 * mm, 14 * mm, ACCENT_GREEN)
txt(c, PW - M - 38 * mm, 11 * mm, "GATE: PASS", size=14, color=WHITE_HEX, bold=True)
txt(c, PW - M - 38 * mm, 18 * mm, "66 pass / 23 N/A / 1 gap", size=8, color=WHITE_HEX)

# By track
bar(c, M, 28 * mm, PW - 2 * M, 1 * mm, ACCENT_BLUE)
txt(c, M, 32 * mm, "BY TRACK", size=11, color=ACCENT_BLUE, bold=True)

tracks = [
    ("Hardware", "18", "8 electrical + 8 mechanical + 4 PCB", ACCENT_ORANGE),
    ("Firmware", "18", "7 core + 4 modes + 4 calibration + 2 power + 1 versioning", ACCENT_GREEN),
    ("Integration", "9", "End-to-end tests spanning HW + FW", ACCENT_RED),
]

for i, (name, count, detail, color) in enumerate(tracks):
    y_top = 38 * mm + i * 18 * mm
    card(c, M, y_top, PW - 2 * M, 15 * mm, CARD_BG)
    bar(c, M, y_top, 2 * mm, 15 * mm, color)
    txt(c, M + 6 * mm, y_top + 4 * mm, name, size=13, color=WHITE_HEX, bold=True)
    txt(c, M + 6 * mm, y_top + 4 * mm, count, size=13, color=color, bold=True,
        align="right", max_w=PW - 2 * M - 12 * mm)
    txt(c, M + 6 * mm, y_top + 11 * mm, detail, size=8, color=LIGHT_GRAY)

# Priority
bar(c, M, 95 * mm, PW - 2 * M, 1 * mm, ACCENT_ORANGE)
txt(c, M, 99 * mm, "BY PRIORITY", size=11, color=ACCENT_ORANGE, bold=True)
card(c, M, 104 * mm, PW - 2 * M, 15 * mm, CARD_BG)
txt(c, M + 6 * mm, 108 * mm, "40 Must-have", size=14, color=ACCENT_ORANGE, bold=True)
txt(c, M + 50 * mm, 108 * mm, "5 Should-have", size=14, color=ACCENT_GREEN, bold=True)
txt(c, M + 6 * mm, 115 * mm, "0 Nice-to-have (deferred to V2)", size=9, color=LIGHT_GRAY)

# Key requirements
bar(c, M, 125 * mm, PW - 2 * M, 1 * mm, ACCENT_GREEN)
txt(c, M, 129 * mm, "KEY REQUIREMENTS", size=11, color=ACCENT_GREEN, bold=True)

key_reqs = [
    ("FW-C-05", "Continuous tone scales with tilt angle"),
    ("FW-C-06", "Angle-to-tone tracking < 100ms"),
    ("INT-02", "Zero false triggers on transient motion"),
    ("FW-PM-04", "Battery life >= 6 months at 20 events/day"),
    ("HW-M-01", "Enclosure max 35mm dia x 10mm height"),
    ("HW-E-06", "Total sleep current <= 2 uA"),
]

for i, (req_id, desc) in enumerate(key_reqs):
    y_top = 135 * mm + i * 12 * mm
    bg_c = CARD_BG if i % 2 == 0 else CARD_BG_ALT
    card(c, M, y_top, PW - 2 * M, 10 * mm, bg_c)
    txt(c, M + 4 * mm, y_top + 3.5 * mm, req_id, size=9, color=ACCENT_BLUE, bold=True)
    txt(c, M + 26 * mm, y_top + 3.5 * mm, desc, size=9, color=SOFT_WHITE)

# Traceability
bar(c, M, 210 * mm, PW - 2 * M, 1 * mm, LIGHT_GRAY)
txt(c, M, 214 * mm, "TRACEABILITY", size=9, color=LIGHT_GRAY, bold=True)
traces = [
    "S1 Dinner table -> FW-C-01..07, INT-01, INT-03",
    "S2 Classroom -> FW-M-01, FW-M-04, INT-04, HW-M-06",
    "S3 First use -> FW-CAL-01, FW-CAL-04, HW-M-06",
    "S4 Battery swap -> HW-M-04, FW-PM-02..03, INT-06",
    "S5 False trigger -> FW-C-03, FW-C-04, INT-02",
]
ty = 220 * mm
for t_line in traces:
    txt(c, M + 4 * mm, ty, t_line, size=7, color=LIGHT_GRAY)
    ty += 4 * mm

footer(c, 6, TOTAL_PAGES)
c.showPage()

# ================================================================
# PAGE 7: Open Items & V2
# ================================================================
bg(c)
accent_strip(c, ACCENT_ORANGE)

txt(c, M, 12 * mm, "Open Items & V2", size=28, color=WHITE_HEX, bold=True)
bar(c, M, 22 * mm, 30 * mm, 0.8 * mm, ACCENT_ORANGE)

# Open items
txt(c, M, 28 * mm, "7 OPEN ITEMS (resolve before production)", size=11, color=ACCENT_ORANGE, bold=True)

open_items = [
    ("M2", "Escalation curve tuning across 5+ chair types"),
    ("M2", "Piezo volume validation in real environments"),
    ("M2", "False trigger testing with real users"),
    ("M2", "PWM audio quality -- pleasant at low tilt?"),
    ("M2", "CPSIA / EN 71 acoustic safety check"),
    ("M3", "Tone design for 3 modes (sound designer + FW)"),
    ("M3", "Adhesive durability testing"),
]

for i, (milestone, desc) in enumerate(open_items):
    y_top = 34 * mm + i * 13 * mm
    bg_c = CARD_BG if i % 2 == 0 else CARD_BG_ALT
    card(c, M, y_top, PW - 2 * M, 11 * mm, bg_c)
    txt(c, M + 4 * mm, y_top + 3.5 * mm, milestone, size=10, color=ACCENT_ORANGE, bold=True)
    txt(c, M + 20 * mm, y_top + 3.5 * mm, desc, size=10, color=SOFT_WHITE)

# V2
bar(c, M, 130 * mm, PW - 2 * M, 1 * mm, ACCENT_BLUE)
txt(c, M, 134 * mm, "V2 HORIZON (if market validates)", size=11, color=ACCENT_BLUE, bold=True)

v2_features = [
    ("Custom tone profiles via USB", "Board respin: USB-C, upload escalation curve params"),
    ("BLE + companion app", "MCU swap: ATtiny -> nRF52. Full board respin + app dev"),
    ("Adjustable sensitivity", "Requires BLE. Depends on companion app decision"),
    ("Rechargeable battery", "Adds charging IC, USB-C, Li-Po. Enclosure redesign"),
]

for i, (feature, impact) in enumerate(v2_features):
    y_top = 140 * mm + i * 20 * mm
    card(c, M, y_top, PW - 2 * M, 17 * mm, CARD_BG)
    txt(c, M + 4 * mm, y_top + 4 * mm, feature, size=12, color=ACCENT_BLUE, bold=True)
    txt(c, M + 4 * mm, y_top + 12 * mm, impact, size=9, color=LIGHT_GRAY)

# Bottom
card_flat(c, M, 225 * mm, PW - 2 * M, 10 * mm, CARD_BG)
txt_wrap(c, M + 4 * mm, 228 * mm,
         "V2 decisions wait for 6+ months of V1 sales data and customer feedback.",
         size=10, color=LIGHT_GRAY, max_w=PW - 2 * M - 8 * mm)

footer(c, 7, TOTAL_PAGES)
c.showPage()

# ================================================================
c.save()
print(f"Saved {TOTAL_PAGES}-page carousel PDF to {output}")
print(f"Page size: {PW/mm:.0f} x {PH/mm:.0f} mm (4:5 ratio)")
