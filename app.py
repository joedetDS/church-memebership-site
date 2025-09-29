# app.py
import streamlit as st
import datetime
import base64
import os
import io
from PIL import Image
import streamlit.components.v1 as components

# -----------------------
# Configuration
# -----------------------
PASSPORT_MAX_BYTES = 300 * 1024  # 300 KB
LOGO_FILENAME = "logo.png"  # must exist in the same folder as app.py

# -----------------------
# Session state init
# -----------------------
if 'member_count' not in st.session_state:
    st.session_state.member_count = 0
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
    st.session_state.data = {}

# -----------------------
# Helpers
# -----------------------
def get_next_id():
    """Generate next unique ID for members."""
    st.session_state.member_count += 1
    return f"GWGM{st.session_state.member_count:03d}"

def read_logo_base64(filename=LOGO_FILENAME):
    """Read logo file in current directory and return (mime, base64) or (None, None)."""
    try:
        if os.path.exists(filename):
            with open(filename, "rb") as f:
                b = f.read()
            if b:
                return "image/png", base64.b64encode(b).decode("utf-8")
    except Exception:
        pass
    return None, None

def validate_image_bytes(file_bytes):
    """Optionally validate image bytes (PIL) and return True if valid image."""
    try:
        Image.open(io.BytesIO(file_bytes)).verify()
        return True
    except Exception:
        return False

# -----------------------
# Form view
# -----------------------
if not st.session_state.submitted:
    st.title("GraciousWord Global Mission Membership Form")

    with st.form(key="membership_form"):
        col1, col2 = st.columns(2)
        with col1:
            passport_file = st.file_uploader(
                "Upload Passport Photo (Drag and drop • Limit 300KB • JPG/JPEG/PNG)",
                type=["jpg", "jpeg", "png"],
                accept_multiple_files=False
            )
            name = st.text_input("Name", max_chars=100)
            dob = st.date_input("Date of Birth", min_value=datetime.date(1900, 1, 1), max_value=datetime.date.today())
            gender = st.radio("Gender", ["Male", "Female"])
            phone = st.text_input("Phone / WhatsApp Number", max_chars=20)

        with col2:
            address = st.text_area("Residential Address", max_chars=200)
            occupation = st.text_input("Occupation", max_chars=100)
            branch = st.selectbox("Branch Affiliation", ["Uyo", "Aksu", "Eket"])
            position = st.selectbox("Position Held", ["Pastor", "Evangelist", "Deacon", "Deaconess", "Unit Head", "Worker", "Member"])
            motivation = st.text_area("What has drawn you to join GraciousWord Global Mission, and how do you hope to grow in your faith through this family?", max_chars=500)

        submit_button = st.form_submit_button("Submit")

        if submit_button:
            # Basic validations
            error = None
            if passport_file is None:
                error = "Please upload a passport photo."
            elif passport_file.size > PASSPORT_MAX_BYTES:
                error = "Passport photo size must not exceed 300KB."
            elif not name.strip():
                error = "Please enter your name."
            elif not phone.strip():
                error = "Please enter your phone/WhatsApp number."
            elif not address.strip():
                error = "Please enter your residential address."
            elif not occupation.strip():
                error = "Please enter your occupation."
            # optional more validation: image sanity check
            if error is None:
                try:
                    pb = passport_file.getvalue()
                    if not validate_image_bytes(pb):
                        error = "Uploaded passport is not a valid image file."
                except Exception:
                    error = "Failed to read uploaded passport file."

            if error:
                st.error(error)
            else:
                # Save the minimal data required for ID
                st.session_state.data = {
                    'unique_id': get_next_id(),
                    'name': name.strip(),
                    'gender': gender,
                    'branch': branch,
                    'position': position,
                    'passport_bytes': pb,
                    'passport_type': passport_file.type
                }
                st.session_state.submitted = True
                st.experimental_rerun()

