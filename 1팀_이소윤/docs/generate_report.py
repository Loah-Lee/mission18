from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "backend" / "movies.db"
OUTPUT_PATH = ROOT / "report.pdf"
ARCH_IMAGE_PATH = ROOT / "docs" / "architecture.png"
ERD_IMAGE_PATH = ROOT / "docs" / "erd.png"
FONT_PATH = Path("/System/Library/Fonts/Supplemental/AppleGothic.ttf")
FONT_NAME = "AppleGothic"


def register_font() -> None:
    pdfmetrics.registerFont(TTFont(FONT_NAME, str(FONT_PATH)))


def load_summary() -> list[tuple[str, int, float | None, int, int, int]]:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        """
        SELECT
            m.title,
            COUNT(r.id) AS review_count,
            ROUND(AVG(r.sentiment_score), 2) AS avg_score,
            SUM(CASE WHEN r.sentiment_label = 'positive' THEN 1 ELSE 0 END) AS positive_count,
            SUM(CASE WHEN r.sentiment_label = 'neutral' THEN 1 ELSE 0 END) AS neutral_count,
            SUM(CASE WHEN r.sentiment_label = 'negative' THEN 1 ELSE 0 END) AS negative_count
        FROM movies m
        LEFT JOIN reviews r ON r.movie_id = m.id
        GROUP BY m.id, m.title
        ORDER BY m.id
        """
    ).fetchall()
    conn.close()
    return rows


