document.addEventListener('DOMContentLoaded', function() {
    // Initialize form elements
    const registrationForm = document.getElementById('registrationForm');
    const passportPhoto = document.getElementById('passportPhoto');
    const passportPreview = document.getElementById('passportPreview');
    const uploadText = document.getElementById('uploadText');

    // Handle passport photo preview
    if (passportPhoto) {
        passportPhoto.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                // Check file size
                if (file.size > 300 * 1024) { // 300KB
                    alert('Photo size must be less than 300KB');
                    passportPhoto.value = '';
                    return;
                }

                // Check file type
                const validTypes = ['image/jpeg', 'image/png', 'image/jpg'];
                if (!validTypes.includes(file.type)) {
                    alert('Only JPG/PNG images are allowed');
                    passportPhoto.value = '';
                    return;
                }

                // Create preview
                const reader = new FileReader();
                reader.onload = function(event) {
                    passportPreview.src = event.target.result;
                    passportPreview.classList.remove('hidden');
                    uploadText.classList.add('hidden');
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // Handle form submission
    if (registrationForm) {
        registrationForm.addEventListener('submit', function(e) {
            e.preventDefault();

            // Validate phone number
            const phone = document.getElementById('phone').value;
            if (!/^[0-9]{11}$/.test(phone)) {
                alert('Please enter a valid 11-digit phone number');
                return;
            }

            // Gather form data
            const formData = {
                passportPhoto: passportPreview.src,
                fullName: document.getElementById('fullName').value,
                dob: document.getElementById('dob').value,
                regDate: document.getElementById('regDate').value,
                gender: document.querySelector('input[name="gender"]:checked').value,
                phone: phone,
                address: document.getElementById('address').value,
                occupation: document.getElementById('occupation').value,
                branch: document.getElementById('branch').value,
                position: document.getElementById('position').value,
                motivation: document.getElementById('motivation').value,
                memberId: generateMemberId()
            };

            // Store in localStorage
            localStorage.setItem('memberData', JSON.stringify(formData));

            // Redirect to ID card page
            window.location.href = 'id-card.html';
        });
    }

    // Load ID card page content
    if (window.location.pathname.includes("id-card.html")) {
        const memberData = JSON.parse(localStorage.getItem('memberData'));

        if (memberData) {
            // Fill card details
            document.getElementById('idPhoto').src = memberData.passportPhoto;
            document.getElementById('idFullName').textContent = memberData.fullName;
            document.getElementById('idBranch').textContent = memberData.branch;
            document.getElementById('idPosition').textContent = memberData.position;
            document.getElementById('memberId').textContent = memberData.memberId;
            document.getElementById('idIssueDate').textContent = memberData.regDate;


            const qrEl = document.getElementById('qrCode');
            if (qrEl && window.QRCode) {
                try {
                    // Clear any previous content
                    qrEl.innerHTML = '';
                    // Pass element (DOM node or id) and avoid using QRCode.CorrectLevel
                    new QRCode(qrEl, {
                        text: JSON.stringify({
                            id: memberData.memberId,
                            name: memberData.fullName,
                            branch: memberData.branch,
                            position: memberData.position
                        }),
                        width: 100,
                        height: 100,
                        colorDark: "#000000",
                        colorLight: "#ffffff"
                    });
                } catch (err) {
                    console.error('QR generation failed:', err);
                }
            } else if (!window.QRCode) {
                console.error('QRCode library not loaded. Ensure qrcode.min.js is included before script.js');
            } else {
                console.error('QR element #qrCode not found in the DOM');
            }
            
        }
    }

    // Handle ID card download/print
    const downloadBtn = document.getElementById('downloadBtn');
    const printBtn = document.getElementById('printBtn');

    if (downloadBtn) {
        downloadBtn.addEventListener('click', function() {
            generatePDF();
        });
    }

    if (printBtn) {
        printBtn.addEventListener('click', function() {
            window.print();
        });
    }
});

// Generate unique member ID
function generateMemberId() {
    let memberCount = localStorage.getItem('memberCount');
    if (!memberCount) {
        memberCount = 1;
    } else {
        memberCount = parseInt(memberCount) + 1;
    }

    localStorage.setItem('memberCount', memberCount);
    return 'GWGM' + memberCount.toString().padStart(3, '0');
}

// Generate PDF from ID card
function generatePDF() {
    const { jsPDF } = window.jspdf;
    const element = document.getElementById('idCard');

    html2canvas(element, {
        scale: 2,
        logging: true,
        useCORS: true
    }).then(canvas => {
        const imgData = canvas.toDataURL('image/png');
        const pdf = new jsPDF({
            orientation: 'landscape',
            unit: 'mm'
        });

        // Calculate dimensions to fit the PDF
        const pdfWidth = pdf.internal.pageSize.getWidth();
        const pdfHeight = pdf.internal.pageSize.getHeight();
        const imgWidth = canvas.width;
        const imgHeight = canvas.height;
        const ratio = Math.min(pdfWidth / imgWidth, pdfHeight / imgHeight) * 0.95;
        const imgX = (pdfWidth - imgWidth * ratio) / 2;
        const imgY = (pdfHeight - imgHeight * ratio) / 2;

        pdf.addImage(imgData, 'PNG', imgX, imgY, imgWidth * ratio, imgHeight * ratio);
        pdf.save('GWGM_MemberID.pdf');
    });
}
