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
    
    # Display ID card visually (basic layout)
    col1, col2 = st.columns(2)
    with col1:
        if data['passport_bytes']:
            st.image(data['passport_bytes'], width=300, caption="Passport Photo")  # Increased width to match text column height
        else:
            st.write("No passport photo uploaded.")
    with col2:
        st.write(f"**Membership ID:** {data['unique_id']}")
        st.write(f"**Name:** {data['name'] or 'Not provided'}")
        st.write(f"**Gender:** {data['gender'] or 'Not provided'}")
        st.write(f"**Branch:** {data['branch'] or 'Not provided'}")
        st.write(f"**Position:** {data['position'] or 'Not provided'}")
    
    # Centralized button to reset for another form
    st.markdown(
        """
        <style>
        .centered-button {
            text-align: center;
            margin-top: 20px;
        }
        .centered-button button {
            background-color: #4a90e2;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        </style>
        <div class="centered-button">
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Submit Another Form", key="reset_button"):
        st.session_state.submitted = False
        st.session_state.data = {}
        st.rerun()

