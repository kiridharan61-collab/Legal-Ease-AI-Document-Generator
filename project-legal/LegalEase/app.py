import os
import tempfile
from datetime import date
from pathlib import Path

import requests
import streamlit as st
from dotenv import load_dotenv

from utils.exporters import format_docx, format_pdf, format_txt
from utils.sanitize import sanitize_text

load_dotenv()

st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

DEFAULT_BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")


def apply_styles():
    st.markdown(
        """
        <style>
        .main-title {
            text-align: center;
            font-size: 42px;
            font-weight: 800;
            margin-bottom: 4px;
        }
        .subtitle {
            text-align: center;
            color: #9aa4b2;
            margin-bottom: 28px;
        }
        .preview {
            background: #111827;
            border: 1px solid #374151;
            border-radius: 12px;
            padding: 24px;
            height: 620px;
            overflow-y: auto;
            white-space: pre-wrap;
            font-family: Georgia, serif;
            line-height: 1.65;
        }
        .notice {
            padding: 12px 16px;
            border-radius: 10px;
            background: #1f2937;
            border-left: 4px solid #60a5fa;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def generate_document(
    backend_url: str,
    document_type: str,
    parties: str,
    terms: str,
    effective_date: str,
) -> str:
    response = requests.post(
        f"{backend_url.rstrip('/')}/generate",
        json={
            "document_type": document_type,
            "parties": parties,
            "terms": terms,
            "effective_date": effective_date,
        },
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["content"]


apply_styles()

st.markdown('<div class="main-title">⚖️ LegalEase</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">AI-powered legal document drafting, editing and export</div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Settings")
    backend_url = st.text_input("Backend URL", value=DEFAULT_BACKEND_URL)
    st.caption("FastAPI must be running before generation.")

    st.divider()
    st.subheader("Optional branding")
    logo = st.file_uploader(
        "Upload logo",
        type=["png", "jpg", "jpeg"],
        help="The logo is included in DOCX/PDF exports.",
    )

    st.divider()
    st.markdown(
        '<div class="notice">LegalEase creates document templates and is not a '
        'substitute for advice from a qualified lawyer.</div>',
        unsafe_allow_html=True,
    )

left, right = st.columns([0.9, 1.1], gap="large")

with left:
    st.subheader("Document details")

    document_type = st.selectbox(
        "Document Type",
        [
            "Employment Contract",
            "Non-Disclosure Agreement (NDA)",
            "Lease Agreement",
            "Service Agreement",
            "Freelance Work Contract",
            "Employment Offer Letter",
            "General Agreement",
            "Custom Legal Document",
        ],
    )

    custom_type = ""
    if document_type == "Custom Legal Document":
        custom_type = st.text_input("Enter document type")
        document_type = custom_type or document_type

    parties = st.text_area(
        "Parties Involved",
        placeholder=(
            "Example: Jane Doe (Service Provider), TechNova Inc. (Client)"
        ),
        height=120,
    )

    terms = st.text_area(
        "Terms & Conditions",
        placeholder=(
            "Use semicolons between terms.\n"
            "Payment within 30 days; Confidentiality must be maintained; "
            "Either party may terminate with 15 days notice"
        ),
        height=180,
    )

    effective_date = st.date_input(
        "Effective Date",
        value=date.today(),
    )

    if st.button("Generate Document", type="primary", use_container_width=True):
        if not parties.strip() or not terms.strip():
            st.error("Please enter the parties and at least one term.")
        else:
            try:
                with st.spinner("Generating your document..."):
                    content = generate_document(
                        backend_url,
                        document_type,
                        parties,
                        terms,
                        effective_date.isoformat(),
                    )
                st.session_state["document"] = content
                st.session_state["document_type"] = document_type
                st.session_state["terms"] = terms
                st.success("Document generated successfully.")
            except requests.RequestException as exc:
                detail = getattr(exc.response, "text", "") if exc.response else ""
                st.error(
                    f"Could not reach the backend. Check that FastAPI is running. "
                    f"{detail}"
                )
            except Exception as exc:
                st.error(f"Generation failed: {exc}")

with right:
    st.subheader("Document preview")

    if "document" not in st.session_state:
        st.info("Your generated document will appear here.")
    else:
        current = st.session_state["document"]

        edited = st.text_area(
            "Editable document",
            value=current,
            height=430,
            key="document_editor",
        )
        st.session_state["document"] = edited

        st.markdown("**Preview**")
        safe_html = (
            sanitize_text(edited)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\n", "<br>")
        )
        st.markdown(
            f'<div class="preview">{safe_html}</div>',
            unsafe_allow_html=True,
        )

        st.markdown("### Download")

        doc_type = st.session_state.get("document_type", "Legal Document")
        terms_value = st.session_state.get("terms", "")

        txt_bytes = format_txt(edited)
        docx_bytes = format_docx(
            edited,
            doc_type,
            terms=terms_value,
            logo_bytes=logo.getvalue() if logo else None,
        )

        logo_path = None
        if logo:
            suffix = Path(logo.name).suffix or ".png"
            temp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            temp.write(logo.getvalue())
            temp.close()
            logo_path = temp.name

        try:
            pdf_bytes = format_pdf(edited, doc_type, logo_path=logo_path)
        finally:
            if logo_path:
                try:
                    os.unlink(logo_path)
                except OSError:
                    pass

        base_name = "legalease_document"

        c1, c2, c3 = st.columns(3)
        with c1:
            st.download_button(
                "Download TXT",
                data=txt_bytes,
                file_name=f"{base_name}.txt",
                mime="text/plain",
                use_container_width=True,
            )
        with c2:
            st.download_button(
                "Download DOCX",
                data=docx_bytes,
                file_name=f"{base_name}.docx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "wordprocessingml.document"
                ),
                use_container_width=True,
            )
        with c3:
            st.download_button(
                "Download PDF",
                data=pdf_bytes,
                file_name=f"{base_name}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
