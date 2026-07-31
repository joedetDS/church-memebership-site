// GWGM — ID Card page logic (ES module)
import { supabase } from './supabaseClient.js';
import { showToast, formatDate, setButtonLoading } from './utils.js';
import { renderMemberQrCode, buildQrPayload } from './qr.js';

const loadingState = document.getElementById('loadingState');
const errorState = document.getElementById('errorState');
const errorMessage = document.getElementById('errorMessage');
const cardSection = document.getElementById('cardSection');

async function init() {
  // Read the temporary handoff written by register.js. This is used only
  // to know WHICH record to look up — never as the permanent data source.
  const raw = localStorage.getItem('memberData');
  const params = new URLSearchParams(window.location.search);
  const idFromUrl = params.get('id');

  let handoff = null;
  try { handoff = raw ? JSON.parse(raw) : null; } catch { handoff = null; }

  const memberId = idFromUrl || handoff?.id;

  if (!memberId) {
    showError('No registration found. Please register first.');
    return;
  }

  try {
    // Always re-fetch the authoritative record from Supabase — this
    // guarantees the card reflects permanent, persisted data rather than
    // whatever happened to be sitting in localStorage. We read from the
    // `public_member_card` VIEW (not the `members` table directly) so the
    // anon key only ever exposes the fields the card actually displays —
    // never email, phone, whatsapp, address, state, country, or DOB.
    const { data: member, error } = await supabase
      .from('public_member_card')
      .select('*')
      .eq('id', memberId)
      .single();

    if (error || !member) {
      throw new Error('We could not retrieve your membership record. Please contact an administrator.');
    }

    await renderCard(member);

    // The handoff has served its purpose — clear it so it can't be
    // reused or resubmitted (e.g. on browser back/refresh).
    localStorage.removeItem('memberData');

    loadingState.hidden = true;
    cardSection.hidden = false;
  } catch (err) {
    console.error(err);
    showError(err.message);
  }
}

function showError(message) {
  loadingState.hidden = true;
  errorMessage.textContent = message;
  errorState.hidden = false;
}

async function renderCard(member) {
  document.getElementById('cardPhoto').src = member.profile_photo_url || '';
  document.getElementById('cardPhoto').alt = `Photo of ${member.full_name}`;
  document.getElementById('cardName').textContent = member.full_name;
  document.getElementById('cardMembershipId').textContent = member.membership_number || '—';
  document.getElementById('cardBranch').textContent = member.branch;
  document.getElementById('cardPosition').textContent = member.position_held || 'Member';
  document.getElementById('cardIssueDate').textContent = formatDate(member.issue_date);

  const qrCanvas = document.getElementById('qrCanvas');
  const payload = member.qr_data || buildQrPayload(member);
  try {
    await renderMemberQrCode(qrCanvas, payload);
  } catch (err) {
    console.warn('QR code could not be generated:', err.message);
  }
}

// ---- Download / print actions ----
document.getElementById('downloadPngBtn').addEventListener('click', async (e) => {
  const btn = e.currentTarget;
  setButtonLoading(btn, true, 'Preparing…');
  try {
    const canvas = await html2canvas(document.getElementById('membershipCard'), { scale: 2, useCORS: true });
    const link = document.createElement('a');
    link.download = 'gwgm-membership-card.png';
    link.href = canvas.toDataURL('image/png');
    link.click();
  } catch (err) {
    showToast('Could not generate the image download.', 'error');
  } finally {
    setButtonLoading(btn, false);
  }
});

document.getElementById('downloadPdfBtn').addEventListener('click', async (e) => {
  const btn = e.currentTarget;
  setButtonLoading(btn, true, 'Preparing…');
  try {
    const canvas = await html2canvas(document.getElementById('membershipCard'), { scale: 2, useCORS: true });
    const imgData = canvas.toDataURL('image/png');
    const { jsPDF } = window.jspdf;
    const pdf = new jsPDF({ orientation: 'portrait', unit: 'pt' });
    const pageWidth = pdf.internal.pageSize.getWidth();
    const imgWidth = pageWidth - 80;
    const imgHeight = (canvas.height / canvas.width) * imgWidth;
    pdf.addImage(imgData, 'PNG', 40, 60, imgWidth, imgHeight);
    pdf.save('gwgm-membership-card.pdf');
  } catch (err) {
    showToast('Could not generate the PDF download.', 'error');
  } finally {
    setButtonLoading(btn, false);
  }
});

document.getElementById('printBtn').addEventListener('click', () => window.print());

init();
