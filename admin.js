// GWGM — Admin dashboard logic (ES module)
//
// Security model:
//  - The frontend NEVER holds the Supabase service role key.
//  - All admin reads/writes call the `admin-actions` Supabase Edge Function,
//    which checks the shared admin password (stored as a server-side secret)
//    and only then uses the service role key to touch the database.
//  - The password is kept in sessionStorage only (cleared when the tab
//    closes) and sent as a header on each request — it is never written to
//    localStorage or the repo.
import { showToast, setButtonLoading } from './utils.js';

const FN_URL = window.GWGM_CONFIG.ADMIN_FUNCTION_URL;
const PW_KEY = 'gwgm_admin_session_pw';
const PAGE_SIZE = 20;

let state = { page: 1, total: 0, search: '', branch: '', sort: 'created_at-desc', rows: [] };

// ---- Elements ----
const loginGate = document.getElementById('loginGate');
const loginForm = document.getElementById('loginForm');
const loginError = document.getElementById('loginError');
const adminApp = document.getElementById('adminApp');

// ---- Auth ----
function getPassword() { return sessionStorage.getItem(PW_KEY); }
function setPassword(pw) { sessionStorage.setItem(PW_KEY, pw); }
function clearPassword() { sessionStorage.removeItem(PW_KEY); }

async function adminFetch(path, options = {}) {
  const res = await fetch(`${FN_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'x-admin-password': getPassword() || '',
      ...(options.headers || {}),
    },
  });
  if (res.status === 401) {
    clearPassword();
    showAdminApp(false);
    throw new Error('Session expired. Please sign in again.');
  }
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(body.message || 'Request failed.');
  return body;
}

function showAdminApp(isLoggedIn) {
  loginGate.hidden = isLoggedIn;
  adminApp.hidden = !isLoggedIn;
}

loginForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  loginError.textContent = '';
  const pw = document.getElementById('adminPassword').value;
  const btn = document.getElementById('loginBtn');
  setButtonLoading(btn, true, 'Signing in…');
  try {
    setPassword(pw);
    await adminFetch('/stats'); // acts as a password check
    showAdminApp(true);
    await bootDashboard();
  } catch (err) {
    clearPassword();
    loginError.textContent = 'Incorrect password. Please try again.';
  } finally {
    setButtonLoading(btn, false);
  }
});

document.getElementById('logoutBtn').addEventListener('click', () => {
  clearPassword();
  showAdminApp(false);
});

// If a password is already in this tab's session, skip straight to the dashboard.
if (getPassword()) {
  showAdminApp(true);
  bootDashboard().catch(() => showAdminApp(false));
} else {
  showAdminApp(false);
}

// ---- Dashboard boot ----
async function bootDashboard() {
  await Promise.all([loadStats(), loadMembers()]);
}

async function loadStats() {
  try {
    const stats = await adminFetch('/stats');
    document.getElementById('statTotal').textContent = stats.total ?? '—';
    document.getElementById('statBranches').textContent = stats.branches ?? '—';
    document.getElementById('statToday').textContent = stats.today ?? '—';
    document.getElementById('statMonth').textContent = stats.month ?? '—';

    const branchFilter = document.getElementById('branchFilter');
    branchFilter.innerHTML = '<option value="">All Branches</option>' +
      (stats.branchList || []).map((b) => `<option value="${b}">${b}</option>`).join('');
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function loadMembers() {
  const tbody = document.getElementById('membersTbody');
  tbody.innerHTML = '<tr><td colspan="8" class="table-empty">Loading members…</td></tr>';
  try {
    const params = new URLSearchParams({
      search: state.search, branch: state.branch, sort: state.sort,
      page: state.page, pageSize: PAGE_SIZE,
    });
    const { rows, total } = await adminFetch(`/members?${params}`);
    state.rows = rows; state.total = total;
    renderTable(rows);
    renderPagination();
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="8" class="table-empty">${err.message}</td></tr>`;
  }
}

function renderTable(rows) {
  const tbody = document.getElementById('membersTbody');
  if (!rows.length) {
    tbody.innerHTML = '<tr><td colspan="8" class="table-empty">No members found.</td></tr>';
    return;
  }
  tbody.innerHTML = rows.map((m) => `
    <tr>
      <td><img class="thumb" src="${m.profile_photo_url || ''}" alt="" /></td>
      <td>${m.membership_number || '—'}</td>
      <td>${m.full_name}</td>
      <td>${m.branch}</td>
      <td>${m.phone}</td>
      <td>${m.position_held || '—'}</td>
      <td>${new Date(m.created_at).toLocaleDateString()}</td>
      <td>
        <button class="row-action" data-action="view" data-id="${m.id}" aria-label="View ${m.full_name}"><i data-feather="eye"></i></button>
      </td>
    </tr>
  `).join('');
  window.feather.replace();
}

