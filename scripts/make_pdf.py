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
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    Table, TableStyle, KeepTogether, PageBreak
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

# ── Palette ──────────────────────────────────────────────────────────────────
INK        = colors.HexColor("#16213e")
ACCENT     = colors.HexColor("#4f46e5")
ACCENT_DK  = colors.HexColor("#3730a3")
ACCENT_LT  = colors.HexColor("#ede9fe")
PROBLEM    = colors.HexColor("#be123c")
PROBLEM_LT = colors.HexColor("#fff1f2")
SUCCESS    = colors.HexColor("#15803d")
SUCCESS_LT = colors.HexColor("#f0fdf4")
RULE       = colors.HexColor("#e2e2f0")
MUTED      = colors.HexColor("#64748b")
WHITE      = colors.white
TAG_BG     = colors.HexColor("#f8f7ff")
STRIPE     = colors.HexColor("#f9f9fd")
HEAD_BG    = colors.HexColor("#4f46e5")

W_PAGE = A4[0] - 44*mm   # usable width

# ── Style factory ─────────────────────────────────────────────────────────────
def S():
    return {
        "title": ParagraphStyle("title",
            fontName="Helvetica-Bold", fontSize=32, leading=38,
            textColor=WHITE, spaceAfter=1*mm),
        "tagline": ParagraphStyle("tagline",
            fontName="Helvetica", fontSize=13, leading=18,
            textColor=colors.HexColor("#c7d2fe"), spaceAfter=0),
        "section_label": ParagraphStyle("section_label",
            fontName="Helvetica-Bold", fontSize=10.5, leading=14,
            textColor=WHITE),
        "body": ParagraphStyle("body",
            fontName="Helvetica", fontSize=10, leading=15.5,
            textColor=INK, spaceAfter=3*mm),
        "body_sm": ParagraphStyle("body_sm",
            fontName="Helvetica", fontSize=9.5, leading=14.5,
            textColor=INK),
        "body_muted": ParagraphStyle("body_muted",
            fontName="Helvetica", fontSize=9.5, leading=14,
            textColor=MUTED),
        "bullet": ParagraphStyle("bullet",
            fontName="Helvetica", fontSize=10, leading=15,
            textColor=INK, leftIndent=6*mm, spaceAfter=1.5*mm),
        "bullet_sm": ParagraphStyle("bullet_sm",
            fontName="Helvetica", fontSize=9.5, leading=14,
            textColor=INK, leftIndent=4*mm, spaceAfter=1*mm),
        "bold_lead": ParagraphStyle("bold_lead",
            fontName="Helvetica-Bold", fontSize=10, leading=15,
            textColor=INK, spaceAfter=1*mm),
        "problem": ParagraphStyle("problem",
            fontName="Helvetica", fontSize=9.5, leading=14,
            textColor=PROBLEM),
        "solution": ParagraphStyle("solution",
            fontName="Helvetica", fontSize=9.5, leading=14,
            textColor=SUCCESS),
        "caption": ParagraphStyle("caption",
            fontName="Helvetica-Oblique", fontSize=8, leading=12,
            textColor=MUTED, alignment=TA_CENTER),
        "table_head": ParagraphStyle("table_head",
            fontName="Helvetica-Bold", fontSize=9.5, leading=13,
            textColor=WHITE),
        "table_cell": ParagraphStyle("table_cell",
            fontName="Helvetica", fontSize=9.5, leading=14,
            textColor=INK),
        "table_cell_bold": ParagraphStyle("table_cell_bold",
            fontName="Helvetica-Bold", fontSize=9.5, leading=14,
            textColor=INK),
        "step_num": ParagraphStyle("step_num",
            fontName="Helvetica-Bold", fontSize=13, leading=16,
            textColor=ACCENT),
        "step_text": ParagraphStyle("step_text",
            fontName="Helvetica", fontSize=10, leading=15,
            textColor=INK),
    }


# ── Helpers ───────────────────────────────────────────────────────────────────

def section_box(label, styles):
    """Indigo full-width heading box."""
    t = Table(
        [[Paragraph(label.upper(), styles["section_label"])]],
        colWidths=[W_PAGE]
    )
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,-1), HEAD_BG),
        ("LEFTPADDING",  (0,0), (-1,-1), 5*mm),
        ("RIGHTPADDING", (0,0), (-1,-1), 5*mm),
        ("TOPPADDING",   (0,0), (-1,-1), 3.5*mm),
        ("BOTTOMPADDING",(0,0), (-1,-1), 3.5*mm),
        ("ROUNDEDCORNERS", [3]),
    ]))
    return t


