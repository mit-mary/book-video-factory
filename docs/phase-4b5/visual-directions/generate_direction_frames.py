"""Generate Phase 4B.5 visual-direction keyframes from text-free art atlases.

This is a static review-board generator only. It is not a Remotion composition,
does not render video, and does not alter the production renderer.
"""

from __future__ import annotations

import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "source-assets"
W, H = 1080, 1920
FONT = Path(r"C:\Windows\Fonts\Noto Sans SC (TrueType).otf")
BOLD = Path(r"C:\Windows\Fonts\Noto Sans SC Bold (TrueType).otf")

IVORY = "#F1E9D8"
PAPER = "#F8F3E8"
INK = "#201F1B"
RUST = "#A84F34"
BLUE = "#294C67"
AMBER = "#D8A238"
GRAPHITE = "#3D3A36"
MUSTARD = "#C59A32"
BURGUNDY = "#744238"
SAGE = "#7C8874"
VERMILION = "#A6402C"
BRASS = "#A78145"


FRAME_NAMES = (
    "frame-01-hook.png",
    "frame-02-small-action.png",
    "frame-03-three-actions.png",
    "frame-04-turning.png",
    "frame-05-ending.png",
)


def font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(BOLD if bold else FONT), size=size)


def paper(color: str, seed: int) -> Image.Image:
    image = Image.new("RGB", (W, H), color)
    draw = ImageDraw.Draw(image, "RGBA")
    rng = random.Random(seed)
    for _ in range(2600):
        x = rng.randrange(W)
        y = rng.randrange(H)
        alpha = rng.randrange(3, 13)
        tone = 30 if rng.random() < 0.55 else 245
        draw.point((x, y), fill=(tone, tone, tone, alpha))
    for _ in range(12):
        y = rng.randrange(H)
        draw.line((0, y, W, y + rng.randrange(-8, 9)), fill=(70, 60, 45, 8), width=1)
    return image


def crop(atlas: Image.Image, box: tuple[int, int, int, int]) -> Image.Image:
    return atlas.crop(box).convert("RGB")


def fit(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    return ImageOps.fit(image, size, method=Image.Resampling.LANCZOS)


def torn_mask(size: tuple[int, int], seed: int, jitter: int = 13) -> Image.Image:
    w, h = size
    rng = random.Random(seed)
    points: list[tuple[int, int]] = []
    step = 38
    for x in range(0, w + step, step):
        points.append((min(x, w), rng.randrange(0, jitter + 1)))
    for y in range(step, h + step, step):
        points.append((w - rng.randrange(0, jitter + 1), min(y, h)))
    for x in range(w - step, -step, -step):
        points.append((max(x, 0), h - rng.randrange(0, jitter + 1)))
    for y in range(h - step, 0, -step):
        points.append((rng.randrange(0, jitter + 1), y))
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).polygon(points, fill=255)
    return mask


def paste_torn(
    canvas: Image.Image,
    source: Image.Image,
    rect: tuple[int, int, int, int],
    *,
    seed: int,
    angle: float = 0,
    border: int = 14,
    shadow: tuple[int, int] = (15, 20),
) -> None:
    x, y, w, h = rect
    photo = fit(source, (w, h)).convert("RGBA")
    mask = torn_mask((w, h), seed)
    photo.putalpha(mask)
    backing = Image.new("RGBA", (w + border * 2, h + border * 2), PAPER)
    backing.alpha_composite(photo, (border, border))
    backing = backing.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
    alpha = backing.getchannel("A")
    shadow_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    shadow_blob = Image.new("RGBA", backing.size, (20, 18, 14, 75))
    shadow_blob.putalpha(alpha.filter(ImageFilter.GaussianBlur(5)))
    shadow_layer.alpha_composite(shadow_blob, (x + shadow[0], y + shadow[1]))
    canvas.alpha_composite(shadow_layer)
    canvas.alpha_composite(backing, (x, y))


def label(draw: ImageDraw.ImageDraw, text: str, xy: tuple[int, int], *, color: str) -> None:
    x, y = xy
    draw.rounded_rectangle((x, y, x + 164, y + 46), radius=3, fill=color)
    draw.text((x + 14, y + 9), text, font=font(20, bold=True), fill=PAPER)


def rule(draw: ImageDraw.ImageDraw, xy: tuple[int, int, int, int], color: str, width: int = 5) -> None:
    draw.line(xy, fill=color, width=width)


