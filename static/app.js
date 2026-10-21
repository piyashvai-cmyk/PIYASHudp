let currentCategory = '2_level';
let allAccounts = [];
let activeLogAccountId = null;
let logPollInterval = null;

// Initialization
document.addEventListener('DOMContentLoaded', () => {
  fetchStats();
  fetchAccounts();
  setInterval(fetchStats, 4000);
  setInterval(fetchAccounts, 3000);
});

async function fetchStats() {
  try {
    const res = await fetch('/api/stats');
    if (!res.ok) return;
    const data = await res.json();
    document.getElementById('statTotal').innerText = data.total_accounts;
    document.getElementById('statRunning').innerText = data.running_accounts;
    document.getElementById('statL2Running').innerText = `${data.level_2_running} / ${data.level_2_total}`;
    document.getElementById('statL3Running').innerText = `${data.level_3_running} / ${data.level_3_total}`;
    document.getElementById('countL2').innerText = data.level_2_total;
    document.getElementById('countL3').innerText = data.level_3_total;
    document.getElementById('serverClock').innerText = data.server_time || 'LIVE';
  } catch (err) {
    console.error('Error fetching stats:', err);
  }
}

async function fetchAccounts() {
  try {
    const res = await fetch('/api/accounts');
    if (!res.ok) return;
    allAccounts = await res.json();
    renderAccounts();
  } catch (err) {
    console.error('Error fetching accounts:', err);
  }
}

function switchCategory(category) {
  currentCategory = category;
  document.getElementById('tabL2').classList.toggle('active', category === '2_level');
  document.getElementById('tabL3').classList.toggle('active', category === '3_level');

  const titleEl = document.getElementById('categoryTitle');
  const descEl = document.getElementById('categoryDesc');
  const modalSub = document.getElementById('modalCategorySubtitle');

  if (category === '2_level') {
    titleEl.innerText = '2 Level Accounts';
    descEl.innerText = 'Standard bot session (Update check, OAuth token grant, TCP chat/online socket, and standby invite handlers).';
    modalSub.innerText = 'Target: 2 Level Standard';
  } else {
    titleEl.innerText = '3 Level Accounts (Auto Match Pump)';
    descEl.innerText = 'Automated continuous matchmaking loop (0319 lobby-clear + Lone Wolf 43 match-start every 5.7s with independent UDP handlers).';
    modalSub.innerText = 'Target: 3 Level Lone Wolf Pump';
  }

  renderAccounts();
}

