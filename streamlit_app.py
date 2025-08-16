import streamlit as st
from pathlib import Path
import os

# Import your project modules
from extractors.format_extractor import extract_image_format_info
from extractors.feature_extractor import extract_features
from reporters.csp_report import generate_csp_report
from converters.image_converter import convert_image_to_raw


# =======================
# Setup directories
# =======================
BASE_DIR = Path(__file__).parent.resolve()
UPLOAD_DIR = BASE_DIR / "uploads"
REPORT_DIR = BASE_DIR / "reports"
CONVERTED_DIR = BASE_DIR / "converted"

for d in [UPLOAD_DIR, REPORT_DIR, CONVERTED_DIR]:
    d.mkdir(parents=True, exist_ok=True)


# =======================
# Helper function
# =======================
def process_vm_image(image_path: Path):
    """Process VM image: extract info, convert if needed, extract features, generate PDF."""
    format_info = extract_image_format_info(image_path)

    if not format_info or format_info.get("error"):
        raise ValueError("❌ Failed to extract image format information.")

    # Convert to RAW if necessary
    if format_info.get("format") != "raw":
        st.info("Converting image to RAW format...")
        image_path = convert_image_to_raw(str(image_path), output_dir=CONVERTED_DIR)

    features = extract_features(str(image_path))

    # Generate CSP compatibility report
    pdf_path = generate_csp_report(features, format_info, output_dir=REPORT_DIR)

    return format_info, features, pdf_path


# =======================
# Streamlit UI
# =======================
st.set_page_config(page_title="VM Image Compatibility Checker", layout="wide")

st.title("🖥️ VM Image Compatibility Checker")
st.write("Upload a VM image to analyze and generate a Cloud Service Provider (CSP) compatibility report.")

uploaded_file = st.file_uploader(
    "Choose a VM image file",
    type=["qcow2", "vmdk", "img"]
)

if uploaded_file:
    # Save uploaded file
    file_path = UPLOAD_DIR / uploaded_file.name
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success(f"✅ File uploaded: {uploaded_file.name}")

    # Process image
    try:
        format_info, features, pdf_path = process_vm_image(file_path)

        # Show extracted info
        st.subheader("🔍 Extracted Information")
        st.json(format_info)
        st.json(features)

        # Report download
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="⬇️ Download CSP Report",
                data=f,
                file_name=os.path.basename(pdf_path),
                mime="application/pdf"
            )

        st.success("✅ Report generated successfully!")

    except Exception as e:
        st.error(f"⚠️ Error while processing image: {e}")
