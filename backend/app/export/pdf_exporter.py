from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from xhtml2pdf import pisa

from app.config import settings
from app.models.icp import Icp
from app.models.lead import Lead

TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"

_env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)),
    autoescape=select_autoescape(["html"]),
)


class PdfExportError(Exception):
    pass


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "icp"


def render_lead_report(leads: list[Lead], icp: Icp, output_dir: Path | None = None) -> Path:
    output_dir = output_dir or settings.reports_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    by_grade = {"Hot": [], "Warm": [], "Cold": []}
    for lead in leads:
        by_grade.setdefault(lead.grade, []).append(lead)
    for grade_leads in by_grade.values():
        grade_leads.sort(key=lambda item: item.score, reverse=True)

    template = _env.get_template("lead_report.html")
    html = template.render(
        icp_name=icp.name,
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        total_leads=len(leads),
        hot_leads=by_grade["Hot"],
        warm_leads=by_grade["Warm"],
        cold_leads=by_grade["Cold"],
    )

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"{_slugify(icp.name)}_{timestamp}.pdf"
    output_path = output_dir / filename

    with output_path.open("wb") as f:
        result = pisa.CreatePDF(html, dest=f)

    if result.err:
        output_path.unlink(missing_ok=True)
        raise PdfExportError(f"Failed to render PDF report ({result.err} error(s))")

    return output_path
