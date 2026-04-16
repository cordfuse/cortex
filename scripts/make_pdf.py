#!/usr/bin/env python3
"""
Generate a Cortex summary PDF for non-technical readers.
Usage: python scripts/make_pdf.py [output_path]
Default output: cortex-overview.pdf in the repo root.
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "cortex-overview.pdf")

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER

# --- Palette ---
INK        = colors.HexColor("#1a1a2e")   # near-black
ACCENT     = colors.HexColor("#4f46e5")   # indigo
LIGHT_RULE = colors.HexColor("#e2e2f0")
MUTED      = colors.HexColor("#5c5c7a")
TAG_BG     = colors.HexColor("#f0effc")

# --- Styles ---
def styles():
    return {
        "title": ParagraphStyle(
            "title",
            fontName="Helvetica-Bold",
            fontSize=28,
            leading=34,
            textColor=INK,
            spaceAfter=2*mm,
        ),
        "subtitle": ParagraphStyle(
            "subtitle",
            fontName="Helvetica",
            fontSize=13,
            leading=18,
            textColor=MUTED,
            spaceAfter=6*mm,
        ),
        "section": ParagraphStyle(
            "section",
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=16,
            textColor=ACCENT,
            spaceBefore=7*mm,
            spaceAfter=2*mm,
            textTransform="uppercase",
            letterSpacing=1.2,
        ),
        "body": ParagraphStyle(
            "body",
            fontName="Helvetica",
            fontSize=10,
            leading=15,
            textColor=INK,
            spaceAfter=3*mm,
        ),
        "bullet": ParagraphStyle(
            "bullet",
            fontName="Helvetica",
            fontSize=10,
            leading=15,
            textColor=INK,
            leftIndent=8*mm,
            bulletIndent=2*mm,
            spaceAfter=1.5*mm,
        ),
        "bold_lead": ParagraphStyle(
            "bold_lead",
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=15,
            textColor=INK,
            spaceAfter=1*mm,
        ),
        "caption": ParagraphStyle(
            "caption",
            fontName="Helvetica-Oblique",
            fontSize=8.5,
            leading=12,
            textColor=MUTED,
            spaceBefore=6*mm,
            alignment=TA_CENTER,
        ),
    }


def build():
    doc = SimpleDocTemplate(
        OUTPUT,
        pagesize=A4,
        leftMargin=22*mm,
        rightMargin=22*mm,
        topMargin=22*mm,
        bottomMargin=22*mm,
        title="Cortex — Overview",
        author="Cordfuse",
    )

    S = styles()
    W = A4[0] - 44*mm   # usable width
    story = []

    # ── Header ──────────────────────────────────────────────────────────────
    story.append(Paragraph("Cortex", S["title"]))
    story.append(Paragraph(
        "A private record of your life — or your team's.&nbsp; Git-driven. AI-scribed.",
        S["subtitle"]
    ))
    story.append(HRFlowable(width=W, thickness=1, color=ACCENT, spaceAfter=4*mm))

    # ── The problem ──────────────────────────────────────────────────────────
    story.append(Paragraph("The Problem", S["section"]))
    story.append(Paragraph(
        "Your life happens across a hundred apps — none of them talk to each other, "
        "none of them are yours, and none of them have any idea who you are.",
        S["body"]
    ))
    for line in [
        "Notes rot in silos.",
        "Health records disappear when you switch providers.",
        "Work logs don't connect to personal patterns.",
        "Therapy insights evaporate between sessions.",
        "Every AI conversation starts from zero.",
    ]:
        story.append(Paragraph(f"\u2022&nbsp;&nbsp;{line}", S["bullet"]))

    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "Existing tools are either too simple, too clinical, or too locked-in — "
        "and the AI tools that could help process your most sensitive records on "
        "servers you don't control, under privacy policies you didn't write.",
        S["body"]
    ))

    # ── What Cortex does differently ─────────────────────────────────────────
    story.append(Paragraph("What Cortex Does Differently", S["section"]))

    points = [
        ("You own everything.",
         "Records live in your private git repository — not a vendor's database. "
         "Plain text files. Readable by any tool, forever. Portable the day you want out."),
        ("The AI is a scribe, not a product.",
         "It listens, organises, and files. It follows a protocol you can read and modify. "
         "No upsell, no monetised insights, no lock-in."),
        ("Context that carries.",
         "At session start the scribe reads your recent records. It knows what you were "
         "working through, what's unresolved, what patterns have been building. "
         "Every session picks up where the last one left off."),
        ("Analysis on demand.",
         "Ask the scribe to look across your records and tell you what it sees. "
         "Patterns, connections, escalations, progress — the kind of insight that "
         "only emerges when everything is in one place."),
        ("Private by default, offline if you need it.",
         "Run fully local with a self-hosted AI and git server. Nothing leaves your machine."),
    ]

    for bold, rest in points:
        story.append(Paragraph(f"<b>{bold}</b>&nbsp; {rest}", S["body"]))

    # ── Solo or collaborative ────────────────────────────────────────────────
    story.append(Paragraph("Solo or Collaborative", S["section"]))
    story.append(Paragraph(
        "Cortex works for one person. It also works for any number of people sharing a repo. "
        "Clone the same repository, run your own AI agent against it, commit your entries. "
        "Everyone pushes, everyone pulls, everyone sees the full record. "
        "Git handles the collaboration. The AI handles the scribing.",
        S["body"]
    ))

    use_cases = [
        "A couple's shared health journal",
        "A team's decision log",
        "A family's care record",
        "A band's creative sessions",
        "A startup's retrospectives",
    ]
    for uc in use_cases:
        story.append(Paragraph(f"\u2022&nbsp;&nbsp;{uc}", S["bullet"]))

    story.append(Spacer(1, 2*mm))
    story.append(Paragraph(
        "Each person can use a different AI. One uses Claude, another uses ChatGPT, "
        "another uses Qwen. Same repo. Same protocol. Same truth.",
        S["body"]
    ))

    # ── What it covers ───────────────────────────────────────────────────────
    story.append(Paragraph("What It Covers", S["section"]))
    story.append(Paragraph(
        "Cortex ships with 19 templates across every domain worth recording:",
        S["body"]
    ))

    table_data = [
        [Paragraph("<b>Category</b>", S["body"]), Paragraph("<b>Templates</b>", S["body"])],
        ["Personal",    "Daily log, event, person, theory / insight"],
        ["Health",      "Therapy session, medication, symptoms, appointment"],
        ["Life admin",  "Finance, inventory, supplies, tasks"],
        ["Work",        "Work log, project, career"],
        ["Creative",    "Idea, creative session"],
        ["Analytical",  "Analysis, review"],
    ]

    col_w = [40*mm, W - 40*mm]
    table = Table(table_data, colWidths=col_w)
    table.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, 0), TAG_BG),
        ("TEXTCOLOR",   (0, 0), (-1, 0), ACCENT),
        ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, -1), 9.5),
        ("LEADING",     (0, 0), (-1, -1), 14),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f8fc")]),
        ("GRID",        (0, 0), (-1, -1), 0.4, LIGHT_RULE),
        ("LEFTPADDING",  (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING",   (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
    ]))
    story.append(table)

    # ── Works with ───────────────────────────────────────────────────────────
    story.append(Paragraph("Works With", S["section"]))
    story.append(Paragraph(
        "Any major AI agent — Claude, ChatGPT, Gemini CLI, OpenCode, Qwen — "
        "on any device. Desktop, mobile, or fully offline. "
        "Switch agents mid-session. Pick up on your phone what you started on your desktop.",
        S["body"]
    ))

    # ── Get started ──────────────────────────────────────────────────────────
    story.append(Paragraph("Get Started", S["section"]))
    steps = [
        "Create a private repository from the Cortex template on GitHub.",
        "Clone it to your device.",
        "Open it in your AI agent of choice and say hello.",
        "The scribe takes it from there.",
    ]
    for i, step in enumerate(steps, 1):
        story.append(Paragraph(f"{i}.&nbsp;&nbsp;{step}", S["bullet"]))

    story.append(Spacer(1, 2*mm))
    story.append(Paragraph(
        "Mobile users: set up a Claude or ChatGPT project with the included system prompt "
        "and your repository credentials. Every new chat opens a session automatically — "
        "no terminal, no setup.",
        S["body"]
    ))

    # ── Rule ─────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 4*mm))
    story.append(HRFlowable(width=W, thickness=0.5, color=LIGHT_RULE, spaceAfter=4*mm))

    story.append(Paragraph(
        "github.com/cordfuse/cortex&nbsp;&nbsp;·&nbsp;&nbsp;MIT licence&nbsp;&nbsp;·&nbsp;&nbsp;"
        "Nothing in Cortex constitutes medical, legal, or psychiatric advice.",
        S["caption"]
    ))

    doc.build(story)
    print(f"Written: {OUTPUT}")


if __name__ == "__main__":
    build()