function renderPagination() {
  const wrap = document.getElementById('pagination');
  const totalPages = Math.max(1, Math.ceil(state.total / PAGE_SIZE));
  let html = '';
  for (let p = 1; p <= totalPages; p++) {
    html += `<button class="${p === state.page ? 'active' : ''}" data-page="${p}">${p}</button>`;
  }
  wrap.innerHTML = html;
  wrap.querySelectorAll('button').forEach((btn) => {
    btn.addEventListener('click', () => {
      state.page = Number(btn.dataset.page);
      loadMembers();
    });
  });
}

// ---- Toolbar events ----
let searchTimeout;
document.getElementById('searchInput').addEventListener('input', (e) => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    state.search = e.target.value.trim();
    state.page = 1;
    loadMembers();
  }, 350);
});
document.getElementById('branchFilter').addEventListener('change', (e) => {
  state.branch = e.target.value;
  state.page = 1;
  loadMembers();
});
document.getElementById('sortSelect').addEventListener('change', (e) => {
  state.sort = e.target.value;
  state.page = 1;
  loadMembers();
});
document.getElementById('printListBtn').addEventListener('click', () => window.print());

// ---- Export ----
document.getElementById('exportCsvBtn').addEventListener('click', async () => {
  try {
    const { rows } = await adminFetch('/members/export');
    const csv = toCsv(rows);
    downloadBlob(csv, 'gwgm-members.csv', 'text/csv');
  } catch (err) { showToast(err.message, 'error'); }
});
document.getElementById('exportXlsxBtn').addEventListener('click', async () => {
  try {
    const { rows } = await adminFetch('/members/export');
    const ws = window.XLSX.utils.json_to_sheet(rows);
    const wb = window.XLSX.utils.book_new();
    window.XLSX.utils.book_append_sheet(wb, ws, 'Members');
    window.XLSX.writeFile(wb, 'gwgm-members.xlsx');
  } catch (err) { showToast(err.message, 'error'); }
});

function toCsv(rows) {
  if (!rows.length) return '';
  const headers = Object.keys(rows[0]);
  const escape = (v) => `"${String(v ?? '').replace(/"/g, '""')}"`;
  const lines = [headers.join(','), ...rows.map((r) => headers.map((h) => escape(r[h])).join(','))];
  return lines.join('\n');
}
function downloadBlob(content, filename, mime) {
  const blob = new Blob([content], { type: mime });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = filename;
  link.click();
  URL.revokeObjectURL(link.href);
}

// ---- View / Edit / Delete modal ----
const modal = document.getElementById('memberModal');
const editForm = document.getElementById('editForm');
let activeMemberId = null;

document.getElementById('membersTbody').addEventListener('click', (e) => {
  const btn = e.target.closest('button[data-action="view"]');
  if (!btn) return;
  const member = state.rows.find((m) => String(m.id) === btn.dataset.id);
  if (member) openModal(member);
});

const EDITABLE_FIELDS = [
  ['full_name', 'Full Name', 'text'], ['gender', 'Gender', 'text'],
  ['phone', 'Phone', 'tel'], ['whatsapp', 'WhatsApp', 'tel'],
  ['email', 'Email', 'email'], ['occupation', 'Occupation', 'text'],
  ['residential_address', 'Address', 'text'], ['state', 'State', 'text'],
  ['country', 'Country', 'text'], ['branch', 'Branch', 'text'],
  ['position_held', 'Position', 'text'],
];

function openModal(member) {
  activeMemberId = member.id;
  document.getElementById('modalTitle').textContent = `${member.full_name} — ${member.membership_number}`;
  editForm.innerHTML = EDITABLE_FIELDS.map(([field, label, type]) => `
    <label>${label}
      <input type="${type}" name="${field}" value="${(member[field] ?? '').toString().replace(/"/g, '&quot;')}" />
    </label>
  `).join('');
  modal.hidden = false;
}
document.getElementById('closeModalBtn').addEventListener('click', () => { modal.hidden = true; });
modal.addEventListener('click', (e) => { if (e.target === modal) modal.hidden = true; });

document.getElementById('saveEditBtn').addEventListener('click', async () => {
  const btn = document.getElementById('saveEditBtn');
  const formData = new FormData(editForm);
  const updates = Object.fromEntries(formData.entries());
  setButtonLoading(btn, true, 'Saving…');
  try {
    await adminFetch(`/members/${activeMemberId}`, { method: 'PUT', body: JSON.stringify(updates) });
    showToast('Member updated successfully.', 'success');
    modal.hidden = true;
    await Promise.all([loadStats(), loadMembers()]);
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    setButtonLoading(btn, false);
  }
});

document.getElementById('deleteMemberBtn').addEventListener('click', async () => {
  if (!confirm('Delete this member permanently? This cannot be undone.')) return;
  const btn = document.getElementById('deleteMemberBtn');
  setButtonLoading(btn, true, 'Deleting…');
  try {
    await adminFetch(`/members/${activeMemberId}`, { method: 'DELETE' });
    showToast('Member deleted.', 'success');
    modal.hidden = true;
    await Promise.all([loadStats(), loadMembers()]);
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    setButtonLoading(btn, false);
  }
});
