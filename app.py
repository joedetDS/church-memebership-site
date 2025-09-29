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
                st.rerun()

else:
    data = st.session_state.data
    st.title("Your GraciousWord Global Mission ID Card")
    
    passport_base64 = ""
    if data['passport_bytes']:
        passport_base64 = base64.b64encode(data['passport_bytes']).decode("utf-8")

    st.markdown(
    f"""
    <style>
    .id-card {{
        border: 2px solid #007BFF;
        border-radius: 10px;
        padding: 15px;
        background-color: #F8F9FA;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        max-width: 600px;
        width: 95%;
        margin: 0 auto;
        box-sizing: border-box;
        overflow: hidden; /* prevent horizontal scroll */
    }}
    /* Centered title (explicit) */
    .id-card h3 {{
        color: #007BFF;
        text-align: center;
        margin: 0 0 12px 0;
        font-size: clamp(16px, 3.5vw, 24px);
        text-transform: uppercase;
        font-weight: 600;
        display: block;
    }}

    /* Horizontal layout: photo left, text right.
       align-items: stretch makes the photo match the text column's height. */
    .id-card .layout {{
        display: flex;
        gap: 8px;                 /* smaller gap reduces left whitespace */
        align-items: stretch;     /* make photo span the bio height */
        flex-direction: row;
        flex-wrap: nowrap;
    }}

    /* Photo column uses a responsive, clamped width (narrower than before) */
    .id-card .photo {{
        flex: 0 0 clamp(72px, 16vw, 110px); /* narrower width but full height */
        box-sizing: border-box;
    }}
    /* Make the image fill the photo column height and crop as needed */
    .id-card img {{
        width: 100%;
        height: 100%;
        object-fit: cover;       /* cover ensures it spans height while keeping aspect */
        border: 1px solid #ccc;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        display: block;
    }}

    /* Text column: bigger font, allowed to shrink to avoid overflow */
    .id-card .text {{
        flex: 1 1 auto;
        min-width: 0;  /* allow text to shrink within the flex container */
        font-size: clamp(13px, 3vw, 18px); /* INCREASED bio font size */
        line-height: 1.35;
        color: #333;
        padding-left: 4px; /* tiny padding so text isn't jammed to the image */
    }}
    .id-card .text p {{
        margin: 6px 0;
        padding-bottom: 4px;
        border-bottom: 1px solid #eee;
        word-wrap: break-word;
        overflow-wrap: break-word;
    }}
    .id-card .text p:last-child {{
        border-bottom: none;
    }}

    /* Very small screens: keep everything legible */
    @media (max-width: 360px) {{
        .id-card {{
            padding: 10px;
        }}
        .id-card h3 {{
            font-size: 16px;
        }}
        .id-card .photo {{
            flex: 0 0 64px; /* smallest width on tiny screens */
        }}
        .id-card .text {{
            font-size: 12.5px;
        }}
        .id-card .text p {{
            margin: 4px 0;
            padding-bottom: 3px;
        }}
    }}
    </style>

    <div class="id-card">
        <h3>GraciousWord Global Mission ID Card</h3>
        <div class="layout">
            <div class="photo">
                {'<img src="data:' + data['passport_type'] + ';base64,' + passport_base64 + '" alt="Passport Photo">' if data['passport_bytes'] else '<p style="text-align: center; color: #888; margin:0;">No passport photo uploaded</p>'}
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



