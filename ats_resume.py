from __future__ import annotations
import argparse
import html
import json
import re
import sqlite3
import unicodedata
from pathlib import Path
from typing import Any
from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", value).strip().lower()


TRACKS = {'tecnologia': {'terms': ['tecnologia', 'suporte', 'ti', 'informatica', 'sistema', 'cyber', 'seguranca'], 'summary': '', 'order': []}, 'administrativo': {'terms': ['administrativo', 'backoffice', 'planilha', 'documento', 'operacional', 'relatorio'], 'summary': '', 'order': []}, 'comercial': {'terms': ['venda', 'comercial', 'prospeccao', 'negociacao', 'lead', 'meta'], 'summary': '', 'order': []}, 'atendimento': {'terms': ['atendimento', 'cliente', 'sac', 'chat', 'whatsapp', 'telemarketing'], 'summary': '', 'order': []}}


def choose_track(job_text: str) -> str:
    normalized = normalize(job_text)
    scores = {name: sum(1 for term in cfg["terms"] if term in normalized) for name, cfg in TRACKS.items()}
    return max(scores, key=scores.get) if max(scores.values()) > 0 else "atendimento"


def paragraph(text: str, style: ParagraphStyle) -> Paragraph:
    text = text.replace("–", "-").replace("—", "-").replace("‑", "-")
    return Paragraph(html.escape(text), style)


def rich_paragraph(text: str, style: ParagraphStyle) -> Paragraph:
    text = text.replace("–", "-").replace("—", "-").replace("‑", "-")
    return Paragraph(text, style)


def ats_section(title: str, style: ParagraphStyle) -> Table:
    table = Table([[Paragraph(html.escape(title.upper()), style)]], colWidths=[184 * mm])
    table.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 1.0 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.0 * mm),
        ("LINEBELOW", (0, 0), (-1, -1), 0.45, colors.HexColor("#777777")),
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
    ]))
    return table


def build_pdf(job: sqlite3.Row, candidate: dict[str, Any], target: Path, font_size: float = 9.2) -> None:
    styles = getSampleStyleSheet()
    black = colors.HexColor("#111111")
    gray = colors.HexColor("#555555")
    body = ParagraphStyle(
        "ats_body", parent=styles["BodyText"], fontName="Helvetica", fontSize=font_size,
        leading=font_size + 2.0, textColor=black, alignment=TA_LEFT, spaceAfter=1.0 * mm,
    )
    small = ParagraphStyle(
        "ats_small", parent=body, fontSize=font_size - 0.15, leading=font_size + 1.65,
        spaceAfter=0.45 * mm,
    )
    bullet = ParagraphStyle(
        "ats_bullet", parent=small, leftIndent=3.4 * mm, firstLineIndent=-2.6 * mm,
        bulletIndent=0, spaceAfter=0.35 * mm,
    )
    heading = ParagraphStyle(
        "ats_heading", parent=body, fontName="Helvetica-Bold", fontSize=10.2,
        leading=12, textColor=black, spaceBefore=2.0 * mm, spaceAfter=0,
    )
    name_style = ParagraphStyle(
        "ats_name", parent=body, fontName="Helvetica-Bold", fontSize=17.5,
        leading=20, alignment=TA_LEFT, textColor=black, spaceAfter=0.7 * mm,
    )
    contact_style = ParagraphStyle(
        "ats_contact", parent=small, fontSize=8.6, leading=10.5,
        alignment=TA_LEFT, textColor=gray, spaceAfter=1.4 * mm,
    )
    experience_style = ParagraphStyle(
        "ats_experience", parent=body, fontName="Helvetica-Bold", fontSize=font_size,
        leading=font_size + 2, spaceAfter=0.2 * mm,
    )

    job_text = f"{job['title']} {job['description']}"
    track_name = choose_track(job_text)
    track = TRACKS[track_name]
    summary_override = job.get("summary_override") if isinstance(job, dict) else None
    professional_summary = summary_override or candidate.get("resumos", {}).get(track_name, candidate.get("resumo", ""))
    experiences_by_id = {exp["id"]: exp for exp in candidate["experiencias"]}
    order = candidate.get("ordem_experiencias", {}).get(track_name, list(experiences_by_id))
    experiences = [experiences_by_id[item] for item in order if item in experiences_by_id]

    story = [
        paragraph(candidate["nome_completo"], name_style),
        paragraph(f"{candidate['telefone']}  |  {candidate['email']}  |  {candidate.get("localidade", "Localidade não informada")}", contact_style),
        HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#777777"), spaceBefore=0, spaceAfter=1.0 * mm),
        ats_section("Resumo profissional", heading),
        Spacer(1, 0.9 * mm),
        paragraph(professional_summary, body),
        ats_section("Experiência profissional", heading),
        Spacer(1, 0.9 * mm),
    ]

    for exp in experiences:
        story.append(paragraph(exp["empresa"], experience_style))
        story.append(rich_paragraph(f"<b>{html.escape(exp['cargo'])}</b>", small))
        for activity in exp["atividades"][:3]:
            story.append(Paragraph(html.escape(activity), bullet, bulletText="-"))
        story.append(Spacer(1, 0.55 * mm))

    story.extend([ats_section("Competências técnicas", heading), Spacer(1, 0.9 * mm)])
    for label, description in [("Competências declaradas", ", ".join(candidate.get("competencias", [])))]:
        story.append(rich_paragraph(f"<b>{html.escape(label)}:</b> {html.escape(description)}", small))

    story.extend([
        ats_section("Formação acadêmica", heading),
        Spacer(1, 0.9 * mm),
        rich_paragraph(f"<b>{html.escape(candidate['formacao'])}</b> - {html.escape(candidate['situacao_formacao'])}<br/>{html.escape(candidate['ensino'])}", small),
        ats_section("Cursos complementares", heading),
        Spacer(1, 0.9 * mm),
        paragraph(" | ".join(candidate["cursos"]), small),
        ats_section("Idiomas", heading),
        Spacer(1, 0.9 * mm),
        paragraph(" | ".join(candidate.get("idiomas", [])), small),
    ])

    target.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(target), pagesize=A4, leftMargin=13 * mm, rightMargin=13 * mm,
        topMargin=10 * mm, bottomMargin=9 * mm,
        title=f"{candidate['nome_arquivos']} - {job['cargo']}", author=candidate["nome_completo"],
    )
    doc.build(story)

def main():
    parser=argparse.ArgumentParser(description="Gera PDF ATS com dados declarados pelo candidato.")
    parser.add_argument("--candidate",required=True,type=Path)
    parser.add_argument("--job",required=True,type=Path)
    parser.add_argument("--output",type=Path,default=Path("generated/CV.pdf"))
    args=parser.parse_args()
    candidate=json.loads(args.candidate.read_text(encoding="utf-8"))
    job=json.loads(args.job.read_text(encoding="utf-8"))
    for size in [9.2,8.55]:
        build_pdf(job,candidate,args.output,size)
        if len(PdfReader(args.output).pages)==1: break
    print(args.output)

if __name__=="__main__": main()
