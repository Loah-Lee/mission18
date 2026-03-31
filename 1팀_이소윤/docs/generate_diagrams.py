from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
ARCH_PATH = ROOT / "architecture.png"
ERD_PATH = ROOT / "erd.png"
FONT_PATH = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"


def get_font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_PATH, size)


def draw_box(draw: ImageDraw.ImageDraw, xy, text: str, fill: str, outline: str) -> None:
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=18, fill=fill, outline=outline, width=3)
    font = get_font(26)
    bbox = draw.multiline_textbbox((0, 0), text, font=font, spacing=6, align="center")
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    draw.multiline_text(
        ((x1 + x2 - text_w) / 2, (y1 + y2 - text_h) / 2),
        text,
        font=font,
        fill="#1b2a41",
        spacing=6,
        align="center",
    )


def draw_arrow(draw: ImageDraw.ImageDraw, start, end, label: str = "") -> None:
    draw.line([start, end], fill="#355070", width=5)
    arrow = 12
    ex, ey = end
    draw.polygon(
        [(ex, ey), (ex - arrow, ey - arrow / 1.8), (ex - arrow, ey + arrow / 1.8)],
        fill="#355070",
    )
    if label:
        font = get_font(18)
        mx = (start[0] + end[0]) / 2
        my = (start[1] + end[1]) / 2 - 28
        draw.text((mx - 55, my), label, font=font, fill="#355070")


def generate_architecture() -> None:
    image = Image.new("RGB", (1600, 900), "#f7f9fc")
    draw = ImageDraw.Draw(image)

    title_font = get_font(38)
    draw.text((60, 45), "서비스 구조도", font=title_font, fill="#13294b")

    draw_box(draw, (70, 260, 330, 430), "사용자", "#fff4d6", "#e9c46a")
    draw_box(draw, (430, 220, 760, 470), "Streamlit\n프론트엔드", "#ddeafc", "#7aa6e3")
    draw_box(draw, (870, 220, 1200, 470), "FastAPI\n백엔드", "#ddeafc", "#7aa6e3")
    draw_box(draw, (1290, 120, 1530, 300), "SQLite\nDB", "#e6f6ec", "#5bb381")
    draw_box(draw, (1290, 390, 1530, 570), "Hugging Face\n감성 분석 모델", "#fde7ea", "#e76f51")

    draw_arrow(draw, (330, 345), (430, 345), "입력/조회")
    draw_arrow(draw, (760, 345), (870, 345), "API 호출")
    draw_arrow(draw, (1200, 255), (1290, 210), "저장/조회")
    draw_arrow(draw, (1200, 435), (1290, 480), "리뷰 분석")

    note_font = get_font(20)
    note = "리뷰 등록 시 FastAPI가 감성 분석 모델을 호출하고, 분석 결과를 DB에 저장"
    draw.text((60, 810), note, font=note_font, fill="#3d4f68")
    image.save(ARCH_PATH)


def generate_erd() -> None:
    image = Image.new("RGB", (1400, 900), "#f7f9fc")
    draw = ImageDraw.Draw(image)
    title_font = get_font(38)
    body_font = get_font(24)
    draw.text((60, 45), "데이터베이스 구조도 (ERD)", font=title_font, fill="#13294b")

    movie_box = (90, 170, 610, 700)
    review_box = (790, 170, 1310, 700)

    draw.rounded_rectangle(movie_box, radius=18, fill="#eaf2ff", outline="#7aa6e3", width=3)
    draw.rounded_rectangle(review_box, radius=18, fill="#edf8f1", outline="#5bb381", width=3)

    draw.text((125, 205), "Movie", font=get_font(30), fill="#13294b")
    draw.text((825, 205), "Review", font=get_font(30), fill="#13294b")

    movie_fields = [
        "id (PK)",
        "title",
        "release_date",
        "director",
        "genre",
        "poster_url",
        "created_at",
    ]
    review_fields = [
        "id (PK)",
        "movie_id (FK)",
        "author",
        "content",
        "sentiment_label",
        "sentiment_score",
        "created_at",
    ]

    y = 270
    for field in movie_fields:
        draw.text((125, y), f"- {field}", font=body_font, fill="#1b2a41")
        y += 58

    y = 270
    for field in review_fields:
        draw.text((825, y), f"- {field}", font=body_font, fill="#1b2a41")
        y += 58

    draw.line([(610, 430), (790, 430)], fill="#355070", width=5)
    draw.polygon([(790, 430), (774, 420), (774, 440)], fill="#355070")
    draw.text((650, 380), "1 : N", font=get_font(28), fill="#355070")
    draw.text((620, 465), "Movie.id -> Review.movie_id", font=get_font(20), fill="#355070")

    image.save(ERD_PATH)


def main() -> None:
    generate_architecture()
    generate_erd()
    print(f"Generated: {ARCH_PATH}")
    print(f"Generated: {ERD_PATH}")


if __name__ == "__main__":
    main()
