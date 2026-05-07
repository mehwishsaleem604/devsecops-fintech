const API = 'http://16.170.208.184:5000';

// ── Auth helpers ──────────────────────────────────────────
function getToken() { return localStorage.getItem('ft_token'); }
function getUser()  { return JSON.parse(localStorage.getItem('ft_user') || '{}'); }
function setAuth(token, user) {
  localStorage.setItem('ft_token', token);
  localStorage.setItem('ft_user', JSON.stringify(user));
}
function clearAuth() {
  localStorage.removeItem('ft_token');
  localStorage.removeItem('ft_user');
}

// ── Alert helpers ─────────────────────────────────────────
function showAlert(id, type, msg) {
  const el = document.getElementById(id);
  if (!el) return;
  el.className = 'alert alert-' + type + ' show';
  el.innerHTML = (type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ') + ' ' + msg;
  setTimeout(() => el.classList.remove('show'), 5000);
}

function setLoading(btnId, spinnerId, loading) {
  const btn = document.getElementById(btnId);
  const sp  = document.getElementById(spinnerId);
  if (btn) btn.disabled = loading;
  if (sp)  sp.classList.toggle('show', loading);
}

// ── Page Navigation ───────────────────────────────────────
function showPage(name) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  const pg = document.getElementById('page-' + name);
  const nv = document.getElementById('nav-' + name);
  if (pg) pg.classList.add('active');
  if (nv) nv.classList.add('active');
  document.getElementById('topbar-title').textContent = {
    dashboard: 'Dashboard',
    transfer: 'Transfer Funds',
    history: 'Payment History',
    users: 'Users',
    security: 'Security Vulnerabilities',
    pipeline: 'CI/CD Pipeline'
  }[name] || name;
  document.getElementById('topbar-sub').textContent = {
    dashboard: 'Welcome to your FinTech dashboard',
    transfer: 'Send money securely via JWT-protected API',
    history: 'View all your transaction history',
    users: 'All registered accounts in the system',
    security: 'Intentional vulnerabilities for demo — caught by pipeline',
    pipeline: 'GitHub Actions — DevSecOps CI/CD Status'
  }[name] || '';
  if (name === 'history') loadHistory();
}

// ── Quick fill on login page ──────────────────────────────
function fillCreds(username) {
  document.getElementById('username').value = username;
  document.getElementById('password').value = username + '123';
}

// ── LOGIN ─────────────────────────────────────────────────
async function doLogin() {
  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value.trim();
  if (!username || !password) { showAlert('login-alert', 'error', 'Please enter username and password.'); return; }
  setLoading('login-btn', 'login-spinner', true);
  try {
    const res = await fetch(API + '/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    const data = await res.json();
    if (res.ok && data.token) {
      setAuth(data.token, { username, user_id: data.user_id });
      window.location.href = 'dashboard.html';
    } else {
      showAlert('login-alert', 'error', data.error || 'Invalid credentials.');
    }
  } catch {
    showAlert('login-alert', 'error', 'Cannot reach API. Check if EC2 container is running.');
  }
  setLoading('login-btn', 'login-spinner', false);
}

// ── REGISTER ──────────────────────────────────────────────
async function doRegister() {
  const username = document.getElementById('reg-username').value.trim();
  const password = document.getElementById('reg-password').value.trim();
  const email    = document.getElementById('reg-email').value.trim();
  if (!username || !password || !email) { showAlert('register-alert', 'error', 'All fields required.'); return; }
  setLoading('reg-btn', 'reg-spinner', true);
  try {
    const res = await fetch(API + '/api/v1/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password, email })
    });
    const data = await res.json();
    if (res.ok) {
      showAlert('register-alert', 'success', 'Account created! You can now login.');
      document.getElementById('reg-username').value = '';
      document.getElementById('reg-password').value = '';
      document.getElementById('reg-email').value = '';
    } else {
      showAlert('register-alert', 'error', data.error || 'Registration failed.');
    }
  } catch {
    showAlert('register-alert', 'error', 'Cannot reach API.');
  }
  setLoading('reg-btn', 'reg-spinner', false);
}

// ── DASHBOARD init ────────────────────────────────────────
function initDashboard() {
  const token = getToken();
  if (!token) { window.location.href = 'index.html'; return; }
  const user = getUser();
  document.getElementById('sidebar-username').textContent = user.username || 'User';
  document.getElementById('sidebar-userid').textContent = 'ID: ' + (user.user_id || '?');
  document.getElementById('user-avatar-text').textContent = (user.username || 'U').charAt(0).toUpperCase();
  checkHealth();
  showPage('dashboard');
}

