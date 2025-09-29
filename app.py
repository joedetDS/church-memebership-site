import streamlit as st
import datetime
import base64
from PIL import Image
import io

# Initialize session state for counter and submission
if 'member_count' not in st.session_state:
    st.session_state.member_count = 0
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
    st.session_state.data = {}

# Function to generate unique ID
def get_next_id():
    st.session_state.member_count += 1
    return f"GWGM{st.session_state.member_count:03d}"

if not st.session_state.submitted:
    st.title("GraciousWord Global Mission Membership Form")
    
    with st.form(key="membership_form"):
        col1, col2 = st.columns(2)
        with col1:
            passport_file = st.file_uploader(
                "Upload Passport Photo (Limit 300KB • JPG, JPEG, PNG)", 
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
            # Optional logo uploader (this is where the logo is provided)
            logo_file = st.file_uploader(
                "Optional: Upload Organization Logo (PNG with transparency recommended)",
                type=["png", "jpg", "jpeg"], accept_multiple_files=False, key="logo_uploader"
            )
        
        submit_button = st.form_submit_button("Submit")
        
        if submit_button:
            if passport_file is None:
                st.error("Please upload a passport photo.")
            elif passport_file.size > 300 * 1024:
                st.error("Passport photo size must not exceed 300KB.")
            elif not name.strip():
                st.error("Please enter your name.")
            elif not phone.strip():
                st.error("Please enter your phone/WhatsApp number.")
            elif not address.strip():
                st.error("Please enter your residential address.")
            elif not occupation.strip():
                st.error("Please enter your occupation.")
            elif branch == "":
                st.error("Please select a branch affiliation.")
            elif position == "":
                st.error("Please select a position held.")
            else:
                # store data including logo if provided
                st.session_state.data = {
                    'unique_id': get_next_id(),
                    'name': name,
                    'gender': gender,
                    'branch': branch,
                    'position': position,
                    'passport_bytes': passport_file.getvalue(),
                    'passport_type': passport_file.type,
                    'logo_bytes': logo_file.getvalue() if logo_file else None,
                    'logo_type': logo_file.type if logo_file else None
                }
                st.session_state.submitted = True
                st.rerun()

else:
    data = st.session_state.data
    st.title("Your GraciousWord Global Mission Membership Card")
    
    passport_base64 = ""
    if data.get('passport_bytes'):
        passport_base64 = base64.b64encode(data['passport_bytes']).decode("utf-8")
    logo_base64 = ""
    if data.get('logo_bytes'):
        logo_base64 = base64.b64encode(data['logo_bytes']).decode("utf-8")

    # Card with deep/dark background, centered logo and "MEMBERSHIP CARD" subtitle
    st.markdown(
    f"""
    <style>
    :root {{
        --card-bg-start: #071228;
        --card-bg-end: #0a2b45;
        --accent: #FF6B6B; /* unused but available */
        --text-light: #FFFFFF;
        --muted: rgba(255,255,255,0.85);
    }}
    body {{ background-color: transparent; }}
    .id-card {{
        border-radius: 12px;
        padding: 14px;
        background: linear-gradient(135deg, var(--card-bg-start), var(--card-bg-end));
        box-shadow: 0 6px 18px rgba(2,6,23,0.55);
        max-width: 680px;
        width: 96%;
        margin: 12px auto;
        box-sizing: border-box;
        color: var(--text-light);
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.06);
    }}
    /* Header: logo centered (if provided) or fallback title text */
    .id-card .header {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 6px;
        padding-bottom: 8px;
        border-bottom: 1px solid rgba(255,255,255,0.06);
        margin-bottom: 10px;
    }}
    .id-card .logo {{
        max-width: clamp(90px, 22vw, 160px);
        width: auto;
        height: auto;
        display: block;
    }}
    .id-card .fallback-title {{
        color: var(--text-light);
        font-size: clamp(16px, 3.2vw, 20px);
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }}
    .id-card .subtitle {{
        color: rgba(255,255,255,0.95);
        font-size: clamp(12px, 2.6vw, 14px);
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.2px;
    }}

    /* Horizontal layout: passport left, bio right */
    .id-card .layout {{
        display: flex;
        gap: 12px;
        align-items: stretch;
        flex-direction: row;
        flex-wrap: nowrap;
    }}
    .id-card .photo {{
        flex: 0 0 clamp(70px, 18vw, 120px);
        box-sizing: border-box;
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.07);
        background: rgba(255,255,255,0.03);
    }}
    .id-card .photo img {{
        width: 100%;
        height: 100%;
        display: block;
        object-fit: cover;
    }}
    .id-card .text {{
        flex: 1 1 auto;
        min-width: 0;
        font-size: clamp(13px, 3vw, 18px);
        line-height: 1.35;
        color: var(--muted);
        padding-left: 6px;
    }}
    .id-card .text p {{
        margin: 6px 0;
        padding-bottom: 6px;
        border-bottom: 1px solid rgba(255,255,255,0.04);
        color: var(--text-light);
    }}
    .id-card .text p small {{
        display: block;
        color: rgba(255,255,255,0.80);
        font-weight: 500;
    }}

    @media (max-width: 420px) {{
        .id-card {{
            padding: 10px;
        }}
        .id-card .layout {{
            gap: 8px;
        }}
        .id-card .photo {{
            flex: 0 0 64px;
        }}
        .id-card .text {{
            font-size: 13px;
        }}
    }}
    </style>

    <div class="id-card">
        <div class="header">
            <!-- show logo if uploaded, else fallback title text -->
            {f'<img class="logo" src="data:{data.get("logo_type")};base64,{logo_base64}" alt="Logo">' if logo_base64 else '<div class="fallback-title">GraciousWord Global Mission</div>'}
            <div class="subtitle">MEMBERSHIP CARD</div>
        </div>

        <div class="layout">
            <div class="photo">
                {'<img src="data:' + data["passport_type"] + ';base64,' + passport_base64 + '" alt="Passport Photo">' if passport_base64 else '<div style="padding:12px; text-align:center; color:rgba(255,255,255,0.6);">No photo</div>'}
            </div>
            <div class="text">
                <p><strong>Unique ID:</strong> <small>{data['unique_id']}</small></p>
                <p><strong>Name:</strong> <small>{data['name'] or 'Not provided'}</small></p>
                <p><strong>Gender:</strong> <small>{data['gender'] or 'Not provided'}</small></p>
                <p><strong>Branch:</strong> <small>{data['branch'] or 'Not provided'}</small></p>
                <p><strong>Position:</strong> <small>{data['position'] or 'Not provided'}</small></p>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
    )
