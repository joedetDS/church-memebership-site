// GWGM — QR code helper (ES module)
// Wraps the `qrcode` UMD library (loaded globally via CDN <script> in each HTML page).

/**
 * Renders a QR code into the given canvas element.
 * @param {HTMLCanvasElement} canvasEl
 * @param {object} data - plain object to encode as JSON in the QR code
 */
export async function renderMemberQrCode(canvasEl, data) {
  const payload = JSON.stringify(data);
  return new Promise((resolve, reject) => {
    if (!window.QRCode) {
      reject(new Error('QR code library did not load.'));
      return;
    }
    window.QRCode.toCanvas(
      canvasEl,
      payload,
      { width: 140, margin: 1, color: { dark: '#2E0854', light: '#FFFFFF' } },
      (err) => (err ? reject(err) : resolve())
    );
  });
}

/** Builds the standard QR payload shape used across the app. */
export function buildQrPayload(member) {
  return {
    id: member.id,
    membership_id: member.membership_number,
    name: member.full_name,
    branch: member.branch,
    phone: member.phone,
    issue_date: member.issue_date,
  };
}
