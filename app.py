import streamlit as st
import datetime
import base64
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont
import io
import os
import tempfile

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
    
    # HTML for ID card display
    id_card_html = f"""
    <div id="id-card" style="border: 2px solid black; padding: 10px; width: 300px; height: 400px; overflow: hidden;">
        <h2 style="text-align: center;">GraciousWord Global Mission ID Card</h2>
        {('<img src="data:{data["passport_type"]};base64,' + (base64.b64encode(Image.open(io.BytesIO(data['passport_bytes'])).tobytes()).decode('utf-8') if data['passport_bytes'] else '') + '" style="width: 120px; height: 150px; float: left; margin-right: 10px;" />' if data['passport_bytes'] else '<p>No passport photo</p>')}
        <p><strong>Unique ID:</strong> {data['unique_id']}</p>
        <p><strong>Name:</strong> {data['name'] or 'Not provided'}</p>
        <p><strong>Gender:</strong> {data['gender'] or 'Not provided'}</p>
        <p><strong>Branch:</strong> {data['branch'] or 'Not provided'}</p>
        <p><strong>Position:</strong> {data['position'] or 'Not provided'}</p>
    </div>
    """
    st.components.v1.html(id_card_html, height=450)

    # Generate ID card image
    img_buffer = io.BytesIO()
    img_width, img_height = 300, 400  # Match the HTML div size
    id_card_img = Image.new('RGB', (img_width, img_height), color='white')
    d = ImageDraw.Draw(id_card_img)
    
    # Load a font (using a default system font; adjust path if needed)
    try:
        font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()  # Fallback to default if custom font fails
    
    # Add title
    d.text((150, 10), "GraciousWord Global Mission ID Card", fill="black", font=font, anchor="mt")
    
    # Add passport photo if available
    if data['passport_bytes']:
        passport_img = Image.open(io.BytesIO(data['passport_bytes']))
        passport_img = passport_img.resize((120, 150), Image.Resampling.LANCZOS)
        id_card_img.paste(passport_img, (10, 40))
    
    # Add text fields
    text_y = 40
    text_items = [
        f"Unique ID: {data['unique_id']}",
        f"Name: {data['name'] or 'Not provided'}",
        f"Gender: {data['gender'] or 'Not provided'}",
        f"Branch: {data['branch'] or 'Not provided'}",
        f"Position: {data['position'] or 'Not provided'}"
    ]
    for item in text_items:
        d.text((140, text_y), item, fill="black", font=font)
        text_y += 30
    
    # Save image to buffer
    id_card_img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    # Download button for ID card image
    st.download_button(
        label="Download ID Card as Image",
        data=img_buffer,
        file_name=f"{data['unique_id']}_id_card.png",
        mime="image/png"
    )

    # Generate PDF in-memory
    pdf_buffer = io.BytesIO()
    pdf = FPDF(unit="mm", format=(100, 150))  # Custom size for ID card layout
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(100, 10, txt="GraciousWord Global Mission ID Card", ln=1, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(100, 10, txt=f"Unique ID: {data['unique_id']}", ln=1)
    pdf.cell(100, 10, txt=f"Name: {data['name'] or 'Not provided'}", ln=1)
    pdf.cell(100, 10, txt=f"Gender: {data['gender'] or 'Not provided'}", ln=1)
    pdf.cell(100, 10, txt=f"Branch: {data['branch'] or 'Not provided'}", ln=1)
    pdf.cell(100, 10, txt=f"Position: {data['position'] or 'Not provided'}", ln=1)
    
    # Add image to PDF if available
    if data['passport_bytes']:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
            img = Image.open(io.BytesIO(data['passport_bytes']))
            img.save(tmp_file, format="JPEG")
            tmp_path = tmp_file.name
            # Adjust image size to fit the left column (50mm width, proportional height)
            img_width = 50  # mm
            img_height = img.height * img_width / img.width
            pdf.image(tmp_path, x=5, y=20, w=img_width, h=img_height)  # Position and size adjusted
        os.unlink(tmp_path)  # Clean up temporary file
    
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
        st.rerun()