def multiline(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    size: int,
    *,
    fill: str = INK,
    bold: bool = False,
    spacing: int = 18,
    anchor: str | None = None,
    align: str = "left",
) -> None:
    draw.multiline_text(
        xy,
        text,
        font=font(size, bold=bold),
        fill=fill,
        spacing=spacing,
        anchor=anchor,
        align=align,
    )


def direction_a(atlas: Image.Image) -> list[Image.Image]:
    hand = crop(atlas, (18, 18, 500, 674))
    switch = crop(atlas, (523, 18, 1005, 674))
    trio = (
        crop(atlas, (18, 697, 330, 1075)),
        crop(atlas, (333, 697, 676, 1075)),
        crop(atlas, (679, 697, 1005, 1075)),
    )
    road = crop(atlas, (18, 1098, 500, 1520))
    walker = crop(atlas, (523, 1098, 1005, 1520))
    frames: list[Image.Image] = []

    c = paper(IVORY, 101).convert("RGBA")
    paste_torn(c, hand, (-60, 70, 720, 1350), seed=11, angle=-2.5, border=12)
    d = ImageDraw.Draw(c)
    d.polygon([(610, 0), (1080, 0), (1080, 1920), (760, 1920), (690, 1180)], fill=INK)
    label(d, "EDITORIAL / 01", (742, 90), color=RUST)
    multiline(d, (760, 300), "改变\n生活", 116, fill=PAPER, bold=True, spacing=2)
    rule(d, (760, 570, 1010, 570), AMBER, 10)
    multiline(d, (740, 640), "通常不是\n一个重大决定。", 48, fill=PAPER, bold=True, spacing=20)
    multiline(d, (760, 1660), "改变生活的，", 35, fill="#D7CDBB")
    frames.append(c.convert("RGB"))

    c = paper(PAPER, 102).convert("RGBA")
    d = ImageDraw.Draw(c)
    d.rectangle((0, 0, 330, 1920), fill=BLUE)
    paste_torn(c, switch, (245, 190, 780, 1120), seed=12, angle=1.7, border=18)
    label(d, "SCALE / 02", (72, 90), color=RUST)
    d.rectangle((50, 270, 365, 520), fill=BLUE)
    multiline(d, (70, 290), "真正\n起作用的", 58, fill=PAPER, bold=True, spacing=8)
    d.ellipse((170, 1450, 194, 1474), fill=AMBER)
    multiline(d, (215, 1415), "往往只是", 38, fill=INK)
    multiline(d, (215, 1490), "一个很小的动作。", 74, fill=INK, bold=True)
    rule(d, (215, 1605, 875, 1605), RUST, 7)
    frames.append(c.convert("RGB"))

    c = paper(IVORY, 103).convert("RGBA")
    d = ImageDraw.Draw(c)
    label(d, "THREE CUTS / 03", (72, 70), color=INK)
    titles = ("早睡十分钟。", "拒绝一次迎合。", "承认自己的不舒服。")
    colors = (BLUE, RUST, GRAPHITE)
    ys = (210, 715, 1220)
    angles = (-1.8, 1.4, -1.0)
    for index, (img, title, color, y, angle) in enumerate(zip(trio, titles, colors, ys, angles)):
        side = 70 if index != 1 else 420
        paste_torn(c, img, (side, y, 560, 410), seed=30 + index, angle=angle, border=12, shadow=(12, 15))
        tx = 680 if index != 1 else 72
        d.rectangle((tx, y + 95, tx + 330, y + 107), fill=color)
        multiline(d, (tx, y + 135), title.replace("。", "。\n" if index == 2 else ""), 44, fill=INK, bold=True, spacing=8)
        d.text((tx, y + 45), f"0{index + 1}", font=font(24, bold=True), fill=color)
    frames.append(c.convert("RGB"))

    c = paper("#E8DFCD", 104).convert("RGBA")
    paste_torn(c, road, (-30, 210, 1140, 1420), seed=41, angle=-1.2, border=0, shadow=(0, 0))
    d = ImageDraw.Draw(c)
    d.rectangle((0, 0, 1080, 260), fill=INK)
    multiline(d, (72, 55), "生活不会突然改变，", 54, fill=PAPER, bold=True)
    d.polygon([(650, 1360), (1080, 1210), (1080, 1920), (560, 1920)], fill=RUST)
    multiline(d, (790, 1420), "转\n向", 150, fill=PAPER, bold=True, spacing=-10, anchor="mm", align="center")
    multiline(d, (72, 1720), "它只是慢慢转向。", 44, fill=INK, bold=True)
    frames.append(c.convert("RGB"))

    c = paper(IVORY, 105).convert("RGBA")
    paste_torn(c, walker, (0, 0, 700, 1920), seed=51, angle=0, border=0, shadow=(0, 0))
    d = ImageDraw.Draw(c)
    d.rectangle((700, 0, 1080, 1920), fill=PAPER)
    label(d, "AFTER / 05", (760, 90), color=BLUE)
    multiline(d, (760, 320), "你今天的\n一个小选择，", 52, fill=INK, bold=True, spacing=18)
    rule(d, (760, 620, 1010, 620), AMBER, 9)
    multiline(d, (760, 720), "可能正在\n改变以后\n的人生。", 67, fill=RUST, bold=True, spacing=15)
    frames.append(c.convert("RGB"))
    return frames


