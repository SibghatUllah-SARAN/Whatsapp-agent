const API_BASE = (window.API_BASE_URL || "").replace(/\/$/, "");
const rows = document.getElementById("messageRows");
const notice = document.getElementById("notice");
let messages = [];

function dashboardKey() {
  return sessionStorage.getItem("wa_dashboard_key") || "";
}
function showNotice(text, error=false) {
  notice.textContent = text;
  notice.className = error ? "notice error" : "notice";
}
function escapeHTML(value) {
  return String(value ?? "").replace(/[&<>"']/g, ch => ({
    "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"
  }[ch]));
}
function renderMessages() {
  const query = document.getElementById("searchInput").value.toLowerCase();
  const filtered = messages.filter(m =>
    String(m.phone).toLowerCase().includes(query) ||
    String(m.body).toLowerCase().includes(query)
  );
  document.getElementById("totalCount").textContent = messages.length;
  document.getElementById("inCount").textContent = messages.filter(m=>m.direction==="inbound").length;
  document.getElementById("outCount").textContent = messages.filter(m=>m.direction==="outbound").length;
  if (!filtered.length) {
    rows.innerHTML = '<tr><td colspan="4" class="empty">No matching messages.</td></tr>';
    return;
  }
  rows.innerHTML = filtered.map(m => `
    <tr>
      <td>${escapeHTML(m.phone)}</td>
      <td class="message">${escapeHTML(m.body)}</td>
      <td><span class="direction ${m.direction==="inbound"?"inbound":"outbound"}">${escapeHTML(m.direction)}</span></td>
      <td>${escapeHTML(m.created_at)}</td>
    </tr>`).join("");
}
async function loadMessages() {
  if (!API_BASE || API_BASE.includes("YOUR-BACKEND-URL")) {
    showNotice("Set your deployed backend URL in static/config.js first.", true);
    return;
  }
  if (!dashboardKey()) {
    showNotice("Click “Set dashboard key” and enter the DASHBOARD_API_KEY from your backend environment.");
    return;
  }
  showNotice("Loading message history…");
  try {
    const response = await fetch(`${API_BASE}/api/messages?limit=150`, {
      headers: {"X-Dashboard-Key": dashboardKey()}
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Could not load messages.");
    messages = data.messages || [];
    renderMessages();
    showNotice(`Loaded ${messages.length} message(s).`);
  } catch (err) {
    showNotice(err.message + " Check your backend URL and CORS settings.", true);
  }
}
document.getElementById("refreshBtn").addEventListener("click", loadMessages);
document.getElementById("keyBtn").addEventListener("click", () => {
  const key = prompt("Enter the dashboard API key:");
  if (key !== null) {
    sessionStorage.setItem("wa_dashboard_key", key.trim());
    loadMessages();
  }
});
document.getElementById("searchInput").addEventListener("input", renderMessages);
loadMessages();
