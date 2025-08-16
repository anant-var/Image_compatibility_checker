import os
import uuid
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from config import CSP_RULES
from pathlib import Path
import tempfile

def generate_csp_report(features, format_info, output_dir="outputs/reports"):
    """
    Generates a CSP compatibility PDF report and saves it in output_dir.
    Returns the full path to the saved PDF.
    """
    # Ensure output directory exists
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Unique filename: timestamp + short UUID
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    short_uuid = uuid.uuid4().hex[:8]
    final_filename = f"compatibility_report_{timestamp}_{short_uuid}.pdf"
    final_path = output_dir / final_filename

    # Create temporary file for atomic write
    with tempfile.NamedTemporaryFile(
        suffix=".pdf", prefix="tmp_report_", dir=str(output_dir), delete=False
    ) as tmp:
        temp_path = Path(tmp.name)

    try:
        # Build PDF content
        doc = SimpleDocTemplate(str(temp_path), pagesize=LETTER)
        styles = getSampleStyleSheet()
        elements = []

        # Header
        elements.append(Paragraph("CSP Compatibility Report", styles["Title"]))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(
            "This report evaluates a virtual machine image based on extracted features for compatibility with major Cloud Service Providers (CSPs).",
            styles["Normal"]
        ))
        elements.append(Spacer(1, 20))

        # Feature Summary Table
        feature_table_data = [
            ["Feature", "Value"],
            ["Boot Partition Present", str(features.get("boot", False))],
            ["EFI Partition Present", str(features.get("efi", False))],
            ["Cloud-Init Detected", str(features.get("cloud_init", False))],
            ["Detected OS", features.get("os", "Unknown")],
            ["Image Format", format_info.get("format", "Unknown")],
            ["Virtual Size", format_info.get("virtual_size_human", "Unknown")],
            ["Actual Size", format_info.get("actual_size_human", "Unknown")],
            ["Cluster Size", str(format_info.get("cluster_size", "Unknown"))],
            ["Backing File", "None" if not format_info.get("backing_file") else str(format_info.get("backing_file"))],
            ["Dirty Flag", str(format_info.get("dirty_flag", False))],
            ["Refcount Bits", str(format_info.get("refcount-bits", "Unknown"))],
            ["Lazy Refcounts", str(format_info.get("lazy-refcounts", "Unknown"))],
            ["Corrupt", str(format_info.get("corrupt", "Unknown"))]
        ]

        feature_table = Table(feature_table_data, hAlign='LEFT', colWidths=[200, 280])
        feature_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#d3d3d3")),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ALIGN', (1, 1), (-1, -1), 'LEFT'),
        ]))

        elements.append(feature_table)
        elements.append(Spacer(1, 20))

        # Cloud-init Section
        elements.append(Paragraph("📄 Cloud-Init Details", styles["Heading2"]))
        if features.get("cloud_init", False):
            elements.append(Paragraph(
                "✅ Cloud-init detected. Enables automatic configuration of VMs in cloud platforms like AWS, GCP, and Azure.",
                styles["Normal"]
            ))
            found_paths = features.get("cloud_init_paths", [])
            if found_paths:
                elements.append(Paragraph("📁 Detected cloud-init paths:", styles["Normal"]))
                for path in found_paths:
                    elements.append(Paragraph(f"• {path}", styles["Code"]))
            else:
                elements.append(Paragraph(
                    "⚠️ Cloud-init presence detected, but no file paths were reported.",
                    styles["Normal"]
                ))
        else:
            elements.append(Paragraph(
                "❌ Cloud-init NOT detected. This may affect auto-configuration on AWS, GCP, Azure.",
                styles["Normal"]
            ))

        elements.append(Spacer(1, 24))

        # CSP Compatibility Scores
        elements.append(Paragraph("☁️ CSP Compatibility Scoring (out of 10)", styles["Heading2"]))
        elements.append(Spacer(1, 12))
        scoring_table_data = [["CSP", "Score", "Details"]]

        for csp, cfg in CSP_RULES.items():
            score = 0
            max_score = 0
            reasons = []

            img_format = format_info.get("format", "").lower()
            backing_file = format_info.get("backing_file")
            corrupt = format_info.get("corrupt", False)
            refcount_bits = format_info.get("refcount-bits")
            lazy_refcounts = format_info.get("lazy-refcounts")

            feature_values = {
                "bios_boot": features.get("boot", False),
                "uefi_boot": features.get("efi", False),
                "cloud_init": features.get("cloud_init", False),
                "format": img_format in cfg.get("accepted_formats", []),
                "no_backing_file": not backing_file,
                "not_corrupt": not corrupt,
                "refcount_bits": refcount_bits is not None and int(refcount_bits) <= 16,
                "lazy_refcounts": lazy_refcounts is True
            }

            # Hard requirements
            hard_reqs = cfg.get("requires", {})
            failed = False
            for key, required in hard_reqs.items():
                if feature_values.get(key, False) != required:
                    reasons.append(f"❌ Missing required: {key}")
                    failed = True
            if failed:
                scoring_table_data.append([csp, "0 / 10", "\n".join(reasons)])
                continue

            # Weighted scoring
            weights = cfg.get("score_weights", {})
            for key, weight in weights.items():
                max_score += weight
                if feature_values.get(key, False):
                    score += weight
                    reasons.append(f"✅ {key} (+{weight})")
                else:
                    reasons.append(f"❌ {key} (+0)")

            normalized = round((score / max_score) * 10, 2) if max_score else 0
            scoring_table_data.append([csp, f"{normalized} / 10", "\n".join(reasons)])

        # Render scoring table
        score_table = Table(scoring_table_data, colWidths=[150, 80, 250])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e0e0e0")),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.4, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ]))
        elements.append(score_table)

        # Build PDF
        doc.build(elements)

        # Atomic move to final file
        os.replace(str(temp_path), str(final_path))

        return str(final_path)  # return path for streamlit_app.py to use

    finally:
        if temp_path.exists():
            try:
                temp_path.unlink()
            except Exception:
                pass
