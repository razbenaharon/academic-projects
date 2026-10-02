"""Generate the required one-page submission explanation PDF."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "id_000000000_000000000.pdf"

styles = getSampleStyleSheet()
title = ParagraphStyle(
    "TitleCompact", parent=styles["Title"], fontName="Helvetica-Bold",
    fontSize=16, leading=19, alignment=TA_CENTER, textColor=colors.HexColor("#17365D"),
    spaceAfter=4,
)
subtitle = ParagraphStyle(
    "Subtitle", parent=styles["Normal"], fontSize=8.5, leading=10.5,
    alignment=TA_CENTER, textColor=colors.HexColor("#555555"), spaceAfter=7,
)
heading = ParagraphStyle(
    "HeadingCompact", parent=styles["Heading2"], fontName="Helvetica-Bold",
    fontSize=10.2, leading=12, textColor=colors.HexColor("#1F4E79"),
    spaceBefore=3, spaceAfter=1.5,
)
body = ParagraphStyle(
    "BodyCompact", parent=styles["BodyText"], fontName="Helvetica",
    fontSize=8.25, leading=10.25, spaceAfter=2.2,
)

doc = SimpleDocTemplate(
    str(OUTPUT), pagesize=A4,
    leftMargin=15 * mm, rightMargin=15 * mm,
    topMargin=12 * mm, bottomMargin=12 * mm,
    title="HW3 Adaptive GSP Bidding Strategies",
    author="000000000_000000000",
)

story = [
    Paragraph("HW3 - Adaptive GSP Bidding Strategies", title),
    Paragraph("Agent ID 000000000_000000000 | Implementation: id_000000000_000000000.py", subtitle),
    Paragraph("Task and shared market learner", heading),
    Paragraph(
        "The assignment runs repeated Generalized Second Price auctions. Agent 1 maximizes "
        "utility without a budget constraint; Agent 2 must maximize utility while pacing a "
        "finite budget whose leftover value is zero. After every round, all agents observe "
        "(agent ID, slot, price) for every winner. In GSP, a slot price equals the raw bid of "
        "the agent immediately below it, so the implementation reconstructs every non-top "
        "winning bid and maintains a conservative lower-bound estimate for the censored top bid.",
        body,
    ),
    Paragraph(
        "Both agents keep a bounded rolling history of sorted opponent-bid snapshots. Candidate "
        "bids combine a value-scaled grid with small increments above rank boundaries observed in "
        "the latest five rounds. Replaying the latest 30 snapshots estimates the slot, payment, "
        "click-adjusted utility, and spend for each candidate. These fixed horizons make running "
        "time and memory independent of T and allow fast adaptation to changing opponents.",
        body,
    ),
    Paragraph("Agent 1 - unconstrained strategy", heading),
    Paragraph(
        "The first round bids the private value to obtain an informative observation. Later rounds "
        "select the candidate with maximum empirical utility, CTR[j] * (value - price[j]), with "
        "ties resolved toward the lower bid. A floor of 0.65 * value prevents the empirical best "
        "response from yielding too much rank to competitors; the learner can still bid above the "
        "floor when a higher slot is worthwhile. Bids never exceed the private value.",
        body,
    ),
    Paragraph("Agent 2 - budget pacing", heading),
    Paragraph(
        "The budgeted agent estimates expected utility and spend for every candidate. Its per-round "
        "target is 0.95 * remaining_budget / remaining_rounds. The small reserve offsets optimistic "
        "sampling error, while recomputing the target each round releases unused reserve later. A "
        "bounded binary search finds a budget shadow price lambda; for each lambda the chosen action "
        "maximizes expected_utility - lambda * expected_spend. The two frontier actions bracketing "
        "the target are randomized in the proportion needed to match it. Every bid is capped by both "
        "private value and remaining budget.",
        body,
    ),
    Paragraph("Validation and alternatives", heading),
    Paragraph(
        "Local paired benchmarks rotated the same sampled values and budgets among agents. Tests "
        "included fresh-only top-bid bounds, short and weighted histories, constant shading from "
        "55%-85%, pacing targets from 80%-125%, and budget-dependent bid floors. The 65% floor was "
        "the strongest robust Agent 1 hybrid. For Agent 2, the 30-snapshot estimator with a 95% "
        "target improved utility on two independent seed groups. Hard budget floors were rejected "
        "because their performance varied sharply across markets.",
        body,
    ),
    Spacer(1, 2 * mm),
    Paragraph(
        "Safety: standard library only; finite non-negative bids; fixed-size history; value and "
        "budget caps; bounded searches designed for the 50 ms callback limit.",
        ParagraphStyle("FooterNote", parent=body, fontSize=7.8, leading=9.5,
                       textColor=colors.HexColor("#444444"),
                       borderColor=colors.HexColor("#A9C4DC"), borderWidth=0.5,
                       borderPadding=4, backColor=colors.HexColor("#F4F8FB")),
    ),
]

doc.build(story)
print(OUTPUT)