// ── HEALTH CHECK ──────────────────────────────────────────
async function checkHealth() {
  try {
    const res = await fetch(API + '/health');
    const data = await res.json();
    const el = document.getElementById('health-status');
    if (res.ok && data.status === 'healthy') {
      el.innerHTML = '<div class="status-dot"></div> API Healthy — ' + API + '/health — v' + data.version;
      el.parentElement.style.borderColor = 'rgba(16,185,129,0.3)';
    }
  } catch {
    const el = document.getElementById('health-status');
    el.textContent = '✕ API Unreachable — ' + API;
    el.parentElement.style.background = 'rgba(239,68,68,0.1)';
    el.parentElement.style.borderColor = 'rgba(239,68,68,0.3)';
    el.style.color = '#f87171';
  }
}

// ── LOGOUT ────────────────────────────────────────────────
function doLogout() {
  clearAuth();
  window.location.href = 'index.html';
}

// ── TRANSFER ─────────────────────────────────────────────
function updateSummary() {
  const amount = parseFloat(document.getElementById('xfer-amount').value) || 0;
  document.getElementById('summary-amount').textContent = '$' + amount.toFixed(2);
  document.getElementById('summary-fee').textContent = '$0.00';
  document.getElementById('summary-total').textContent = '$' + amount.toFixed(2);
}

async function doTransfer() {
  const receiver_id  = parseInt(document.getElementById('xfer-receiver').value);
  const amount       = parseFloat(document.getElementById('xfer-amount').value);
  const card_number  = document.getElementById('xfer-card').value.trim();
  const cvv          = document.getElementById('xfer-cvv').value.trim();
  const token        = getToken();

  if (!receiver_id || !amount || !card_number || !cvv) {
    showAlert('transfer-alert', 'error', 'All fields are required.');
    return;
  }
  if (amount <= 0) { showAlert('transfer-alert', 'error', 'Amount must be greater than 0.'); return; }
  if (card_number.length < 16) { showAlert('transfer-alert', 'error', 'Invalid card number.'); return; }

  setLoading('transfer-btn', 'transfer-spinner', true);
  try {
    const res = await fetch(API + '/api/v1/payments/transfer', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
      },
      body: JSON.stringify({ receiver_id, amount, card_number, cvv })
    });
    const data = await res.json();
    if (res.ok) {
      showAlert('transfer-alert', 'success', 'Transfer of $' + amount.toFixed(2) + ' sent! Transaction ID: ' + data.transaction_id);
      document.getElementById('xfer-amount').value = '';
    } else {
      showAlert('transfer-alert', 'error', data.error || 'Transfer failed.');
    }
  } catch {
    showAlert('transfer-alert', 'error', 'Cannot reach API. Check EC2 connection.');
  }
  setLoading('transfer-btn', 'transfer-spinner', false);
}

// ── PAYMENT HISTORY ───────────────────────────────────────
async function loadHistory() {
  const token   = getToken();
  const user    = getUser();
  const user_id = user.user_id;
  if (!user_id) return;
  const container = document.getElementById('history-list');
  container.innerHTML = '<p style="color:var(--text-secondary);padding:16px">Loading...</p>';
  try {
    const res = await fetch(API + '/api/v1/payments/history/' + user_id, {
      headers: { 'Authorization': 'Bearer ' + token }
    });
    const data = await res.json();
    if (res.ok) {
      const txns = data.transactions || [];
      if (txns.length === 0) {
        container.innerHTML = '<p style="color:var(--text-secondary);padding:16px">No transactions yet.</p>';
        return;
      }
      container.innerHTML = txns.map(t => {
        const isSent = t.sender_id === user_id;
        const date   = new Date(t.timestamp * 1000).toLocaleString();
        return `
          <div class="tx-item">
            <div class="tx-avatar ${isSent ? 'sent' : 'recv'}">${isSent ? '↑' : '↓'}</div>
            <div class="tx-info">
              <div class="tx-name">${isSent ? 'Sent to User #' + t.receiver_id : 'Received from User #' + t.sender_id}</div>
              <div class="tx-date">${date} · Tx #${t.id}</div>
            </div>
            <div>
              <div class="tx-amount ${isSent ? 'sent' : 'recv'}">${isSent ? '-' : '+'}$${Number(t.amount).toFixed(2)}</div>
              <span class="badge badge-${t.status === 'completed' ? 'success' : 'pending'}" style="margin-top:4px;display:block;text-align:right">${t.status}</span>
            </div>
          </div>`;
      }).join('');
    } else {
      container.innerHTML = '<p style="color:var(--accent-red);padding:16px">' + (data.error || 'Failed to load.') + '</p>';
    }
  } catch {
    container.innerHTML = '<p style="color:var(--accent-red);padding:16px">Cannot reach API.</p>';
  }
}

// ── Enter key support ─────────────────────────────────────
document.addEventListener('keydown', e => {
  if (e.key === 'Enter') {
    if (document.getElementById('login-btn')) doLogin();
  }
});