def direction_b(atlas: Image.Image) -> list[Image.Image]:
    tear = crop(atlas, (12, 12, 504, 649))
    blank = crop(atlas, (518, 12, 1012, 649))
    trio = (
        crop(atlas, (12, 663, 350, 1000)),
        crop(atlas, (352, 663, 650, 1000)),
        crop(atlas, (652, 663, 1012, 1000)),
    )
    tabs = crop(atlas, (12, 1013, 504, 1524))
    open_book = crop(atlas, (518, 1013, 1012, 1524))
    frames: list[Image.Image] = []

    c = paper("#E9E3D8", 201).convert("RGBA")
    paste_torn(c, tear, (120, 110, 840, 1420), seed=61, angle=-1.3, border=10)
    d = ImageDraw.Draw(c)
    multiline(d, (185, 270), "改变生活的，", 45, fill=GRAPHITE)
    multiline(d, (185, 365), "通常不是一个\n重大决定。", 78, fill=INK, bold=True, spacing=16)
    rule(d, (190, 585, 815, 610), GRAPHITE, 9)
    d.rectangle((790, 1280, 1015, 1500), fill=MUSTARD)
    multiline(d, (900, 1390), "01", 38, fill=INK, bold=True, anchor="mm", align="center")
    frames.append(c.convert("RGB"))

    c = paper("#D8D2C8", 202).convert("RGBA")
    paste_torn(c, blank, (95, 80, 900, 1680), seed=62, angle=0.7, border=8)
    d = ImageDraw.Draw(c)
    d.text((145, 190), "P. 02", font=font(22, bold=True), fill=SAGE)
    multiline(d, (170, 500), "真正起作用的，", 42, fill=GRAPHITE)
    multiline(d, (170, 605), "往往只是一个", 56, fill=INK, bold=True)
    d.rectangle((170, 730, 370, 790), fill=MUSTARD)
    multiline(d, (185, 728), "很小", 40, fill=INK, bold=True)
    multiline(d, (390, 720), "的动作。", 56, fill=INK, bold=True)
    rule(d, (165, 840, 765, 825), GRAPHITE, 7)
    d.arc((690, 980, 900, 1200), 60, 240, fill=BURGUNDY, width=7)
    frames.append(c.convert("RGB"))

    c = paper(PAPER, 203).convert("RGBA")
    d = ImageDraw.Draw(c)
    d.rectangle((80, 70, 1000, 1850), outline="#B8AE9D", width=3)
    d.text((120, 110), "MARGIN NOTES / 03", font=font(22, bold=True), fill=BURGUNDY)
    items = (
        ("早睡十分钟。", MUSTARD),
        ("拒绝一次迎合。", BURGUNDY),
        ("承认自己的不舒服。", SAGE),
    )
    for i, (img, (title, color)) in enumerate(zip(trio, items)):
        y = 260 + i * 500
        paste_torn(c, img, (135 if i != 1 else 500, y, 420, 330), seed=70 + i, angle=(-1.5 + i * 1.2), border=8, shadow=(9, 12))
        tx = 610 if i != 1 else 130
        d.rectangle((tx, y + 40, tx + 16, y + 250), fill=color)
        multiline(d, (tx + 35, y + 55), title.replace("自己的", "自己的\n"), 39, fill=INK, bold=True, spacing=10)
        rule(d, (tx + 30, y + 205, min(tx + 360, 940), y + 220), color, 5)
    frames.append(c.convert("RGB"))

    c = paper("#E7E0D2", 204).convert("RGBA")
    paste_torn(c, tabs, (0, 0, 1080, 1920), seed=80, angle=0, border=0, shadow=(0, 0))
    d = ImageDraw.Draw(c)
    d.rectangle((90, 120, 705, 380), fill=(248, 243, 232, 235))
    multiline(d, (125, 155), "生活不会突然改变，", 47, fill=INK, bold=True)
    multiline(d, (125, 240), "它只是", 35, fill=GRAPHITE)
    multiline(d, (125, 305), "慢慢转向。", 72, fill=BURGUNDY, bold=True)
    d.arc((430, 610, 1030, 1280), 40, 250, fill=GRAPHITE, width=10)
    frames.append(c.convert("RGB"))

    c = paper("#D9D1C3", 205).convert("RGBA")
    paste_torn(c, open_book, (0, 0, 1080, 1920), seed=90, angle=0, border=0, shadow=(0, 0))
    d = ImageDraw.Draw(c)
    d.rectangle((120, 260, 930, 860), fill=(248, 243, 232, 222))
    multiline(d, (175, 330), "你今天的一个小选择，", 48, fill=GRAPHITE)
    multiline(d, (175, 445), "可能正在改变", 68, fill=INK, bold=True)
    multiline(d, (175, 570), "以后的人生。", 68, fill=BURGUNDY, bold=True)
    rule(d, (175, 690, 760, 680), MUSTARD, 12)
    d.text((820, 800), "05", font=font(26, bold=True), fill=SAGE)
    frames.append(c.convert("RGB"))
    return frames


