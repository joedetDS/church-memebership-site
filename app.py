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
        # Passport upload (with size limit)
        passport_file = st.file_uploader("Upload Passport Photo (max 300 KB)", type=["jpg", "jpeg", "png"])
        if passport_file:
            file_bytes = passport_file.getvalue()
            if len(file_bytes) > 300 * 1024:
                st.error("File size exceeds 300 KB. Please upload a smaller image.")
                st.stop()
        
        name = st.text_input("Name", max_chars=100)
        dob = st.date_input("Date of Birth", min_value=datetime.date(1900, 1, 1), max_value=datetime.date.today())
        gender = st.radio("Gender", ["Male", "Female"])
        phone = st.text_input("Phone / WhatsApp Number", max_chars=20)
        address = st.text_area("Residential Address", max_chars=200)
        occupation = st.text_input("Occupation", max_chars=100)
        branch = st.selectbox("Branch Affiliation", ["Uyo", "Aksu", "Eket"])
        position = st.selectbox("Position Held", ["Pastor", "Evangelist", "Deacon", "Deaconess", "Unit Head", "Worker", "Member"])
        motivation = st.text_area("What has drawn you to join GraciousWord Global Mission, and how do you hope to grow in your faith through this family?", max_chars=500)
        
        submit_button = st.form_submit_button("Submit")
        
        if submit_button:
            if not all([passport_file, name, dob, gender, phone, address, occupation, branch, position, motivation]):
                st.error("Please fill all required fields.")
            else:
                # Generate unique ID
                unique_id = get_next_id()
                
                # Store data in session state
                st.session_state.data = {
                    'unique_id': unique_id,
                    'name': name,
                    'gender': gender,
                    'branch': branch,
                    'position': position,
                    'passport_bytes': file_bytes,
                    'passport_type': passport_file.type
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
    
    # Generate PDF for download
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
    
    # Add image to PDF
    with open("temp_passport.jpg", "wb") as f:
        f.write(data['passport_bytes'])
    pdf.image("temp_passport.jpg", x=10, y=10, w=50)  # Position image at top-left
    
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
        st.rerun()