function renderAccounts() {
  const container = document.getElementById('accountsGrid');
  const filtered = allAccounts.filter(acc => acc.category === currentCategory);

  if (filtered.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <p>No accounts configured under <strong>${currentCategory === '2_level' ? '2 Level' : '3 Level'}</strong>.</p>
        <button class="btn btn-primary" style="margin-top: 14px;" onclick="openCreateModal()">
          Create First Account
        </button>
      </div>
    `;
    return;
  }

  container.innerHTML = filtered.map(acc => {
    const isRunning = acc.status === 'RUNNING';
    const statusClass = acc.status.toLowerCase();

    return `
      <div class="account-card ${statusClass}">
        <div class="card-top">
          <div>
            <h4 class="card-name">${escapeHtml(acc.name)}</h4>
            <div class="card-uid">UID: <strong>${acc.uid}</strong></div>
          </div>
          <span class="status-badge ${acc.status}">${acc.status}</span>
        </div>

        <div class="card-meta">
          <span>CAT: ${acc.category === '2_level' ? '2 Level' : '3 Level Pump'}</span>
          <span>PASS: ••••••••</span>
        </div>

        <div class="card-actions">
          ${isRunning ? `
            <button class="btn btn-sm btn-stop" onclick="stopAccount('${acc.id}')">
              ■ Stop
            </button>
          ` : `
            <button class="btn btn-sm btn-start" onclick="startAccount('${acc.id}')">
              ▶ Start
            </button>
          `}
          <button class="btn btn-sm btn-logs" onclick="openLogModal('${acc.id}', '${escapeHtml(acc.name)}', ${acc.uid})">
            Live Terminal
          </button>
          <button class="btn btn-sm btn-delete" onclick="deleteAccount('${acc.id}')" title="Delete account">
            🗑
          </button>
        </div>
      </div>
    `;
  }).join('');
}

function openCreateModal() {
  const modal = document.getElementById('createModal');
  const modalSub = document.getElementById('modalCategorySubtitle');
  modalSub.innerText = `Target: ${currentCategory === '2_level' ? '2 Level Standard' : '3 Level Lone Wolf Pump'}`;
  
  // Set helpful default placeholder suggestion
  if (currentCategory === '2_level') {
    document.getElementById('accUid').value = '';
    document.getElementById('accPassword').value = '';
    document.getElementById('accName').value = '';
  } else {
    document.getElementById('accUid').value = '';
    document.getElementById('accPassword').value = '';
    document.getElementById('accName').value = '';
  }

  modal.classList.add('open');
}

function closeCreateModal() {
  document.getElementById('createModal').classList.remove('open');
}

function togglePassVisibility() {
  const passInput = document.getElementById('accPassword');
  passInput.type = passInput.type === 'password' ? 'text' : 'password';
}

async function handleCreateAccount(e) {
  e.preventDefault();
  const uid = parseInt(document.getElementById('accUid').value.trim(), 10);
  const password = document.getElementById('accPassword').value.trim();
  const name = document.getElementById('accName').value.trim();
  const autoStart = document.getElementById('accAutoStart').checked;

  if (!uid || !password) {
    alert('Please enter both UID and Password');
    return;
  }

  const submitBtn = document.getElementById('btnSubmitAccount');
  submitBtn.disabled = true;
  submitBtn.innerText = 'Creating...';

  try {
    const res = await fetch('/api/accounts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        category: currentCategory,
        uid: uid,
        password: password,
        name: name,
        auto_start: autoStart
      })
    });

    if (res.ok) {
      closeCreateModal();
      document.getElementById('createAccountForm').reset();
      await fetchAccounts();
      await fetchStats();
    } else {
      const err = await res.json();
      alert(`Error creating account: ${err.detail || 'Unknown error'}`);
    }
  } catch (err) {
    alert(`Connection error: ${err.message}`);
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerText = 'Start Account';
  }
}

async function startAccount(accountId) {
  try {
    const res = await fetch(`/api/accounts/${accountId}/start`, { method: 'POST' });
    if (!res.ok) {
      const err = await res.json();
      alert(`Cannot start worker: ${err.detail || 'Unknown'}`);
    }
    await fetchAccounts();
    await fetchStats();
  } catch (err) {
    alert(`Failed to start: ${err.message}`);
  }
}

async function stopAccount(accountId) {
  try {
    const res = await fetch(`/api/accounts/${accountId}/stop`, { method: 'POST' });
    await fetchAccounts();
    await fetchStats();
  } catch (err) {
    alert(`Failed to stop: ${err.message}`);
  }
}

async function deleteAccount(accountId) {
  if (!confirm('Are you sure you want to delete this account configuration? Any running worker will be stopped.')) {
    return;
  }
  try {
    const res = await fetch(`/api/accounts/${accountId}`, { method: 'DELETE' });
    if (res.ok) {
      await fetchAccounts();
      await fetchStats();
    }
  } catch (err) {
    alert(`Failed to delete: ${err.message}`);
  }
}

// Log Terminal Modal
function openLogModal(accountId, name, uid) {
  activeLogAccountId = accountId;
  document.getElementById('logModalTitle').innerText = `${name} [${currentCategory === '2_level' ? '2 Level' : '3 Level'}]`;
  document.getElementById('logModalSubtitle').innerText = `UID: ${uid} | ID: ${accountId}`;
  document.getElementById('logModal').classList.add('open');
  
  fetchLogs();
  if (logPollInterval) clearInterval(logPollInterval);
  logPollInterval = setInterval(fetchLogs, 1500);
}

function closeLogModal() {
  document.getElementById('logModal').classList.remove('open');
  if (logPollInterval) clearInterval(logPollInterval);
  activeLogAccountId = null;
}

async function fetchLogs() {
  if (!activeLogAccountId) return;
  try {
    const res = await fetch(`/api/accounts/${activeLogAccountId}/logs`);
    if (!res.ok) return;
    const data = await res.json();
    const terminal = document.getElementById('terminalLogs');
    const logs = data.logs || [];
    
    if (logs.length === 0) {
      terminal.innerHTML = '<div class="log-line text-muted">No logs recorded yet. Start the process to view real-time events.</div>';
    } else {
      terminal.innerHTML = logs.map(l => `<div class="log-line">${escapeHtml(l)}</div>`).join('');
      terminal.scrollTop = terminal.scrollHeight;
    }
  } catch (err) {
    console.error('Error fetching logs:', err);
  }
}

function copyLogs() {
  const terminal = document.getElementById('terminalLogs');
  navigator.clipboard.writeText(terminal.innerText);
  alert('Logs copied to clipboard!');
}

function clearLocalLogs() {
  document.getElementById('terminalLogs').innerHTML = '<div class="log-line text-muted">View cleared locally.</div>';
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
