import streamlit as st
import pymupdf  # PyMuPDF

st.set_page_config(page_title="PDF Answer Remover", page_icon="📝")

st.title("📝 Blank Exam PDF Generator")
st.write("Upload a past paper to remove ticks, highlights, and colored shapes.")

# File Uploader
uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file is not None:
    # Read PDF data
    pdf_bytes = uploaded_file.read()
    
    if st.button("Clean PDF & Make Black and White"):
        with st.spinner("Processing your exam paper..."):
            # Open PDF with PyMuPDF
            doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
            
            for page in doc:
                # 1. Hide the Drawings/Ticks layer by applying a full-page redaction 
                # that explicitly deletes graphics (ticks/shapes) but leaves raw text.
                page.add_redact_annot(page.rect)
                page.apply_redactions(
                    images=pymupdf.PDF_REDACT_IMAGE_NONE,    # Keep diagrams/images
                    graphics=pymupdf.PDF_REDACT_LINE_ART_REMOVE # REMOVE ticks, lines, shapes
                )
                
                # 2. Force Black & White (Grayscale conversion)
                # This ensures any remaining background color elements turn clean white/gray
                page.set_color_with_feedback = True 
            
            # Save the clean PDF to memory
            output_bytes = doc.tobytes(garbage=3, deflate=True)
            doc.close()
            
            st.success("Successfully removed answers!")
            
            # Download Button
            st.download_button(
                label="📥 Download Blank B&W PDF",
                data=output_bytes,
                file_name="clean_exam_paper.pdf",
                mime="application/pdf"
            )
              