def spacer(h=3):
    return Spacer(1, h*mm)


def rule(color=RULE):
    return HRFlowable(width=W_PAGE, thickness=0.5, color=color, spaceAfter=3*mm, spaceBefore=1*mm)


def bullet(text, styles, key="bullet"):
    return Paragraph(f"\u2022\u2002{text}", styles[key])


def p(text, styles, key="body"):
    return Paragraph(text, styles[key])


# ── Build ─────────────────────────────────────────────────────────────────────

def build():
    doc = SimpleDocTemplate(
        OUTPUT,
        pagesize=A4,
        leftMargin=22*mm, rightMargin=22*mm,
        topMargin=18*mm, bottomMargin=18*mm,
        title="Cortex — Overview",
        author="Cordfuse",
    )

    styles = S()
    story  = []

    # ════════════════════════════════════════════════════════════════════
    # HERO BANNER
    # ════════════════════════════════════════════════════════════════════
    hero = Table(
        [[
            Paragraph("Cortex", styles["title"]),
            ""
        ],[
            Paragraph(
                "A private record of your life — or your team's.&nbsp; "
                "Git-driven. AI-scribed.",
                styles["tagline"]),
            ""
        ]],
        colWidths=[W_PAGE * 0.78, W_PAGE * 0.22]
    )
    hero.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), HEAD_BG),
        ("LEFTPADDING",   (0,0), (-1,-1), 6*mm),
        ("RIGHTPADDING",  (0,0), (-1,-1), 4*mm),
        ("TOPPADDING",    (0,0), (0,0),   5*mm),
        ("BOTTOMPADDING", (0,1), (-1,-1), 5*mm),
        ("TOPPADDING",    (0,1), (-1,-1), 1*mm),
        ("SPAN",          (0,0), (0,0)),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(hero)
    story.append(spacer(4))

    # ── Intro paragraph ──────────────────────────────────────────────────────
    intro_style = ParagraphStyle("intro",
        fontName="Helvetica", fontSize=10.5, leading=16.5,
        textColor=INK, spaceAfter=3*mm,
        borderPad=4*mm, borderColor=ACCENT_LT,
        backColor=ACCENT_LT,
        leftIndent=0, rightIndent=0,
    )
    story.append(Paragraph(
        "Cortex is a private, AI-assisted record-keeper for your life — or your team's. "
        "Instead of notes scattered across dozens of apps, everything goes into one place <i>you</i> own: "
        "a secure private folder of plain text files stored in your own online account "
        "<i>(think of it like a personal filing cabinet in the cloud, but one only you control)</i>. "
        "An <i>AI scribe</i> (a conversational AI assistant like Claude or ChatGPT) listens as you talk, "
        "organises what you say, and files it automatically. "
        "Every session picks up where the last one left off — on any device, with any AI. "
        "Nothing is sent to Cordfuse. Nothing is sold. The records are yours, forever.",
        intro_style
    ))
    story.append(spacer(3))

    # ════════════════════════════════════════════════════════════════════
    # PROBLEM vs SOLUTION  (two-column comparison)
    # ════════════════════════════════════════════════════════════════════
    story.append(KeepTogether([
        section_box("The Problem — and What Cortex Does About It", styles),
        spacer(3),
    ]))

    col = (W_PAGE - 4*mm) / 2

    problems = [
        ("Notes rot in app silos",
         "Your notes, health records, work logs and journal "
         "entries all live in different apps that never talk to each other."),
        ("Every AI chat starts from zero",
         "No AI tool remembers what you told it last week. "
         "You re-explain your situation every single session."),
        ("You don't own your data",
         "Your most personal records live on vendor servers, "
         "under privacy policies written by lawyers, not you."),
        ("Sensitive data processed by third parties",
         "Cloud AI tools send your records to servers you don't control. "
         "Subpoenas, breaches, and policy changes are out of your hands."),
        ("Lock-in is invisible until it hurts",
         "Proprietary formats and closed APIs mean the day you "
         "want out, you often can't take your history with you."),
        ("No pattern-level insight",
         "Individual entries are useful. Seeing what they add up to "
         "over months is where the real value is — and no tool does that."),
    ]

    solutions = [
        ("One repo, everything connected",
         "All records in one private repository <i>(a secure folder that tracks every change)</i> — "
         "dated files, plain text, readable by any tool now and in twenty years."),
        ("Context that carries across every session",
         "At session start the AI scribe reads your recent records. "
         "It knows what's unresolved. Every session picks up where you left off."),
        ("You own everything — permanently",
         "Records live in your own account. No vendor can delete them, "
         "sell them, or lock them away. Move them anywhere. They're yours."),
        ("Private by default, offline if you need it",
         "Run fully local <i>(on your own computer, no internet required)</i> with a self-hosted AI. "
         "Nothing ever leaves your machine."),
        ("Plain text, forever portable",
         "No proprietary format. No export button needed. "
         "Read it with any text editor, today or in a decade."),
        ("Analysis on demand",
         "Ask the scribe to look across everything and tell you what it sees — "
         "patterns, escalations, connections, progress. The full picture."),
    ]

    def ps_para(title, body, title_color):
        title_style = ParagraphStyle("_t",
            fontName="Helvetica-Bold", fontSize=9.5, leading=13,
            textColor=title_color, spaceAfter=2)
        body_style = ParagraphStyle("_b",
            fontName="Helvetica", fontSize=9, leading=13,
            textColor=MUTED)
        return [Paragraph(title, title_style), Paragraph(body, body_style)]

    # header row
    hdr = Table(
        [[
            Paragraph("THE PROBLEM", styles["table_head"]),
            Paragraph("THE CORTEX ANSWER", styles["table_head"]),
        ]],
        colWidths=[col, col], rowHeights=[8*mm]
    )
    hdr.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (0,0), PROBLEM),
        ("BACKGROUND",    (1,0), (1,0), SUCCESS),
        ("LEFTPADDING",   (0,0), (-1,-1), 4*mm),
        ("RIGHTPADDING",  (0,0), (-1,-1), 4*mm),
        ("TOPPADDING",    (0,0), (-1,-1), 2*mm),
        ("BOTTOMPADDING", (0,0), (-1,-1), 2*mm),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("LINEAFTER",     (0,0), (0,-1), 1, WHITE),
    ]))
    story.append(hdr)

    for i, (prob, sol) in enumerate(zip(problems, solutions)):
        row_bg_p = PROBLEM_LT if i % 2 == 0 else WHITE
        row_bg_s = SUCCESS_LT if i % 2 == 0 else WHITE
        row = Table(
            [[
                ps_para(prob[0], prob[1], PROBLEM),
                ps_para(sol[0],  sol[1],  SUCCESS),
            ]],
            colWidths=[col, col]
        )
        row.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (0,0), row_bg_p),
            ("BACKGROUND",    (1,0), (1,0), row_bg_s),
            ("LEFTPADDING",   (0,0), (-1,-1), 4*mm),
            ("RIGHTPADDING",  (0,0), (-1,-1), 4*mm),
            ("TOPPADDING",    (0,0), (-1,-1), 3*mm),
            ("BOTTOMPADDING", (0,0), (-1,-1), 3*mm),
            ("VALIGN",        (0,0), (-1,-1), "TOP"),
            ("LINEAFTER",     (0,0), (0,-1), 0.5, RULE),
            ("LINEBELOW",     (0,0), (-1,-1), 0.5, RULE),
        ]))
        story.append(row)

    story.append(spacer(3))

    # ════════════════════════════════════════════════════════════════════
    # HOW IT WORKS
    # ════════════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(KeepTogether([
        section_box("How It Works", styles),
        spacer(3),
        p(
            "You open Cortex in your AI agent <i>(a conversational AI assistant — Claude, ChatGPT, "
            "Gemini, or similar)</i> and talk. "
            "The scribe listens, asks clarifying questions, and organises what you say into "
            "structured dated files in your private repository <i>(your secure personal folder of records)</i>. "
            "At session end, everything is saved and synced automatically. "
            "Your records are yours — permanently, portably, privately.",
            styles
        ),
    ]))

    steps = [
        ("1", "Open your repo in any AI agent — Claude Code, Gemini CLI, OpenCode, Qwen, or Claude Desktop. On mobile, open your Cortex project in Claude or ChatGPT."),
        ("2", "Say hello. The scribe reads your recent records and picks up where you left off."),
        ("3", "Talk. Work through whatever's on your mind. The scribe listens, reflects back, and asks one clarifying question at a time."),
        ("4", "When something is worth filing, the scribe flags it: <i>File this?</i> — and handles the rest."),
        ("5", "At session end: everything is saved and synced <i>(committed and pushed — meaning saved with a timestamp and backed up to your online account)</i>. Open items are surfaced. You're done."),
    ]

    step_rows = []
    for num, text in steps:
        step_rows.append([
            Paragraph(num, styles["step_num"]),
            Paragraph(text, styles["step_text"]),
        ])

    step_table = Table(step_rows, colWidths=[10*mm, W_PAGE - 10*mm])
    step_table.setStyle(TableStyle([
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING",   (0,0), (0,-1),  0),
        ("RIGHTPADDING",  (0,0), (-1,-1), 3*mm),
        ("TOPPADDING",    (0,0), (-1,-1), 1.5*mm),
        ("BOTTOMPADDING", (0,0), (-1,-1), 2*mm),
        ("LINEBELOW",     (0,0), (-1,-2), 0.4, RULE),
    ]))
    story.append(step_table)
    story.append(spacer(3))

    # ════════════════════════════════════════════════════════════════════
    # SOLO OR COLLABORATIVE
    # ════════════════════════════════════════════════════════════════════
    story.append(KeepTogether([
        section_box("Solo or Collaborative", styles),
        spacer(3),
        p(
            "Cortex works for one person. It also works for any number of people sharing a repository "
            "<i>(a shared folder of records everyone can add to)</i>. "
            "Everyone runs their own AI assistant against it and adds their entries. "
            "Everyone sees the full record. "
            "<b>The version control software handles the collaboration. The AI handles the scribing.</b>",
            styles
        ),
        p(
            "Each person can use a different AI. One uses Claude, another uses ChatGPT, another "
            "uses Qwen. Same folder. Same protocol. Same truth.",
            styles
        ),
    ]))

    use_cases = [
        ("A couple's shared health journal",    "Both partners log appointments, symptoms, and medications. One AI session each. Full shared picture."),
        ("A team's decision log",               "Every significant call recorded with context and rationale. No more 'why did we decide that?'"),
        ("A family's care record",              "Multiple family members logging care for an elderly parent. One repo, full history, any device."),
        ("A band's creative sessions",          "Lyrics, ideas, rehearsal notes, session recordings — all scribed and committed after every session."),
        ("A startup's retrospectives",          "Sprint reviews, incident post-mortems, hiring decisions — a permanent institutional memory."),
        ("A therapist's session notes",         "Private, portable, owned by the practitioner. No vendor lock-in, no cloud exposure."),
    ]

    uc_data = [[Paragraph("<b>Use Case</b>", styles["table_head"]),
                Paragraph("<b>What it looks like</b>", styles["table_head"])]]
    for title, desc in use_cases:
        uc_data.append([
            Paragraph(title, styles["table_cell_bold"]),
            Paragraph(desc,  styles["table_cell"]),
        ])

    uc_col = [55*mm, W_PAGE - 55*mm]
    uc_table = Table(uc_data, colWidths=uc_col)
    uc_table.setStyle(TableStyle([
        ("BACKGROUND",      (0,0), (-1,0),  HEAD_BG),
        ("ROWBACKGROUNDS",  (0,1), (-1,-1), [WHITE, STRIPE]),
        ("GRID",            (0,0), (-1,-1), 0.4, RULE),
        ("LEFTPADDING",     (0,0), (-1,-1), 4*mm),
        ("RIGHTPADDING",    (0,0), (-1,-1), 4*mm),
        ("TOPPADDING",      (0,0), (-1,-1), 3*mm),
        ("BOTTOMPADDING",   (0,0), (-1,-1), 3*mm),
        ("VALIGN",          (0,0), (-1,-1), "TOP"),
    ]))
    story.append(uc_table)
    story.append(spacer(3))

    # ════════════════════════════════════════════════════════════════════
    # WHAT IT COVERS
    # ════════════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(KeepTogether([
        section_box("What It Covers — 19 Templates", styles),
        spacer(3),
        p("Cortex ships with templates across every domain worth recording. Use what fits. Ignore what doesn't. Add your own.", styles),
    ]))

    templates = [
        ("Personal",    "Daily log",         "Dated record of the day — mood, events, reflections, energy."),
        ("Personal",    "Event",             "A specific episode worth capturing in detail."),
        ("Personal",    "Person",            "A record for someone in your life — history, context, relationship notes."),
        ("Personal",    "Theory / insight",  "A pattern or idea you've noticed that deserves its own file."),
        ("Health",      "Therapy session",   "Session notes — what was covered, what surfaced, what to carry forward."),
        ("Health",      "Medication",        "Drug, dose, schedule, effects, changes over time."),
        ("Health",      "Symptoms",          "Onset, severity, duration, triggers — a timestamped record."),
        ("Health",      "Appointment",       "Pre/post notes, questions asked, answers given, follow-ups."),
        ("Life admin",  "Finance",           "Expenses, decisions, budgets, income events."),
        ("Life admin",  "Inventory",         "What you own, where it is, condition, purchase date."),
        ("Life admin",  "Supplies",          "Consumables tracking — when to reorder, what ran out."),
        ("Life admin",  "Tasks",             "Action items with context, not just a to-do list."),
        ("Work",        "Work log",          "Daily work record — what was done, what's blocked, what matters."),
        ("Work",        "Project",           "Project context, goals, decisions, stakeholders, status."),
        ("Work",        "Career",            "Milestones, feedback, decisions, aspirations over time."),
        ("Creative",    "Idea",              "A single idea captured before it evaporates."),
        ("Creative",    "Creative session",  "A working session — what was made, what direction emerged."),
        ("Analytical",  "Analysis",          "A structured look across records — patterns, connections, findings."),
        ("Analytical",  "Review",            "A periodic review — what's changed, what's working, what isn't."),
    ]

    tmpl_data = [[
        Paragraph("<b>Category</b>",    styles["table_head"]),
        Paragraph("<b>Template</b>",    styles["table_head"]),
        Paragraph("<b>What it captures</b>", styles["table_head"]),
    ]]
    current_cat = None
    for cat, name, desc in templates:
        cat_label = cat if cat != current_cat else ""
        current_cat = cat
        tmpl_data.append([
            Paragraph(cat_label, styles["table_cell_bold"]),
            Paragraph(name,      styles["table_cell_bold"]),
            Paragraph(desc,      styles["table_cell"]),
        ])

    tmpl_cols = [28*mm, 36*mm, W_PAGE - 64*mm]
    tmpl_table = Table(tmpl_data, colWidths=tmpl_cols)

    # Alternating rows + category colour bands
    cat_indices = {"Personal": 1, "Health": 5, "Life admin": 9, "Work": 13, "Creative": 16, "Analytical": 18}
    row_styles = [
        ("BACKGROUND",    (0,0), (-1,0),  HEAD_BG),
        ("GRID",          (0,0), (-1,-1), 0.4, RULE),
        ("LEFTPADDING",   (0,0), (-1,-1), 4*mm),
        ("RIGHTPADDING",  (0,0), (-1,-1), 4*mm),
        ("TOPPADDING",    (0,0), (-1,-1), 2.5*mm),
        ("BOTTOMPADDING", (0,0), (-1,-1), 2.5*mm),
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, STRIPE]),
    ]
    tmpl_table.setStyle(TableStyle(row_styles))
    story.append(tmpl_table)
    story.append(spacer(3))

    # ════════════════════════════════════════════════════════════════════
    # WORKS WITH  +  CLOUD VS OFFLINE
    # ════════════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(KeepTogether([
        section_box("Works With Any Major AI — On Any Device", styles),
        spacer(3),
        p(
            "Cortex works with any major AI assistant <i>(Claude, ChatGPT, Gemini, and others)</i>. "
            "Switch between them any time — mid-session if you want. "
            "The protocol is the same everywhere. Your records folder is the source of truth, not the AI.",
            styles
        ),
    ]))

    agents = [
        ("Claude Code",     "Desktop CLI\n(command line)",  "Full tool use, auto-save, full protocol support."),
        ("Claude Desktop",  "Desktop app",                  "No command line needed. Add your folder as a project. Easiest desktop entry point."),
        ("Claude (mobile)", "iOS / Android",                "Via Claude project + a credentials file. Auto-session on every new chat."),
        ("ChatGPT (mobile)","iOS / Android",                "Via ChatGPT project + a credentials file. Same setup as Claude mobile."),
        ("Gemini CLI",      "Desktop CLI\n(command line)",  "Full protocol support."),
        ("OpenCode",        "Desktop CLI\n(command line)",  "Full protocol support."),
        ("Qwen Code",       "Desktop CLI\n(command line)",  "Full protocol support."),
        ("Ollama (local)",  "Any device",                   "Fully offline — runs on your own computer. Self-hosted storage. Nothing leaves the machine."),
    ]

    ag_data = [[
        Paragraph("<b>Agent</b>",    styles["table_head"]),
        Paragraph("<b>Platform</b>", styles["table_head"]),
        Paragraph("<b>Notes</b>",    styles["table_head"]),
    ]]
    for name, plat, note in agents:
        ag_data.append([
            Paragraph(name, styles["table_cell_bold"]),
            Paragraph(plat, styles["table_cell"]),
            Paragraph(note, styles["table_cell"]),
        ])

    ag_cols = [36*mm, 32*mm, W_PAGE - 68*mm]
    ag_table = Table(ag_data, colWidths=ag_cols)
    ag_table.setStyle(TableStyle([
        ("BACKGROUND",     (0,0), (-1,0),  HEAD_BG),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, STRIPE]),
        ("GRID",           (0,0), (-1,-1), 0.4, RULE),
        ("LEFTPADDING",    (0,0), (-1,-1), 4*mm),
        ("RIGHTPADDING",   (0,0), (-1,-1), 4*mm),
        ("TOPPADDING",     (0,0), (-1,-1), 2.5*mm),
        ("BOTTOMPADDING",  (0,0), (-1,-1), 2.5*mm),
        ("VALIGN",         (0,0), (-1,-1), "TOP"),
    ]))
    story.append(ag_table)
    story.append(spacer(3))

    # Gemini web note
    story.append(p(
        "<i>Note: Gemini web and mobile do not support the project + tool-calling flow "
        "required by Cortex. Use Claude or ChatGPT on mobile.</i>",
        styles, "body_muted"
    ))
    story.append(spacer(3))

    # Cloud vs Offline
    story.append(PageBreak())
    story.append(KeepTogether([
        section_box("Cloud vs Offline", styles),
        spacer(3),
    ]))

    cv_data = [[
        Paragraph("<b>Cloud (default)</b>",     styles["table_head"]),
        Paragraph("<b>Offline / self-hosted</b>", styles["table_head"]),
    ]]
    cloud_points = [
        "GitHub or GitLab <i>(secure online services for storing your records)</i>",
        "Claude, ChatGPT, Gemini, or any hosted AI assistant",
        "Five-minute setup — from template to first session",
        "Syncs across all your devices automatically",
        "Top-tier AI models — most reliable instruction-following",
        "<b>Tradeoff:</b> Your AI provider processes records under their privacy policy. Your online storage account can be subpoenaed.",
    ]
    offline_points = [
        "Your own computer or a private server you run yourself",
        "Ollama <i>(free software that runs AI models locally on your computer)</i>",
        "Nothing leaves your machine — ever",
        "Works with no internet connection at all",
        "No third-party AI provider. No legal exposure on your storage.",
        "<b>Tradeoff:</b> More technical to set up. Local AI models are less reliable at following instructions.",
    ]
    for cp, op in zip(cloud_points, offline_points):
        cv_data.append([
            Paragraph(f"\u2022\u2002{cp}", styles["body_sm"]),
            Paragraph(f"\u2022\u2002{op}", styles["body_sm"]),
        ])

    cv_cols = [W_PAGE/2, W_PAGE/2]
    cv_table = Table(cv_data, colWidths=cv_cols)
    cv_table.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (0,0),  colors.HexColor("#1d4ed8")),
        ("BACKGROUND",    (1,0), (1,0),  colors.HexColor("#166534")),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, STRIPE]),
        ("GRID",          (0,0), (-1,-1), 0.4, RULE),
        ("LEFTPADDING",   (0,0), (-1,-1), 4*mm),
        ("RIGHTPADDING",  (0,0), (-1,-1), 4*mm),
        ("TOPPADDING",    (0,0), (-1,-1), 2.5*mm),
        ("BOTTOMPADDING", (0,0), (-1,-1), 2.5*mm),
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
        ("LINEAFTER",     (0,0), (0,-1), 0.5, RULE),
    ]))
    story.append(cv_table)
    story.append(spacer(3))

    # ════════════════════════════════════════════════════════════════════
    # PRIVACY
    # ════════════════════════════════════════════════════════════════════
    story.append(KeepTogether([
        section_box("Privacy", styles),
        spacer(3),
    ]))

    privacy = [
        ("Cordfuse has zero access to your records",
         "No telemetry, no analytics, no data collection of any kind. The protocol is open source <i>(publicly readable code)</i> — you can see exactly what it does."),
        ("Your records folder is yours",
         "Private, portable, permanent. Every change is logged — even deleted files remain in the history. If you need true erasure, run the offline version."),
        ("Online storage accounts can be subpoenaed",
         "A private account on GitHub or GitLab is not beyond the reach of law enforcement. If this matters to you, run your own private server."),
        ("AI providers process what you send them",
         "When you use a hosted AI (Claude, ChatGPT, etc.), your records pass through their servers. Review their privacy policies. For maximum privacy, run Ollama locally on your own machine."),
    ]

    for title, body in privacy:
        priv_row = Table(
            [[Paragraph(f"<b>{title}</b>", styles["bold_lead"]),
              Paragraph(body, styles["body_sm"])]],
            colWidths=[52*mm, W_PAGE - 52*mm]
        )
        priv_row.setStyle(TableStyle([
            ("VALIGN",        (0,0), (-1,-1), "TOP"),
            ("LEFTPADDING",   (0,0), (-1,-1), 0),
            ("RIGHTPADDING",  (0,0), (-1,-1), 3*mm),
            ("TOPPADDING",    (0,0), (-1,-1), 1.5*mm),
            ("BOTTOMPADDING", (0,0), (-1,-1), 2.5*mm),
            ("LINEBELOW",     (0,0), (-1,-1), 0.4, RULE),
        ]))
        story.append(priv_row)

    story.append(spacer(3))

    # ════════════════════════════════════════════════════════════════════
    # GET STARTED
    # ════════════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(section_box("Get Started", styles))
    story.append(spacer(3))

    # Desktop + Mobile side by side
    desktop_steps = [
        "Click <b>Use this template</b> on GitHub <i>(a free online service for storing files)</i> and create a private folder for your records.",
        "Download it to your computer: <font face='Courier' size='9'>git clone git@github.com:you/your-repo.git</font>",
        "Open it in your AI agent <i>(command line assistant)</i>: <font face='Courier' size='9'>claude</font> / <font face='Courier' size='9'>gemini</font> / <font face='Courier' size='9'>opencode</font>",
        "Say hello.",
    ]
    mobile_steps = [
        "Create a records folder on GitHub from the Cortex template <i>(can be public at first — you'll lock it down at the end)</i>.",
        "Generate a GitHub Personal Access Token <i>(PAT — a secure password that lets the AI read and write your records)</i>.",
        "Create a small file called <b>CONNECT.md</b> with your folder address and PAT — this is your AI's key to your records.",
        "Create a Claude or ChatGPT project — paste the system prompt from <b>CORTEX-PROJECT.md</b> and upload your CONNECT.md as project knowledge <i>(a file the AI reads at the start of every chat)</i>.",
        "Open a new chat. The AI downloads your records folder and is ready.",
        "Go back to GitHub and set your records folder to private.",
    ]

    def numbered_list(items, styles):
        rows = []
        for i, item in enumerate(items, 1):
            rows.append([
                Paragraph(f"<b>{i}</b>", styles["step_num"]),
                Paragraph(item, styles["body_sm"]),
            ])
        t = Table(rows, colWidths=[7*mm, None])
        t.setStyle(TableStyle([
            ("VALIGN",        (0,0), (-1,-1), "TOP"),
            ("LEFTPADDING",   (0,0), (0,-1),  0),
            ("RIGHTPADDING",  (0,0), (-1,-1), 2*mm),
            ("TOPPADDING",    (0,0), (-1,-1), 1*mm),
            ("BOTTOMPADDING", (0,0), (-1,-1), 1.5*mm),
        ]))
        return t

    gs_col = (W_PAGE - 4*mm) / 2

    gs_head = Table(
        [[Paragraph("<b>Desktop</b>", styles["table_head"]),
          Paragraph("<b>Mobile (Claude or ChatGPT project)</b>", styles["table_head"])]],
        colWidths=[gs_col, gs_col]
    )
    gs_head.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (0,0),  colors.HexColor("#374151")),
        ("BACKGROUND",    (1,0), (1,0),  colors.HexColor("#374151")),
        ("LEFTPADDING",   (0,0), (-1,-1), 4*mm),
        ("RIGHTPADDING",  (0,0), (-1,-1), 4*mm),
        ("TOPPADDING",    (0,0), (-1,-1), 3*mm),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3*mm),
        ("LINEAFTER",     (0,0), (0,-1), 0.5, WHITE),
    ]))
    story.append(gs_head)

    gs_body = Table(
        [[numbered_list(desktop_steps, styles),
          numbered_list(mobile_steps,  styles)]],
        colWidths=[gs_col, gs_col]
    )
    gs_body.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), TAG_BG),
        ("LEFTPADDING",   (0,0), (-1,-1), 4*mm),
        ("RIGHTPADDING",  (0,0), (-1,-1), 4*mm),
        ("TOPPADDING",    (0,0), (-1,-1), 3*mm),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3*mm),
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
        ("LINEAFTER",     (0,0), (0,-1), 0.5, RULE),
        ("BOX",           (0,0), (-1,-1), 0.4, RULE),
    ]))
    story.append(gs_body)
    story.append(spacer(3))

    story.append(p(
        "<b>Returning sessions — desktop:</b> <font face='Courier' size='9'>cd your-repo &amp;&amp; claude</font> — say hello.<br/>"
        "<b>Returning sessions — mobile:</b> open a new chat in your Cortex project. The scribe clones the repo and picks up where you left off.",
        styles, "body_sm"
    ))

    story.append(spacer(3))

    # ════════════════════════════════════════════════════════════════════
    # GUARDRAILS NOTE
    # ════════════════════════════════════════════════════════════════════
    guard = Table(
        [[Paragraph(
            "<b>Guardrails</b>&nbsp;&nbsp; Cortex ships with <font face='Courier' size='9'>protocol/GUARDRAILS.md</font> — "
            "hard stops governing how the scribe behaves. They cover crisis situations, intent to harm, "
            "crime disclosure, child safety, and jailbreak attempts. "
            "The scribe will refuse to start if this file is missing. "
            "Cordfuse accepts zero liability if you remove or modify it.",
            styles["body_sm"]
        )]],
        colWidths=[W_PAGE]
    )
    guard.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), colors.HexColor("#fef9c3")),
        ("LEFTPADDING",   (0,0), (-1,-1), 5*mm),
        ("RIGHTPADDING",  (0,0), (-1,-1), 5*mm),
        ("TOPPADDING",    (0,0), (-1,-1), 3.5*mm),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3.5*mm),
        ("BOX",           (0,0), (-1,-1), 0.6, colors.HexColor("#ca8a04")),
    ]))
    story.append(guard)
    story.append(spacer(4))

    # ════════════════════════════════════════════════════════════════════
    # FOOTER
    # ════════════════════════════════════════════════════════════════════
    rule()
    footer = Table(
        [[
            Paragraph("github.com/cordfuse/cortex", styles["body_muted"]),
            Paragraph("MIT licence", styles["body_muted"]),
            Paragraph(
                "Nothing in Cortex constitutes medical, legal, or psychiatric advice.",
                ParagraphStyle("fr", fontName="Helvetica-Oblique", fontSize=8,
                               textColor=MUTED, alignment=TA_RIGHT)),
        ]],
        colWidths=[W_PAGE*0.35, W_PAGE*0.15, W_PAGE*0.5]
    )
    footer.setStyle(TableStyle([
        ("LINEABOVE",   (0,0), (-1,-1), 0.5, RULE),
        ("TOPPADDING",  (0,0), (-1,-1), 3*mm),
        ("LEFTPADDING", (0,0), (0,-1),  0),
        ("RIGHTPADDING",(2,0), (-1,-1), 0),
        ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(footer)

    doc.build(story)
    print(f"Written: {OUTPUT}")


if __name__ == "__main__":
    build()