def direction_c(atlas: Image.Image) -> list[Image.Image]:
    lever = crop(atlas, (15, 15, 503, 679))
    tiny = crop(atlas, (518, 15, 1009, 679))
    trio = (
        crop(atlas, (15, 695, 294, 988)),
        crop(atlas, (296, 695, 729, 988)),
        crop(atlas, (732, 695, 1009, 988)),
    )
    track = crop(atlas, (15, 1004, 503, 1523))
    compass = crop(atlas, (518, 1004, 1009, 1523))
    frames: list[Image.Image] = []

    c = paper("#D8CFBE", 301).convert("RGBA")
    paste_torn(c, lever, (0, 0, 1080, 1920), seed=101, angle=0, border=0, shadow=(0, 0))
    d = ImageDraw.Draw(c)
    d.rectangle((0, 0, 1080, 280), fill=INK)
    multiline(d, (75, 60), "改变生活的，", 43, fill="#CFC2AD")
    multiline(d, (75, 125), "通常不是一个重大决定。", 57, fill=PAPER, bold=True)
    d.rectangle((755, 1530, 1015, 1700), fill=VERMILION)
    multiline(d, (885, 1615), "重大决定", 38, fill=PAPER, bold=True, anchor="mm", align="center")
    frames.append(c.convert("RGB"))

    c = paper("#E9E1D3", 302).convert("RGBA")
    paste_torn(c, tiny, (0, 0, 1080, 1920), seed=102, angle=0, border=0, shadow=(0, 0))
    d = ImageDraw.Draw(c)
    multiline(d, (75, 150), "真正起作用的，", 46, fill="#D8CFBE")
    multiline(d, (75, 245), "往往只是", 62, fill=PAPER, bold=True)
    multiline(d, (775, 1285), "很小", 35, fill=VERMILION, bold=True, anchor="mm")
    multiline(d, (775, 1370), "的动作。", 52, fill=INK, bold=True, anchor="mm")
    rule(d, (680, 1450, 870, 1450), BRASS, 8)
    frames.append(c.convert("RGB"))

    c = paper("#E5DCCD", 303).convert("RGBA")
    d = ImageDraw.Draw(c)
    d.text((70, 75), "THREE SMALL PERMISSIONS", font=font(20, bold=True), fill=VERMILION)
    titles = ("早睡十分钟。", "拒绝一次迎合。", "承认自己的\n不舒服。")
    for i, (img, title) in enumerate(zip(trio, titles)):
        if i == 0:
            rect, tx, ty = (80, 250, 560, 520), 700, 390
        elif i == 1:
            rect, tx, ty = (450, 760, 560, 480), 80, 900
        else:
            rect, tx, ty = (90, 1320, 470, 420), 620, 1460
        paste_torn(c, img, rect, seed=110 + i, angle=(-1.3 + i), border=6, shadow=(10, 13))
        multiline(d, (tx, ty), title, 41, fill=INK, bold=True, spacing=8)
        d.ellipse((tx, ty - 45, tx + 18, ty - 27), fill=(BRASS, VERMILION, GRAPHITE)[i])
    frames.append(c.convert("RGB"))

    c = paper("#DFD5C4", 304).convert("RGBA")
    paste_torn(c, track, (0, 0, 1080, 1920), seed=120, angle=0, border=0, shadow=(0, 0))
    d = ImageDraw.Draw(c)
    d.rectangle((70, 80, 680, 300), fill=(245, 239, 226, 235))
    multiline(d, (105, 115), "生活不会突然改变，", 44, fill=GRAPHITE, bold=True)
    multiline(d, (610, 1240), "它只是", 34, fill=GRAPHITE, bold=True)
    multiline(d, (610, 1320), "慢慢\n转向", 102, fill=VERMILION, bold=True, spacing=-4)
    rule(d, (600, 1510, 950, 1510), BRASS, 9)
    frames.append(c.convert("RGB"))

    c = paper("#D7CEBE", 305).convert("RGBA")
    paste_torn(c, compass, (0, 0, 1080, 1920), seed=130, angle=0, border=0, shadow=(0, 0))
    d = ImageDraw.Draw(c)
    d.rectangle((80, 110, 960, 440), fill=(244, 237, 223, 224))
    multiline(d, (120, 155), "你今天的一个小选择，", 45, fill=GRAPHITE)
    multiline(d, (120, 245), "可能正在改变", 62, fill=INK, bold=True)
    multiline(d, (120, 350), "以后的人生。", 62, fill=VERMILION, bold=True)
    frames.append(c.convert("RGB"))
    return frames


