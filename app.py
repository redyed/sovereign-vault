import streamlit as st
from fpdf import FPDF
from datetime import datetime, date
import hashlib

# -----------------------------------------------------------------------------
# CONFIGURATION & ASSETS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="The Sovereign Vault",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# COLOR PALETTE
COLOR_BG = "#0E1117"
COLOR_SIDEBAR = "#161B22"
COLOR_GOLD = "#D4AF37"
COLOR_TEXT = "#FAFAFA"
COLOR_ACCENT = "#FFD700"

# -----------------------------------------------------------------------------
# CSS STYLING (THEME OVERRIDE)
# -----------------------------------------------------------------------------
def inject_custom_css():
    st.markdown(
        f"""
        <style>
        /* MAIN BACKGROUND */
        .stApp {{
            background-color: {COLOR_BG};
            color: {COLOR_TEXT};
            font-family: 'Courier New', Courier, monospace;
        }}
        
        /* SIDEBAR BACKGROUND */
        section[data-testid="stSidebar"] {{
            background-color: {COLOR_SIDEBAR};
        }}

        /* HEADERS */
        h1, h2, h3, h4, h5, h6 {{
            color: {COLOR_GOLD} !important;
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            text-transform: uppercase;
            letter-spacing: 2px;
        }}

        /* INPUT LABELS */
        .stTextInput label, .stDateInput label, .stNumberInput label, .stSelectbox label {{
            color: {COLOR_ACCENT} !important;
            font-weight: bold;
        }}

        /* BUTTON STYLING - GOLD ACCENT (Including Download Buttons) */
        div.stButton > button, div.stDownloadButton > button {{
            background-color: {COLOR_GOLD} !important;
            color: #000000 !important;
            border-radius: 4px;
            border: 1px solid {COLOR_GOLD} !important;
            padding: 10px 24px;
            font-weight: bold;
            text-transform: uppercase;
            transition: all 0.3s ease;
            width: 100%;
        }}
        
        div.stButton > button:hover, div.stDownloadButton > button:hover {{
            background-color: #F8F8F8 !important;
            color: {COLOR_GOLD} !important;
            border-color: {COLOR_GOLD} !important;
            box-shadow: 0 0 15px rgba(212, 175, 55, 0.4);
        }}

        /* CHECKBOXES */
        .stCheckbox label {{
            color: {COLOR_TEXT};
        }}
        
        /* ERROR MESSAGE */
        .stAlert {{
            background-color: #330000;
            color: #FFcccc;
            border: 1px solid red;
        }}

        /* REMOVE STREAMLIT BRANDING */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        
        /* DIVIDER */
        hr {{
            border-top: 1px solid {COLOR_GOLD};
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# -----------------------------------------------------------------------------
# PDF GENERATION LOGIC
# -----------------------------------------------------------------------------
def create_certificate(data):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()

    # --- FONT LOGIC (SMART FALLBACK) ---
    # We attempt to load custom fonts. If files are missing, we fallback to Helvetica.
    
    font_main = "Helvetica"     # Default Standard Font
    font_label = "Helvetica"    # Default Standard Font
    label_style = "B"           # Bold for labels if using standard font
    
    try:
        # Attempt to load custom fonts (requires files in same directory)
        # Updated to match user filenames: font-regular.ttf, font-bold.ttf
        pdf.add_font('Montserrat', '', 'font-regular.ttf', uni=True)
        pdf.add_font('Montserrat', 'B', 'font-bold.ttf', uni=True)
        font_main = 'Montserrat'
        
        try:
            # Updated to match user filename: font-semi.ttf
            pdf.add_font('Montserrat-Semi', '', 'font-semi.ttf', uni=True)
            font_label = 'Montserrat-Semi'
            label_style = '' # Custom semi-bold font doesn't need 'B' style flag
        except:
            # If semi-bold missing, use Main Bold
            font_label = 'Montserrat'
            label_style = 'B'
            
    except:
        # If main fonts missing, we stay with Helvetica defaults
        # We silently handle this to prevent app crash
        pass

    # --- DESIGN ---
    # Gold Border
    pdf.set_line_width(1)
    pdf.set_draw_color(212, 175, 55) # Sovereign Gold
    pdf.rect(10, 10, 190, 277)

    # HEADER
    pdf.set_font(font_main, 'B', 30)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(20)
    pdf.cell(0, 10, "CERTIFICATE OF SOVEREIGNTY", align='C', ln=True)

    # SUBHEADER
    pdf.set_font(font_main, '', 12)
    pdf.set_text_color(100, 100, 100) # Grey
    pdf.cell(0, 10, "OFFICIAL CHAIN OF TITLE RECORD", align='C', ln=True)

    pdf.ln(20)

    # DATA FIELDS
    pdf.set_text_color(0, 0, 0)
    
    fields = [
        ("Artist:", data['artist']),
        ("Track Title:", data['track']),
        ("Date of Creation:", data['date']),
        ("BPM / Key:", f"{data['bpm']} BPM / {data['key']}"),
        ("Origin Status:", "Human Origin Verified" if data['human_origin'] else "Hybrid/AI Assisted"),
        ("Primary Tools:", data['tools'])
    ]

    for label, value in fields:
        # LABEL
        pdf.set_font(font_label, label_style, 12) 
        pdf.cell(50, 10, label, border=0)
        
        # VALUE
        pdf.set_font(font_main, '', 12)
        pdf.cell(0, 10, str(value), border=0, ln=True)

    pdf.ln(10)
    
    # DIVIDER LINE
    pdf.set_draw_color(200, 200, 200)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(10)

    # METADATA BOX
    pdf.set_font(font_main, '', 10)
    pdf.set_text_color(80, 80, 80)
    pdf.multi_cell(0, 8, f"METADATA HASH:\n{data['meta_string']}", align='C')

    # SEAL IMAGE (Safely ignored if missing)
    try:
        pdf.image("seal.png", x=85, y=230, w=40)
    except:
        pass

    return bytes(pdf.output())

# -----------------------------------------------------------------------------
# VIEW: AUTHENTICATED APP
# -----------------------------------------------------------------------------
def authenticated_app():
    # SIDEBAR
    with st.sidebar:
        st.title("NOETIC INPUT")
        st.markdown("---")
        artist = st.text_input("Artist Name", value="Unknown Artist")
        track = st.text_input("Track Title", value="Untitled No. 1")
        bpm = st.number_input("BPM", min_value=60, max_value=300, value=120)
        track_key = st.text_input("Musical Key", value="C Major")
        reg_date = st.date_input("Registration Date", date.today())
        
        st.markdown("### 🔒 SECURE VAULT")
        st.caption("All entries are immutable upon generation.")
        
        st.markdown("---")
        if st.button("LOGOUT"):
            st.session_state['authenticated'] = False
            st.rerun()

    # MAIN AREA
    st.title("THE SOVEREIGN VAULT")
    st.markdown(f"**PROTOCOL:** ESTABLISHING TRACK LINEAGE")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("HUMAN ORIGIN")
        st.markdown("Check all elements created by biological cognition:")
        h_lyrics = st.checkbox("Lyrics (Written by Human)")
        h_melody = st.checkbox("Melody (Composed by Human)")
        h_prod = st.checkbox("Production (Arranged by Human)")

    with col2:
        st.subheader("SYNTHETIC ASSISTANCE")
        st.markdown("Select AI models utilized in the workflow:")
        ai_tool = st.selectbox(
            "Primary AI Framework",
            ["None", "Suno", "Udio", "RVC", "Stable Audio", "Custom Model"]
        )
        ai_intensity = st.slider("AI Influence %", 0, 100, 0)

    # LOGIC GENERATION
    st.markdown("---")
    
    # Determine Class
    if ai_tool == "None" and h_lyrics and h_melody and h_prod:
        src_class = "BIO-ORGANIC"
        rights = "100%"
        is_human_verified = True
    elif ai_tool != "None" and (not h_lyrics and not h_melody):
        src_class = "SYNTHETIC-GENERATIVE"
        rights = "PROMPT-RIGHTS-ONLY"
        is_human_verified = False
    else:
        src_class = "CYBORG-HYBRID"
        rights = f"{100 - int(ai_intensity/2)}%"
        is_human_verified = False

    # Generate Hash/String
    raw_data = f"{artist}{track}{bpm}{src_class}".encode()
    unique_hash = hashlib.sha256(raw_data).hexdigest()[:16].upper()
    
    meta_string = (
        f"[ID: {unique_hash}] "
        f"[SRC: {src_class}] "
        f"[RIGHTS: {rights}] "
        f"[BPM: {bpm}] "
        f"[TOOL: {ai_tool.upper()}]"
    )

    # DISPLAY
    st.markdown(f"### GENERATED METADATA")
    st.code(meta_string, language="json")

    # ACTION
    if st.button("MINT CERTIFICATE OF SOVEREIGNTY"):
        
        # Prepare Data - Updated to match new create_certificate keys
        data = {
            "artist": artist,
            "track": track,
            "bpm": bpm,
            "key": track_key,
            "date": reg_date,
            "meta_string": meta_string,
            # Mapped fields for new PDF function
            "human_origin": is_human_verified,
            "tools": ai_tool
        }
        
        # Generate PDF
        pdf_bytes = create_certificate(data)
        
        st.success("METADATA LOCKED. CERTIFICATE GENERATED.")
        
        # Download Button
        st.download_button(
            label="DOWNLOAD OFFICIAL PDF",
            data=pdf_bytes,
            file_name=f"{artist}_{track}_Certificate.pdf",
            mime="application/pdf"
        )

# -----------------------------------------------------------------------------
# VIEW: LOGIN SCREEN
# -----------------------------------------------------------------------------
def login_screen():
    # Centering mechanism
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(f"<h1 style='text-align: center;'>THE GATEKEEPER</h1>", unsafe_allow_html=True)
        st.markdown("<div style='text-align: center; color: #888;'>AUTHENTICATION REQUIRED</div>", unsafe_allow_html=True)
        st.markdown("---")
        
        password = st.text_input("SOVEREIGN ACCESS KEY", type="password")
        
        if st.button("INITIATE PROTOCOL"):
            if password == "ARCHITECT2025":
                st.session_state['authenticated'] = True
                st.rerun()
            else:
                st.error("⚠ ACCESS DENIED. Restricted to Sovereign Academy Members.")

# -----------------------------------------------------------------------------
# MAIN CONTROLLER
# -----------------------------------------------------------------------------
def main():
    inject_custom_css()
    
    # Initialize Session State
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    
    # Routing
    if not st.session_state['authenticated']:
        login_screen()
    else:
        authenticated_app()

if __name__ == "__main__":
    main()
