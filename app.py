import streamlit as st
import datetime
from fpdf import FPDF
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
        # Passport upload (with real-time size validation)
        passport_file = st.file_uploader("Upload Passport Photo (max 300 KB)", type=["jpg", "jpeg", "png"])
        if passport_file:
            file_bytes = passport_file.getvalue()
            if len(file_bytes) > 300 * 1024:
                st.warning("File size exceeds 300 KB. Please upload a smaller image.")
            else:
                st.session_state.validations = {'passport': True} if 'validations' not in st.session_state else {**st.session_state.validations, 'passport': True}
        else:
            st.warning("Please upload a passport photo.")
            st.session_state.validations = {'passport': False} if 'validations' not in st.session_state else {**st.session_state.validations, 'passport': False}
        
        # Name
        name = st.text_input("Name", max_chars=100)
        if not name.strip():
            st.warning("Please enter your name.")
            st.session_state.validations = {'name': False} if 'validations' not in st.session_state else {**st.session_state.validations, 'name': False}
        else:
            st.session_state.validations = {'name': True} if 'validations' not in st.session_state else {**st.session_state.validations, 'name': True}
        
        # Date of Birth
        dob = st.date_input("Date of Birth", min_value=datetime.date(1900, 1, 1), max_value=datetime.date.today())
        if dob is None:
            st.warning("Please select your date of birth.")
            st.session_state.validations = {'dob': False} if 'validations' not in st.session_state else {**st.session_state.validations, 'dob': False}
        else:
            st.session_state.validations = {'dob': True} if 'validations' not in st.session_state else {**st.session_state.validations, 'dob': True}
        
        # Gender
        gender = st.radio("Gender", ["Male", "Female"])
        st.session_state.validations = {'gender': True} if 'validations' not in st.session_state else {**st.session_state.validations, 'gender': True}
        
        # Phone / WhatsApp Number
        phone = st.text_input("Phone / WhatsApp Number", max_chars=20)
        if not phone.strip():
            st.warning("Please enter your phone number.")
            st.session_state.validations = {'phone': False} if 'validations' not in st.session_state else {**st.session_state.validations, 'phone': False}
        else:
            st.session_state.validations = {'phone': True} if 'validations' not in st.session_state else {**st.session_state.validations, 'phone': True}
        
        # Residential Address
        address = st.text_area("Residential Address", max_chars=200)
        if not address.strip():
            st.warning("Please enter your residential address.")
            st.session_state.validations = {'address': False} if 'validations' not in st.session_state else {**st.session_state.validations, 'address': False}
        else:
            st.session_state.validations = {'address': True} if 'validations' not in st.session_state else {**st.session_state.validations, 'address': True}
        
        # Occupation
        occupation = st.text_input("Occupation", max_chars=100)
        if not occupation.strip():
            st.warning("Please enter your occupation.")
            st.session_state.validations = {'occupation': False} if 'validations' not in st.session_state else {**st.session_state.validations, 'occupation': False}
        else:
            st.session_state.validations = {'occupation': True} if 'validations' not in st.session_state else {**st.session_state.validations, 'occupation': True}
        
        # Branch Affiliation
        branch = st.selectbox("Branch Affiliation", ["Uyo", "Aksu", "Eket"])
        st.session_state.validations = {'branch': True} if 'validations' not in st.session_state else {**st.session_state.validations, 'branch': True}
        
        # Position Held
        position = st.selectbox("Position Held", ["Pastor", "Evangelist", "Deacon", "Deaconess", "Unit Head", "Worker", "Member"])
        st.session_state.validations = {'position': True} if 'validations' not in st.session_state else {**st.session_state.validations, 'position': True}
        
        # Motivation
        motivation = st.text_area("What has drawn you to join GraciousWord Global Mission, and how do you hope to grow in your faith through this family?", max_chars=500)
        if not motivation.strip():
            st.warning("Please enter your motivation for joining.")
            st.session_state.validations = {'motivation': False} if 'validations' not in st.session_state else {**st.session_state.validations, 'motivation': False}
        else:
            st.session_state.validations = {'motivation': True} if 'validations' not in st.session_state else {**st.session_state.validations, 'motivation': True}
        
        # Submit button (disabled until all fields are valid)
        submit_button = st.form_submit_button("Submit", disabled=not all(st.session_state.validations.values()) if 'validations' in st.session_state else True)
        
        if submit_button and all(st.session_state.validations.values()):
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
        st.session_state.validations = {}
        st.rerun()