def contact_sheet(direction: str, title: str, frames: list[Image.Image], palette: tuple[str, ...]) -> Image.Image:
    sheet = Image.new("RGB", (3300, 1260), "#EEE8DC")
    draw = ImageDraw.Draw(sheet)
    draw.text((90, 55), title, font=font(58, bold=True), fill=INK)
    draw.text((90, 135), "PHASE 4B.5 / FIVE KEYFRAMES / 1080×1920", font=font(24, bold=True), fill=GRAPHITE)
    for i, color in enumerate(palette):
        draw.rounded_rectangle((2500 + i * 100, 65, 2570 + i * 100, 135), radius=35, fill=color)
    thumb_w, thumb_h = 560, 996
    for index, frame in enumerate(frames):
        x = 90 + index * 635
        y = 215
        thumb = fit(frame, (thumb_w, thumb_h))
        shadow = Image.new("RGBA", (thumb_w + 28, thumb_h + 28), (0, 0, 0, 0))
        ImageDraw.Draw(shadow).rectangle((20, 20, thumb_w + 20, thumb_h + 20), fill=(20, 18, 15, 55))
        sheet.paste(shadow, (x, y), shadow)
        sheet.paste(thumb, (x, y))
        draw.text((x, 1220), f"0{index + 1}", font=font(24, bold=True), fill=palette[index % len(palette)])
    return sheet


def main() -> None:
    atlases = {
        "a": Image.open(ASSETS / "direction-a-art-atlas.png").convert("RGB"),
        "b": Image.open(ASSETS / "direction-b-art-atlas.png").convert("RGB"),
        "c": Image.open(ASSETS / "direction-c-art-atlas.png").convert("RGB"),
    }
    outputs = {
        "a": (ROOT / "direction-a-editorial", direction_a(atlases["a"])),
        "b": (ROOT / "direction-b-book-notes", direction_b(atlases["b"])),
        "c": (ROOT / "direction-c-visual-metaphor", direction_c(atlases["c"])),
    }
    for _, (directory, frames) in outputs.items():
        directory.mkdir(parents=True, exist_ok=True)
        for name, frame in zip(FRAME_NAMES, frames):
            if frame.size != (W, H):
                raise ValueError(f"unexpected keyframe dimensions: {frame.size}")
            frame.save(directory / name, format="PNG", optimize=True)
    contact_sheet(
        "a",
        "A. EDITORIAL PAPER COLLAGE",
        outputs["a"][1],
        (RUST, BLUE, AMBER, INK, "#D7CDBB"),
    ).save(ROOT / "direction-a-contact-sheet.png", format="PNG", optimize=True)
    contact_sheet(
        "b",
        "B. QUIET BOOK NOTES",
        outputs["b"][1],
        (MUSTARD, BURGUNDY, SAGE, GRAPHITE, "#B8AE9D"),
    ).save(ROOT / "direction-b-contact-sheet.png", format="PNG", optimize=True)
    contact_sheet(
        "c",
        "C. VISUAL METAPHOR COLLAGE",
        outputs["c"][1],
        (VERMILION, BRASS, INK, "#D8CFBE", "#6F6251"),
    ).save(ROOT / "direction-c-contact-sheet.png", format="PNG", optimize=True)


if __name__ == "__main__":
    main()
