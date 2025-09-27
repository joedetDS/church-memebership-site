import streamlit as st
import datetime
from fpdf import FPDF
from PIL import Image
import io

# Initialize session state for counter, submission, data, and validation
if 'member_count' not in st.session_state:
    st.session_state.member_count = 0
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'data' not in st.session_state:
    st.session_state.data = {}
if 'validations' not in st.session_state:
    st.session_state.validations = {
        'passport': False,
        'name': False,
        'dob': False,
        'gender': True,
        'phone': False,
        'address': False,
        'occupation': False,
        'branch': True,
        'position': True,
        'motivation': False
    }

# Function to generate unique ID
def get_next_id():
    st.session_state.member_count += 1
    return f"GWGM{st.session_state.member_count:03d}"

# Function to check if all fields are valid
def all_fields_valid():
    return all(st.session_state.validations.values())

if not st.session_state.submitted:
    st.title("GraciousWord Global Mission Membership Form")
    
    with st.form(key="membership_form"):
        # Passport upload (with real-time size validation)
        passport_file = st.file_uploader("Upload Passport Photo (max 300 KB)", type=["jpg", "jpeg", "png"], key="passport")
        if passport_file:
            file_bytes = passport_file.getvalue()
            if len(file_bytes) > 300 * 1024:
                st.warning("File size exceeds 300 KB. Please upload a smaller image.")
                st.session_state.validations['passport'] = False
            else:
                st.session_state.validations['passport'] = True
        else:
            st.session_state.validations['passport'] = False
            if st.session_state.validations['passport'] is False and 'passport' in st.session_state:
                st.warning("Please upload a passport photo.")
        
        # Name
        st.session_state.data['name'] = st.text_input("Name", max_chars=100, key="name")
        st.session_state.validations['name'] = bool(st.session_state.data['name'].strip())
        if not st.session_state.validations['name']:
            st.warning("Please enter your name.")
        
        # Date of Birth
        st.session_state.data['dob'] = st.date_input("Date of Birth", min_value=datetime.date(1900, 1, 1), max_value=datetime.date.today(), key="dob")
        st.session_state.validations['dob'] = st.session_state.data['dob'] is not None
        if not st.session_state.validations['dob']:
            st.warning("Please select your date of birth.")
        
        # Gender
        st.session_state.data['gender'] = st.radio("Gender", ["Male", "Female"], key="gender")
        st.session_state.validations['gender'] = True
        
        # Phone / WhatsApp Number
        st.session_state.data['phone'] = st.text_input("Phone / WhatsApp Number", max_chars=20, key="phone")
        st.session_state.validations['phone'] = bool(st.session_state.data['phone'].strip())
        if not st.session_state.validations['phone']:
            st.warning("Please enter your phone number.")
        
        # Residential Address
        st.session_state.data['address'] = st.text_area("Residential Address", max_chars=200, key="address")
        st.session_state.validations['address'] = bool(st.session_state.data['address'].strip())
        if not st.session_state.validations['address']:
            st.warning("Please enter your residential address.")
        
        # Occupation
        st.session_state.data['occupation'] = st.text_input("Occupation", max_chars=100, key="occupation")
        st.session_state.validations['occupation'] = bool(st.session_state.data['occupation'].strip())
        if not st.session_state.validations['occupation']:
            st.warning("Please enter your occupation.")
        
        # Branch Affiliation
        st.session_state.data['branch'] = st.selectbox("Branch Affiliation", ["Uyo", "Aksu", "Eket"], key="branch")
        st.session_state.validations['branch'] = True
        
        # Position Held
        st.session_state.data['position'] = st.selectbox("Position Held", ["Pastor", "Evangelist", "Deacon", "Deaconess", "Unit Head", "Worker", "Member"], key="position")
        st.session_state.validations['position'] = True
        
        # Motivation
        st.session_state.data['motivation'] = st.text_area("What has drawn you to join GraciousWord Global Mission, and how do you hope to grow in your faith through this family?", max_chars=500, key="motivation")
        st.session_state.validations['motivation'] = bool(st.session_state.data['motivation'].strip())
        if not st.session_state.validations['motivation']:
            st.warning("Please enter your motivation for joining.")
        
        # Submit button (disabled until all fields are valid)
        submit_button = st.form_submit_button("Submit", disabled=not all_fields_valid())
        
        if submit_button and all_fields_valid():
            # Store passport data and submit
            if passport_file:
                st.session_state.data['passport_bytes'] = passport_file.getvalue()
                st.session_state.data['passport_type'] = passport_file.type
                st.session_state.data['unique_id'] = get_next_id()
                st.session_state.submitted = True
                st.rerun()  # Refresh to show ID card

else:
    data = st.session_state.data
    st.title("Your GraciousWord Global Mission ID Card")
    
    # Display ID card visually (basic layout)
    col1, col2 = st.columns(2)
    with col1:
        st.image(data['passport_bytes'], width=150, caption="Passport Photo")
    with col2:
        st.write(f"**Unique ID:** {data['unique_id']}")
        st.write(f"**Name:** {data['name']}")
        st.write(f"**Gender:** {data['gender']}")
        st.write(f"**Branch:** {data['branch']}")
        st.write(f"**Position:** {data['position']}")
    
    st.info("You can print this page directly from your browser (Ctrl+P or right-click > Print). Or download as PDF below.")
    
    # Generate PDF in-memory
    pdf_buffer = io.BytesIO()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt="GraciousWord Global Mission ID Card", ln=1, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Unique ID: {data['unique_id']}", ln=1)
    pdf.cell(200, 10, txt=f"Name: {data['name']}", ln=1)
    pdf.cell(200, 10, txt=f"Gender: {data['gender']}", ln=1)
    pdf.cell(200, 10, txt=f"Branch: {data['branch']}", ln=1)
    pdf.cell(200, 10, txt=f"Position: {data['position']}", ln=1)
    
    # Add image to PDF using in-memory bytes
    img = Image.open(io.BytesIO(data['passport_bytes']))
    img_buffer = io.BytesIO()
    img.save(img_buffer, format="JPEG")
    img_buffer.seek(0)
    pdf.image(img_buffer, x=10, y=10, w=50)  # Position image at top-left
    
    pdf.output(pdf_buffer)
    pdf_buffer.seek(0)
    
    st.download_button(
        label="Download ID Card as PDF",
        data=pdf_buffer,
        file_name=f"{data['unique_id']}_id_card.pdf",
        mime="application/pdf"
    )
    
    # Button to reset for another form
    if st.button("Submit Another Form"):
        st.session_state.submitted = False
        st.session_state.data = {}
        st.session_state.validations = {
            'passport': False,
            'name': False,
            'dob': False,
            'gender': True,
            'phone': False,
            'address': False,
            'occupation': False,
            'branch': True,
            'position': True,
            'motivation': False
        }
        st.rerun()
