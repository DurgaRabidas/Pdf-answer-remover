import streamlit as st
import pymupdf  # PyMuPDF

st.set_page_config(page_title="Advanced PDF Answer Remover", page_icon="📝", layout="wide")

st.title("📝 Advanced Blank Exam PDF Generator")
st.write("Remove ticks, drawing layers, and specific typed text/answers from past papers.")

# Sidebar Settings
st.sidebar.header("🔧 Cleaning Controls")
remove_shapes = st.sidebar.checkbox("Remove Vector Drawings & Ticks", value=True, 
                                    help="Deletes digital tick marks, checkboxes, and drawn lines.")

text_redaction = st.sidebar.checkbox("Erase Content by Keywords", value=True,
                                     help="Finds specific words and whites out the text next to them.")

# Custom Keywords Input
keywords_input = st.sidebar.text_input(
    "Keywords to target (comma-separated):", 
    value="Answer:, Correct Option:, [Ans], Choice:"
)

# File Uploader
uploaded_file = st.file_uploader("Choose a PDF question paper", type=["pdf"])

if uploaded_file is not None:
    pdf_bytes = uploaded_file.read()
    
    if st.button("🚀 Process & Clean PDF"):
        with st.spinner("Analyzing and scrubbing your exam paper..."):
            # Open PDF
            doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
            keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]
            
            for page in doc:
                # --- PHASE 1: KEYWORD TEXT MATCHING & WHITEOUT ---
                if text_redaction and keywords:
                    for keyword in keywords:
                        # Find all instances of the keyword on the page
                        text_instances = page.search_for(keyword)
                        
                        for rect in text_instances:
                            # Create an extended box to cover the answer text to the right of the keyword
                            # We extend the right coordinate (x1) by 150 points to catch the answer option
                            redact_rect = pymupdf.Rect(rect.x0, rect.y0, rect.x1 + 150, rect.y1)
                            
                            # Add a redaction zone with a solid white fill so it blends into the page background
                            page.add_redact_annot(
                                redact_rect, 
                                fill=(1, 1, 1) # RGB for White
                            )
                    
                    # Apply text whiteouts
                    page.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE, graphics=pymupdf.PDF_REDACT_LINE_ART_NONE)

                # --- PHASE 2: VECTOR SHAPE & TICK REMOVAL ---
                if remove_shapes:
                    page.add_redact_annot(page.rect)
                    page.apply_redactions(
                        images=pymupdf.PDF_REDACT_IMAGE_NONE,       # Keeps photos/diagrams
                        graphics=pymupdf.PDF_REDACT_LINE_ART_REMOVE # Wipes digital checkboxes/drawings
                    )

            # Compile the clean document
            output_bytes = doc.tobytes(garbage=3, deflate=True)
            doc.close()
            
            st.success("🎉 Processing complete! Your blank test paper is ready.")
            
            # Download Action
            st.download_button(
                label="📥 Download Blank B&W PDF",
                data=output_bytes,
                file_name="blank_practice_paper.pdf",
                mime="application/pdf"
            )
