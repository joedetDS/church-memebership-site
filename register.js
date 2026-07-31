// GWGM — Registration page logic (ES module)
import { supabase, formatMembershipId } from './supabaseClient.js';
import {
  showToast, setButtonLoading, isValidEmail, isValidPhone, isNonEmpty,
  compressImage, ensureOnline,
} from './utils.js';

const form = document.getElementById('registerForm');
const submitBtn = document.getElementById('submitBtn');
const formLevelError = document.getElementById('formLevelError');
const photoInput = document.getElementById('profilePhoto');
const photoPreview = document.getElementById('photoPreview');

let selectedPhotoBlob = null;
let isSubmitting = false; // in-memory lock against double-click / double-submit

// ---- Photo preview + client-side compression ----
photoInput.addEventListener('change', async () => {
  const file = photoInput.files[0];
  clearFieldError('profilePhoto');
  if (!file) { selectedPhotoBlob = null; return; }

  if (!file.type.startsWith('image/')) {
    setFieldError('profilePhoto', 'Please select a valid image file.');
    photoInput.value = '';
    return;
  }

  try {
    selectedPhotoBlob = await compressImage(file);
    const url = URL.createObjectURL(selectedPhotoBlob);
    photoPreview.innerHTML = `<img src="${url}" alt="Selected passport photo preview" />`;
  } catch (err) {
    setFieldError('profilePhoto', 'Could not process this image. Please try another photo.');
    selectedPhotoBlob = null;
  }
});

// ---- Field-level error helpers ----
function setFieldError(fieldId, message) {
  const el = document.getElementById(`err-${fieldId}`);
  const input = document.getElementById(fieldId);
  if (el) el.textContent = message;
  if (input) input.setAttribute('aria-invalid', 'true');
}
function clearFieldError(fieldId) {
  const el = document.getElementById(`err-${fieldId}`);
  const input = document.getElementById(fieldId);
  if (el) el.textContent = '';
  if (input) input.removeAttribute('aria-invalid');
}

function validateForm(values) {
  let valid = true;
  const required = ['firstName', 'lastName', 'gender', 'dob', 'phone', 'email', 'address', 'state', 'country', 'branch'];
  required.forEach((f) => clearFieldError(f));
  clearFieldError('profilePhoto');

  required.forEach((field) => {
    if (!isNonEmpty(values[field])) {
      setFieldError(field, 'This field is required.');
      valid = false;
    }
  });

  if (!selectedPhotoBlob) {
    setFieldError('profilePhoto', 'A passport photograph is required.');
    valid = false;
  }
  if (values.email && !isValidEmail(values.email)) {
    setFieldError('email', 'Please enter a valid email address.');
    valid = false;
  }
  if (values.phone && !isValidPhone(values.phone)) {
    setFieldError('phone', 'Please enter a valid phone number.');
    valid = false;
  }
  if (values.whatsapp && !isValidPhone(values.whatsapp)) {
    setFieldError('whatsapp', 'Please enter a valid WhatsApp number.');
    valid = false;
  }
  return valid;
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  formLevelError.textContent = '';

  if (isSubmitting) return; // guards against double-click
  if (!ensureOnline()) return;

  const values = {
    firstName: form.firstName.value.trim(),
    lastName: form.lastName.value.trim(),
    gender: form.gender.value,
    dob: form.dob.value,
    phone: form.phone.value.trim(),
    whatsapp: form.whatsapp.value.trim(),
    email: form.email.value.trim(),
    occupation: form.occupation.value.trim(),
    address: form.address.value.trim(),
    state: form.state.value.trim(),
    country: form.country.value.trim(),
    branch: form.branch.value,
    position: form.position.value.trim(),
  };

  if (!validateForm(values)) {
    formLevelError.textContent = 'Please correct the highlighted fields above.';
    return;
  }

  isSubmitting = true;
  setButtonLoading(submitBtn, true, 'Registering…');

  try {
    // 1. Upload photo to Supabase Storage first, so we have a URL to save.
    const fileExt = 'jpg';
    const filePath = `${Date.now()}-${Math.random().toString(36).slice(2)}.${fileExt}`;
    const { error: uploadError } = await supabase.storage
      .from(window.GWGM_CONFIG.STORAGE_BUCKET)
      .upload(filePath, selectedPhotoBlob, { contentType: 'image/jpeg', upsert: false });

    if (uploadError) throw new Error(`Photo upload failed: ${uploadError.message}`);

    const { data: publicUrlData } = supabase.storage
      .from(window.GWGM_CONFIG.STORAGE_BUCKET)
      .getPublicUrl(filePath);
    const profilePhotoUrl = publicUrlData.publicUrl;

    // 2. Insert the member record. The database (IDENTITY column) generates
    //    the real id — we never compute or guess it client-side.
    const fullName = `${values.firstName} ${values.lastName}`.trim();
    const issueDate = new Date().toISOString().slice(0, 10);

    const { data: inserted, error: insertError } = await supabase
      .from('members')
      .insert({
        first_name: values.firstName,
        last_name: values.lastName,
        full_name: fullName,
        gender: values.gender,
        phone: values.phone,
        whatsapp: values.whatsapp || null,
        email: values.email,
        date_of_birth: values.dob,
        occupation: values.occupation || null,
        residential_address: values.address,
        state: values.state,
        country: values.country,
        branch: values.branch,
        position_held: values.position || null,
        profile_photo_url: profilePhotoUrl,
        issue_date: issueDate,
      })
      .select()
      .single();

    if (insertError) {
      if (insertError.code === '23505') {
        throw new Error('It looks like you may already be registered with this email or phone number.');
      }
      throw new Error(`Registration could not be saved: ${insertError.message}`);
    }

    // 3. Format the membership id from the real database id, then persist
    //    the QR payload back onto the same row (keeps QR data server-side too).
    const membershipId = formatMembershipId(inserted.id);
    const qrData = {
      id: inserted.id,
      membership_id: membershipId,
      name: fullName,
      branch: inserted.branch,
      phone: inserted.phone,
      issue_date: inserted.issue_date,
    };

    const { data: finalRecord, error: updateError } = await supabase
      .from('members')
      .update({ membership_number: membershipId, qr_data: qrData })
      .eq('id', inserted.id)
      .select()
      .single();

    if (updateError) throw new Error(`Could not finalize membership id: ${updateError.message}`);

    // 4. Hand off ONLY as a temporary bridge to the ID card page.
    //    idcard.js re-reads this record and clears it immediately after use —
    //    it is never treated as the permanent copy of the data.
    localStorage.setItem('memberData', JSON.stringify(finalRecord));

    showToast('Registration successful! Generating your ID card…', 'success');
    window.location.href = 'idcard.html';
  } catch (err) {
    console.error(err);
    formLevelError.textContent = err.message || 'Something went wrong. Please try again.';
    showToast(err.message || 'Registration failed.', 'error');
  } finally {
    isSubmitting = false;
    setButtonLoading(submitBtn, false);
  }
});
