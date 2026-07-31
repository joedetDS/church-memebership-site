// GWGM — Shared utility helpers (ES module)

/** Show a toast notification. type: 'success' | 'error' | 'info' */
export function showToast(message, type = 'info', duration = 4000) {
  let container = document.getElementById('toastContainer');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toastContainer';
    container.setAttribute('role', 'status');
    container.setAttribute('aria-live', 'polite');
    document.body.appendChild(container);
  }
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), duration);
}

/** Toggle a button into a loading state with a spinner + disabled state. */
export function setButtonLoading(button, isLoading, loadingLabel = 'Please wait…') {
  if (isLoading) {
    button.dataset.originalHtml = button.innerHTML;
    button.disabled = true;
    button.innerHTML = `<span class="spinner" aria-hidden="true"></span><span>${loadingLabel}</span>`;
  } else {
    button.disabled = false;
    if (button.dataset.originalHtml) button.innerHTML = button.dataset.originalHtml;
  }
}

export function isValidEmail(value) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim());
}

export function isValidPhone(value) {
  return /^[0-9+\s()-]{7,20}$/.test(value.trim());
}

export function isNonEmpty(value) {
  return typeof value === 'string' && value.trim().length > 0;
}

/** Reads a File object and resolves to a compressed JPEG Blob (max dimension + quality). */
export function compressImage(file, maxDimension = 800, quality = 0.82) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    const reader = new FileReader();
    reader.onerror = () => reject(new Error('Could not read the selected image.'));
    reader.onload = (e) => { img.src = e.target.result; };
    img.onload = () => {
      let { width, height } = img;
      if (width > height && width > maxDimension) {
        height = Math.round((height * maxDimension) / width);
        width = maxDimension;
      } else if (height > maxDimension) {
        width = Math.round((width * maxDimension) / height);
        height = maxDimension;
      }
      const canvas = document.createElement('canvas');
      canvas.width = width;
      canvas.height = height;
      canvas.getContext('2d').drawImage(img, 0, 0, width, height);
      canvas.toBlob(
        (blob) => (blob ? resolve(blob) : reject(new Error('Image compression failed.'))),
        'image/jpeg',
        quality
      );
    };
    img.onerror = () => reject(new Error('The selected file is not a valid image.'));
    reader.readAsDataURL(file);
  });
}

/** Formats an ISO date string into a readable "31 Jul 2026" format. */
export function formatDate(isoString) {
  const d = new Date(isoString);
  return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
}

/** Basic online/offline guard used before network operations. */
export function ensureOnline() {
  if (!navigator.onLine) {
    showToast('You appear to be offline. Please check your connection and try again.', 'error');
    return false;
  }
  return true;
}