# -----------------------
# ID Card view
# -----------------------
else:
    data = st.session_state.data
    st.title("Your GraciousWord Global Mission ID Card")

    # Prepare passport image base64
    passport_base64 = ""
    if data.get('passport_bytes'):
        passport_base64 = base64.b64encode(data['passport_bytes']).decode("utf-8")

    # Load logo from current working directory as 'logo.png'
    logo_mime, logo_base64 = read_logo_base64(LOGO_FILENAME)
    if not logo_base64:
        # If not available, logo_mime and logo_base64 are None; we simply won't show logo.
        logo_mime = "image/png"
        logo_base64 = ""

    # Build the HTML to render
    html_content = f"""
    <style>
    .id-card {{
        border: 2px solid #007BFF;
        border-radius: 10px;
        padding: 15px;
        background-color: #F8F9FA;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        max-width: 640px;
        margin: 0 auto;
        width: 92%;
    }}
    .id-card .header {{
        display:flex;
        align-items:center;
        gap:12px;
        margin-bottom:10px;
    }}
    .id-card .header img.logo {{
        width:80px;
        height:auto;
        border-radius:8px;
        object-fit:contain;
        border: 1px solid rgba(0,0,0,0.05);
        background: white;
        padding: 4px;
    }}
    .id-card h3 {{
        color: #007BFF;
        margin: 0;
        font-size: 22px;
    }}
    .id-card .layout {{
        display: flex;
        gap: 15px;
        align-items: flex-start;
    }}
    .id-card .photo {{
        flex: 0 0 150px;
    }}
    .id-card img.passport {{
        width: 150px;
        height: auto;
        border: 1px solid #ccc;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }}
    .id-card .text {{
        font-size: 16px;
        line-height: 1.5;
        color: #333;
        flex: 1;
    }}
    .id-card .text p {{
        margin: 5px 0;
        border-bottom: 1px solid #eee;
        padding-bottom: 5px;
    }}
    .id-card .text p:last-child {{
        border-bottom: none;
    }}
    @media (max-width: 600px) {{
        .id-card .layout {{
            flex-direction: column;
            align-items: center;
            text-align: center;
        }}
        .id-card .photo {{
            flex: 0 0 120px;
        }}
        .id-card img.passport {{
            width: 120px;
        }}
        .id-card .text {{
            font-size: 14px;
        }}
        .id-card h3 {{
            font-size: 20px;
        }}
        .id-card {{
            padding: 10px;
        }}
    }}
    </style>

    <div class="id-card">
        <div class="header">
            {f'<img class="logo" src="data:{logo_mime};base64,{logo_base64}" alt="Church Logo">' if logo_base64 else ''}
            <h3>GraciousWord Global Mission ID Card</h3>
        </div>

        <div class="layout">
            <div class="photo">
                {'<img class="passport" src="data:' + data['passport_type'] + ';base64,' + passport_base64 + '" alt="Passport Photo">' if data.get('passport_bytes') else '<p style="text-align: center; color: #888;">No passport photo uploaded</p>'}
            </div>

            <div class="text">
                <p><strong>Unique ID:</strong> {data.get('unique_id', 'N/A')}</p>
                <p><strong>Name:</strong> {data.get('name', 'Not provided')}</p>
                <p><strong>Gender:</strong> {data.get('gender', 'Not provided')}</p>
                <p><strong>Branch:</strong> {data.get('branch', 'Not provided')}</p>
                <p><strong>Position:</strong> {data.get('position', 'Not provided')}</p>
            </div>
        </div>
    </div>
    """

    # Render using components.html so the raw HTML/CSS is interpreted
    # Adjust height if the card gets clipped in your environment
    components.html(html_content, height=520, scrolling=True)

    st.markdown("")
    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("Create another ID"):
            st.session_state.submitted = False
            st.experimental_rerun()
    with col2:
        if st.button("Reset member counter"):
            st.session_state.member_count = 0
            st.success("Member counter reset to 0.")