def build_story():
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleKorean",
        parent=styles["Title"],
        fontName=FONT_NAME,
        fontSize=22,
        leading=28,
        alignment=TA_CENTER,
        spaceAfter=12,
    )
    heading_style = ParagraphStyle(
        "HeadingKorean",
        parent=styles["Heading2"],
        fontName=FONT_NAME,
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#1f3b73"),
        spaceBefore=8,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "BodyKorean",
        parent=styles["BodyText"],
        fontName=FONT_NAME,
        fontSize=10.5,
        leading=15,
        spaceAfter=4,
    )
    small_style = ParagraphStyle(
        "SmallKorean",
        parent=body_style,
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#444444"),
    )

    story = []
    story.append(Paragraph("영화 리뷰 감성 분석 서비스 보고서", title_style))
    story.append(Paragraph("미션 18 제출용 초안", body_style))
    story.append(Paragraph(f"작성일: {datetime.now().strftime('%Y-%m-%d')}", body_style))
    story.append(Spacer(1, 10 * mm))

    story.append(Paragraph("1. 서비스 개요", heading_style))
    story.append(
        Paragraph(
            "본 서비스는 영화 정보, 사용자 리뷰, 감성 분석 결과를 함께 제공하는 웹 애플리케이션이다. "
            "프론트엔드는 Streamlit, 백엔드는 FastAPI로 구성했으며, 리뷰 등록 시 Hugging Face 한국어 감성 분석 모델을 호출해 결과를 저장한다.",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "기술 스택: Streamlit, FastAPI, SQLAlchemy, SQLite, Hugging Face Transformers, PyTorch",
            body_style,
        )
    )

    story.append(Paragraph("2. 서비스 구조", heading_style))
    story.append(
        Paragraph(
            "사용자는 Streamlit 화면에서 영화를 등록하고 리뷰를 작성한다. Streamlit은 FastAPI API를 호출해 데이터를 저장하고 조회한다. "
            "리뷰가 등록되면 FastAPI는 감성 분석 모델을 실행하고, 분석 결과를 SQLite 데이터베이스에 함께 저장한다.",
            body_style,
        )
    )
    architecture_table = Table(
        [
            ["사용자", "Streamlit 프론트엔드", "FastAPI 백엔드", "SQLite DB / 감성 분석 모델"],
        ],
        colWidths=[28 * mm, 45 * mm, 45 * mm, 58 * mm],
    )
    architecture_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#e9f0fb")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#13294b")),
                ("FONTNAME", (0, 0), (-1, -1), FONT_NAME),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.75, colors.HexColor("#8aa4d6")),
                ("TOPPADDING", (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ]
        )
    )
    story.append(architecture_table)
    story.append(Spacer(1, 6 * mm))
    if ARCH_IMAGE_PATH.exists() and ARCH_IMAGE_PATH.stat().st_size > 0:
        story.append(Spacer(1, 4 * mm))
        story.append(Image(str(ARCH_IMAGE_PATH), width=168 * mm, height=94.5 * mm))
    else:
        story.append(
            Paragraph(
                "실제 제출본에는 구조도 캡처 또는 다이어그램 이미지를 추가하는 것이 좋다.",
                small_style,
            )
        )

    story.append(Paragraph("3. 구현 기능", heading_style))
    feature_rows = [
        ["영화 관리", "영화 등록, 조회, 수정, 삭제"],
        ["리뷰 관리", "리뷰 등록, 영화별 리뷰 조회, 리뷰 삭제"],
        ["감성 분석", "리뷰 등록 시 자동 분석 후 label/score 저장"],
        ["평균 평점", "영화별 리뷰 감성 점수 평균 계산"],
        ["시각화", "영화별 평균 평점 그래프와 감성 분포 그래프 제공"],
    ]
    feature_table = Table([["구분", "구현 내용"], *feature_rows], colWidths=[35 * mm, 135 * mm])
    feature_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbe8ff")),
                ("FONTNAME", (0, 0), (-1, -1), FONT_NAME),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(feature_table)

    story.append(Paragraph("4. 데이터베이스 구조(ERD)", heading_style))
    story.append(
        Paragraph(
            "Movie 테이블은 영화 기본 정보를 저장하고, Review 테이블은 영화별 리뷰와 감성 분석 결과를 저장한다. "
            "Movie 1개에 Review 여러 개가 연결되는 1:N 구조다.",
            body_style,
        )
    )
    erd_table = Table(
        [
            ["Movie", "Review"],
            [
                "id\n"
                "title\n"
                "release_date\n"
                "director\n"
                "genre\n"
                "poster_url\n"
                "created_at",
                "id\n"
                "movie_id\n"
                "author\n"
                "content\n"
                "sentiment_label\n"
                "sentiment_score\n"
                "created_at",
            ],
        ],
        colWidths=[90 * mm, 90 * mm],
    )
    erd_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f2f5fb")),
                ("FONTNAME", (0, 0), (-1, -1), FONT_NAME),
                ("GRID", (0, 0), (-1, -1), 0.75, colors.HexColor("#9aa7bd")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(erd_table)
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph("Movie 1 : N Review", body_style))
    if ERD_IMAGE_PATH.exists() and ERD_IMAGE_PATH.stat().st_size > 0:
        story.append(Spacer(1, 4 * mm))
        story.append(Image(str(ERD_IMAGE_PATH), width=168 * mm, height=108 * mm))

    story.append(PageBreak())

    story.append(Paragraph("5. API 명세 요약", heading_style))
    api_rows = [
        ["GET /health", "서버 상태 확인"],
        ["POST /movies", "영화 등록"],
        ["GET /movies", "전체 영화 조회"],
        ["GET /movies/{movie_id}", "특정 영화 조회"],
        ["PUT /movies/{movie_id}", "영화 정보 수정"],
        ["DELETE /movies/{movie_id}", "영화 삭제"],
        ["GET /movies/{movie_id}/rating", "영화 평균 평점 조회"],
        ["POST /reviews", "리뷰 등록 및 감성 분석"],
        ["GET /reviews", "전체 리뷰 조회"],
        ["GET /movies/{movie_id}/reviews", "영화별 리뷰 조회"],
        ["DELETE /reviews/{review_id}", "리뷰 삭제"],
    ]
    api_table = Table([["엔드포인트", "설명"], *api_rows], colWidths=[65 * mm, 105 * mm])
    api_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbe8ff")),
                ("FONTNAME", (0, 0), (-1, -1), FONT_NAME),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(api_table)
    story.append(Spacer(1, 4 * mm))
    story.append(
        Paragraph(
            "FastAPI Swagger Docs URL: http://127.0.0.1:8000/docs. 제출본에는 전체 화면 캡처 이미지를 함께 넣어야 한다.",
            small_style,
        )
    )

    story.append(Paragraph("6. 모델 선택 및 경량화 고려", heading_style))
    story.append(
        Paragraph(
            "감성 분석 모델은 Hugging Face의 monologg/koelectra-small-finetuned-sentiment를 사용했다. "
            "한국어 문장 분류에 적합하고 small 계열이라 M1 8GB 로컬 환경에서 비교적 가볍게 실행할 수 있어 선택했다.",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "또한 영화 리뷰에는 슬픔, 여운, 반어적 표현이 많아 단순 감정어만으로는 오분류가 발생할 수 있다. "
            "이를 줄이기 위해 리뷰 평가 관점의 후처리 규칙을 추가해 분류를 보정했다.",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "경량화 관점에서는 작은 모델 선택, 앱 시작 후 1회 로드 및 재사용, 로컬 CPU 기반 추론 가능성을 중심으로 고려했다.",
            body_style,
        )
    )

    story.append(Paragraph("7. 테스트 데이터 요약", heading_style))
    summary_rows = [["영화 제목", "리뷰 수", "평균 평점", "긍정", "중립", "부정"]]
    for title, review_count, avg_score, positive_count, neutral_count, negative_count in load_summary():
        summary_rows.append(
            [
                title,
                str(review_count),
                "-" if avg_score is None else f"{avg_score:.2f}",
                str(positive_count or 0),
                str(neutral_count or 0),
                str(negative_count or 0),
            ]
        )
    summary_table = Table(summary_rows, colWidths=[48 * mm, 20 * mm, 24 * mm, 18 * mm, 18 * mm, 18 * mm])
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbe8ff")),
                ("FONTNAME", (0, 0), (-1, -1), FONT_NAME),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(summary_table)

    story.append(Paragraph("8. 제출 전 남은 작업", heading_style))
    remaining_tasks = [
        "서비스 구조도 이미지 추가",
        "ERD 이미지 추가",
        "FastAPI Docs 전체 캡처 추가",
        "영화 페이지와 리뷰 페이지 동작 캡처 추가",
        "Streamlit Cloud 배포 후 URL 반영",
    ]
    for idx, task in enumerate(remaining_tasks, start=1):
        story.append(Paragraph(f"{idx}. {task}", body_style))

    return story


def main() -> None:
    register_font()
    doc = SimpleDocTemplate(
        str(OUTPUT_PATH),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="영화 리뷰 감성 분석 서비스 보고서",
        author="1팀 이소윤",
    )
    doc.build(build_story())
    print(f"Generated: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
