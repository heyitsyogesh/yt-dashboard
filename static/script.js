/**
 * script.js
 * ─────────
 * Handles the "Check Updates" button, fetches /check from the backend,
 * and renders channel cards dynamically.
 * The API key is NEVER here — it lives only on the Python backend.
 */

/* ── Set today's date in the hero ──────────────────────────────── */
(function setDate() {
  const el = document.getElementById('today-date');
  if (!el) return;
  const opts = { weekday:'long', year:'numeric', month:'long', day:'numeric' };
  el.textContent = new Date().toLocaleDateString('en-IN', opts);
})();


/* ── Main check function ────────────────────────────────────────── */
async function runCheck() {
  const btn     = document.getElementById('check-btn');
  const icon    = document.getElementById('btn-icon');
  const label   = document.getElementById('btn-label');
  const results = document.getElementById('results');
  const errBox  = document.getElementById('error-box');

  // — Loading state —
  btn.disabled = true;
  icon.classList.add('spinning');
  label.textContent = 'Checking…';
  results.style.display = 'none';
  errBox.style.display  = 'none';

  try {
    const res  = await fetch('/check');
    const data = await res.json();

    if (!data.ok) throw new Error(data.error || 'Unknown error from server.');

    renderResults(data);

  } catch (err) {
    document.getElementById('error-msg').textContent = err.message;
    errBox.style.display = 'block';

  } finally {
    // — Restore button —
    btn.disabled = false;
    icon.classList.remove('spinning');
    label.textContent = 'Check Updates';
  }
}


/* ── Render all channel cards ───────────────────────────────────── */
function renderResults(data) {
  const results   = document.getElementById('results');
  const grid      = document.getElementById('channels-grid');
  const lastWrap  = document.getElementById('last-checked-wrap');
  const lastTime  = document.getElementById('last-checked-time');

  // Update summary bar
  let totalVideos = 0;
  let activeCount = 0;
  let silentCount = 0;

  data.channels.forEach(ch => {
    totalVideos += ch.videos.length;
    if (ch.has_videos)   activeCount++;
    else if (!ch.error)  silentCount++;
  });

  document.getElementById('s-total').textContent  = totalVideos;
  document.getElementById('s-active').textContent = activeCount;
  document.getElementById('s-silent').textContent = silentCount;

  // Last checked timestamp
  lastWrap.style.display = 'flex';
  lastTime.textContent   = data.checked_at;

  // Render cards
  grid.innerHTML = '';
  data.channels.forEach((ch, i) => {
    const card = buildChannelCard(ch, i);
    grid.appendChild(card);
  });

  results.style.display = 'block';

  // Smooth scroll to results
  results.scrollIntoView({ behavior: 'smooth', block: 'start' });
}


/* ── Build a single channel card ────────────────────────────────── */
function buildChannelCard(ch, index) {
  const card = document.createElement('div');
  card.className = 'ch-card';
  card.style.cssText      = `--ch-color:${ch.color}; animation-delay:${index * 55}ms`;
  card.style.setProperty('--ch-color', ch.color);

  // Badge
  let badgeClass, badgeText;
  if (ch.error) {
    badgeClass = 'error'; badgeText = 'Error';
  } else if (ch.has_videos) {
    badgeClass = 'ok';
    badgeText  = ch.videos.length === 1 ? '1 video' : `${ch.videos.length} videos`;
  } else {
    badgeClass = 'empty'; badgeText = 'No upload';
  }

  // Header
  const header = `
    <div class="ch-header">
      <div class="ch-dot"></div>
      <div class="ch-name">${escHtml(ch.name)}</div>
      <span class="ch-badge ${badgeClass}">${badgeText}</span>
    </div>`;

  // Body
  let body;
  if (ch.error) {
    body = `<div class="ch-err">⚠ ${escHtml(ch.error)}</div>`;

  } else if (ch.has_videos) {
    const rows = ch.videos.map(v => `
      <a class="video-row" href="${escHtml(v.link)}" target="_blank" rel="noopener">
        <img class="video-thumb"
             src="${escHtml(v.thumbnail)}"
             alt=""
             loading="lazy"
             onerror="this.style.opacity='0'">
        <div class="video-info">
          <div class="video-title">${escHtml(v.title)}</div>
          <div class="video-meta">
            <span class="video-time">🕐 ${escHtml(v.time)}</span>
            <span class="watch-tag">▶ Watch</span>
          </div>
        </div>
      </a>`).join('');
    body = `<div class="ch-videos">${rows}</div>`;

  } else {
    body = `<div class="ch-empty">📭 No video uploaded today</div>`;
  }

  card.innerHTML = header + body;
  return card;
}


/* ── Utility: escape HTML to prevent XSS ───────────────────────── */
function escHtml(str) {
  return String(str ?? '')
    .replace(/&/g,  '&amp;')
    .replace(/</g,  '&lt;')
    .replace(/>/g,  '&gt;')
    .replace(/"/g,  '&quot;')
    .replace(/'/g,  '&#39;');
}
