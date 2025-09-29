import streamlit as st
import datetime
import base64
from PIL import Image
import io

# Load logo image as base64 once at start
with open("logo.png", "rb") as f:
    logo_bytes = f.read()
logo_base64 = base64.b64encode(logo_bytes).decode("utf-8")
logo_html = f'<img src="data:image/png;base64,{logo_base64}" alt="Logo" style="max-width: 200px; display: block; margin: 0 auto 10px auto;">'

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
            passport_file = st.file_uploader("Upload Passport Photo (Drag and drop file here, Limit 300KB per file • JPG, JPEG, PNG)", type=["jpg", "jpeg", "png"], accept_multiple_files=False)
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
                st.session_state.data = {
                    'unique_id': get_next_id(),
                    'name': name,
                    'gender': gender,
                    'branch': branch,
                    'position': position,
                    'passport_bytes': passport_file.getvalue(),
                    'passport_type': passport_file.type
                }
                st.session_state.submitted = True
                st.experimental_rerun()

else:
    data = st.session_state.data
    st.title("Your GraciousWord Global Mission Membership Card")
    
    passport_base64 = ""
    if data['passport_bytes']:
        passport_base64 = base64.b64encode(data['passport_bytes']).decode("utf-8")

    st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');

    .id-card {{
        border: 2px solid #007BFF;
        border-radius: 10px;
        padding: 15px;
        background-color: #001F3F; /* deep navy background */
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        max-width: 600px;
        width: 95%;
        margin: 0 auto;
        box-sizing: border-box;
        overflow: hidden; /* prevent horizontal scroll */
        font-family: 'Roboto', 'Helvetica Neue', sans-serif;
        color: #FFFFFF;
    }}

    .id-card h3 {{
        color: #FFFFFF;
        text-align: center;
        margin: 0 0 12px 0;
        font-size: clamp(22px, 3vw, 24px);
        font-weight: 700;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        font-family: 'Roboto', 'Helvetica Neue', sans-serif;
    }}

    .id-card .logo {{
        display: block;
        margin-left: auto;
        margin-right: auto;
        max-width: 220px;
        margin-bottom: 10px;
    }}

    .id-card .layout {{
        display: flex;
        gap: 8px;
        align-items: stretch;
        flex-direction: row;
        flex-wrap: nowrap;
    }}

    .id-card .photo {{
        flex: 0 0 clamp(72px, 16vw, 110px);
        box-sizing: border-box;
    }}
    .id-card img.passport-photo {{
        width: 100%;
        height: 100%;
        object-fit: cover;
        border: 1px solid #ccc;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        display: block;
    }}

    .id-card .text {{
        flex: 1 1 auto;
        min-width: 0;
        font-size: clamp(14px, 2.8vw, 18px);
        line-height: 1.35;
        color: #FFFFFF;
        padding-left: 6px;
    }}

    .id-card .text p {{
        margin: 6px 0;
        padding-bottom: 4px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        word-wrap: break-word;
        overflow-wrap: break-word;
    }}

    .id-card .text p:last-child {{
        border-bottom: none;
    }}

    /* Responsive for small screens */
    @media (max-width: 360px) {{
        .id-card {{
            padding: 10px;
        }}
        .id-card h3 {{
            font-size: 18px;
        }}
        .id-card .photo {{
            flex: 0 0 64px;
        }}
        .id-card .text {{
            font-size: 13px;
        }}
        .id-card .text p {{
            margin: 4px 0;
            padding-bottom: 3px;
        }}
    }}
    </style>

    <div class="id-card">
        {logo_html}
        <h3>MEMBERSHIP CARD</h3>
        <div class="layout">
            <div class="photo">
                {'<img class="passport-photo" src="data:' + data['passport_type'] + ';base64,' + passport_base64 + '" alt="Passport Photo">' if data['passport_bytes'] else '<p style="text-align: center; color: #AAA; margin:0;">No passport photo uploaded</p>'}
            </div>
            <div class="text">
                <p><strong>Unique ID:</strong> {data['unique_id']}</p>
                <p><strong>Name:</strong> {data['name'] or 'Not provided'}</p>
                <p><strong>Gender:</strong> {data['gender'] or 'Not provided'}</p>
                <p><strong>Branch:</strong> {data['branch'] or 'Not provided'}</p>
                <p><strong>Position:</strong> {data['position'] or 'Not provided'}</p>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
