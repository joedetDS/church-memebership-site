import streamlit as st
import datetime
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
        # Passport upload
        passport_file = st.file_uploader("Upload Passport Photo (optional)", type=["jpg", "jpeg", "png"])
        
        # Name
        name = st.text_input("Name", max_chars=100)
        
        # Date of Birth
        dob = st.date_input("Date of Birth", min_value=datetime.date(1900, 1, 1), max_value=datetime.date.today())
        
        # Gender
        gender = st.radio("Gender", ["Male", "Female"])
        
        # Phone / WhatsApp Number
        phone = st.text_input("Phone / WhatsApp Number", max_chars=20)
        
        # Residential Address
        address = st.text_area("Residential Address", max_chars=200)
        
        # Occupation
        occupation = st.text_input("Occupation", max_chars=100)
        
        # Branch Affiliation
        branch = st.selectbox("Branch Affiliation", ["Uyo", "Aksu", "Eket"])
        
        # Position Held
        position = st.selectbox("Position Held", ["Pastor", "Evangelist", "Deacon", "Deaconess", "Unit Head", "Worker", "Member"])
        
        # Motivation
        motivation = st.text_area("What has drawn you to join GraciousWord Global Mission, and how do you hope to grow in your faith through this family?", max_chars=500)
        
        # Submit button (always enabled)
        submit_button = st.form_submit_button("Submit")
        
        if submit_button:
            # Store data and submit
            st.session_state.data = {
                'unique_id': get_next_id(),
                'name': name,
                'gender': gender,
                'branch': branch,
                'position': position,
                'passport_bytes': passport_file.getvalue() if passport_file else None,
                'passport_type': passport_file.type if passport_file else None
            }
            st.session_state.submitted = True
            st.rerun()  # Refresh to show ID card

else:
    data = st.session_state.data
    st.title("Your GraciousWord Global Mission ID Card")
    
    # Beautified ID card layout using HTML/CSS
    passport_base64 = ""
    if data['passport_bytes']:
        passport_base64 = base64.b64encode(data['passport_bytes']).decode("utf-8")

    st.markdown(
        f"""
        <style>
        .id-card {{
            border: 2px solid #007BFF;
            border-radius: 10px;
            padding: 20px;
            background-color: #F8F9FA;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            max-width: 600px;
            margin: 0 auto;
        }}
        .id-card h3 {{
            color: #007BFF;
            text-align: center;
            margin-bottom: 20px;
            font-size: 24px;
        }}
        .id-card .layout {{
            display: flex;
            gap: 20px;
            align-items: center;
            justify-content: center;
        }}
        .id-card img {{
            width: 200px;
            height: auto;
            border: 1px solid #ccc;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }}
        .id-card .text {{
            font-size: 16px;
            line-height: 1.5;
            color: #333;
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
            }}
        }}
        </style>
        <div class="id-card">
            <h3>GraciousWord Global Mission ID Card</h3>
            <div class="layout">
                <div>
                    {'<img src="data:' + data['passport_type'] + ';base64,' + passport_base64 + '" alt="Passport Photo">' if data['passport_bytes'] else '<p style="text-align: center; color: #888;">No passport photo uploaded</p>'}
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
    
    # Button to reset for another form
    if st.button("Submit Another Form"):
        st.session_state.submitted = False
        st.session_state.data = {}
        st.rerun()
