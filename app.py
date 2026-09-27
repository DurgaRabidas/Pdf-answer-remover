import streamlit as st
import pymupdf  # PyMuPDF

st.set_page_config(page_title="Advanced PDF Answer Remover", page_icon="📝", layout="wide")

st.title("📝 Advanced Blank Exam PDF Generator")
st.write("If answers aren't disappearing, adjust the keyword or the eraser width below.")

# Sidebar Settings
st.sidebar.header("🔧 Cleaning Controls")
remove_shapes = st.sidebar.checkbox("Remove Vector Drawings & Ticks", value=True)
text_redaction = st.sidebar.checkbox("Erase Content by Keywords", value=True)

# Custom Keywords Input
keywords_input = st.sidebar.text_input(
    "Keywords to target (case-insensitive, comma-separated):", 
    value="answer, option, ans, key"
)

# Eraser Width Control
eraser_width = st.sidebar.slider(
    "Eraser Width (How far right to erase the answer)", 
    min_value=50, max_value=500, value=200, step=10
)

# Debug Mode
debug_mode = st.sidebar.checkbox("Debug Mode (Show red boxes instead of whiter out)", value=False)

# File Uploader
uploaded_file = st.file_uploader("Choose a PDF question paper", type=["pdf"])

if uploaded_file is not None:
    pdf_bytes = uploaded_file.read()
    
    if st.button("🚀 Process & Clean PDF"):
        with st.spinner("Analyzing and scrubbing your exam paper..."):
            doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
            
            # Clean up keywords and convert to lowercase for better matching
            keywords = [k.strip().lower() for k in keywords_input.split(",") if k.strip()]
            
            # Check if the PDF has actual text layers
            has_text = False
            
            for page in doc:
                # --- PHASE 1: KEYWORD TEXT MATCHING ---
                if text_redaction and keywords:
                    # Get all text blocks on the page
                    text_page = page.get_text("words") # returns list of tuples: (x0, y0, x1, y1, "word", ...)
                    
                    if text_page:
                        has_text = True
                    
                    for word_meta in text_page:
                        word_text = word_meta[4].lower()
                        
                        # Check if this word matches any of our keywords
                        if any(kw in word_text for kw in keywords):
                            # Get coordinates of the matching word
                            x0, y0, x1, y1 = word_meta[0], word_meta[1], word_meta[2], word_meta[3]
                            
                            # Create a rectangle extending to the right to cover the answer
                            # If debug mode is active, we use Red so you can see where it hits
                            fill_color = (1, 0, 0) if debug_mode else (1, 1, 1)
                            
                            redact_rect = pymupdf.Rect(x0, y0 - 2, x1 + eraser_width, y1 + 2)
                            page.add_redact_annot(redact_rect, fill=fill_color)
                    
                    # Apply the text whiteout/redactions
                    page.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE, graphics=pymupdf.PDF_REDACT_LINE_ART_NONE)

                # --- PHASE 2: SHAPE & TICK REMOVAL ---
                if remove_shapes:
                    page.add_redact_annot(page.rect)
                    page.apply_redactions(
                        images=pymupdf.PDF_REDACT_IMAGE_NONE,
                        graphics=pymupdf.PDF_REDACT_LINE_ART_REMOVE
                    )

            # Compile document
            output_bytes = doc.tobytes(garbage=3, deflate=True)
            doc.close()
            
            # Warning helper if the PDF appears to be a scanned image
            if not has_text and text_redaction:
                st.warning("⚠️ This PDF looks like a scanned image or photo. Digital text keywords cannot be read automatically. Try relying on 'Remove Vector Drawings & Ticks' instead.")
            else:
                st.success("🎉 Processing complete!")
            
            # Download Action
            st.download_button(
                label="📥 Download Blank PDF",
                data=output_bytes,
                file_name="blank_practice_paper.pdf",
                mime="application/pdf"
            )
