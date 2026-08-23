const REFRESH_INTERVAL_MS = 15000;

let allParticipants = [];
let refreshTimer = null;

const els = {
  statApproved: document.getElementById("statApproved"),
  statRejected: document.getElementById("statRejected"),
  statPending: document.getElementById("statPending"),
  statTotal: document.getElementById("statTotal"),
  participantsBody: document.getElementById("participantsBody"),
  approvedCount: document.getElementById("approvedCount"),
  emptyState: document.getElementById("emptyState"),
  lastUpdated: document.getElementById("lastUpdated"),
  searchInput: document.getElementById("searchInput"),
  methodFilter: document.getElementById("methodFilter"),
  downloadPdfBtn: document.getElementById("downloadPdfBtn"),
  exportCsvBtn: document.getElementById("exportCsvBtn"),
  refreshBtn: document.getElementById("refreshBtn"),
  toast: document.getElementById("toast"),
};

function formatDate(isoString) {
  if (!isoString) return "—";
  const date = new Date(isoString);
  return date.toLocaleString(undefined, {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatPaymentFor(value) {
  if (!value) return "—";
  return value === "self" ? "Self" : "Other Person";
}

function showToast(message, type = "success") {
  els.toast.textContent = message;
  els.toast.className = `toast ${type}`;
  els.toast.classList.remove("hidden");
  clearTimeout(showToast._timer);
  showToast._timer = setTimeout(() => {
    els.toast.classList.add("hidden");
  }, 3200);
}

function getFilteredParticipants(participants = allParticipants) {
  const query = els.searchInput.value.trim().toLowerCase();
  const method = els.methodFilter.value;
  return participants.filter((p) => {
    if (method && p.payment_method !== method) return false;
    if (!query) return true;
    const haystack = [
      p.participant_name,
      p.phone,
      p.payment_method,
      String(p.participant_number || ""),
    ]
      .join(" ")
      .toLowerCase();
    return haystack.includes(query);
  });
}

function renderTable(participants) {
  const filtered = getFilteredParticipants(participants);

  els.approvedCount.textContent = `${filtered.length} user${filtered.length === 1 ? "" : "s"}`;

  if (filtered.length === 0) {
    els.participantsBody.innerHTML = "";
    els.emptyState.classList.remove("hidden");
    document.querySelector(".table-wrap").classList.add("hidden");
    return;
  }

  els.emptyState.classList.add("hidden");
  document.querySelector(".table-wrap").classList.remove("hidden");

  els.participantsBody.innerHTML = filtered
    .map(
      (p, index) => `
      <tr>
        <td>${index + 1}</td>
        <td>
          <span class="participant-no">
            #${String(p.participant_number || 0).padStart(3, "0")}
          </span>
        </td>
        <td><strong>${escapeHtml(p.participant_name)}</strong></td>
        <td>${escapeHtml(p.phone)}</td>
        <td><span class="method-tag">${escapeHtml((p.payment_method || "—").toUpperCase())}</span></td>
        <td>${formatPaymentFor(p.payment_for)}</td>
        <td>${formatDate(p.verified_at)}</td>
      </tr>
    `
    )
    .join("");
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text ?? "";
  return div.innerHTML;
}

async function fetchStats() {
  const response = await fetch("/api/stats");
  if (!response.ok) throw new Error("Failed to load stats");
  return response.json();
}

async function fetchApprovedUsers() {
  const response = await fetch("/api/approved-users");
  if (!response.ok) throw new Error("Failed to load approved users");
  return response.json();
}

async function refreshDashboard() {
  try {
    const [stats, approved] = await Promise.all([
      fetchStats(),
      fetchApprovedUsers(),
    ]);

    els.statApproved.textContent = stats.approved;
    els.statRejected.textContent = stats.rejected;
    els.statPending.textContent = stats.pending;
    els.statTotal.textContent = stats.total_users;

    allParticipants = approved.participants || [];
    renderTable(allParticipants);

    els.lastUpdated.textContent = `Last updated: ${formatDate(stats.updated_at)}`;
  } catch (error) {
    console.error(error);
    showToast("Could not refresh dashboard. Is the server running?", "error");
  }
}

function escapeCsv(value) {
  const text = String(value ?? "");
  return `"${text.replaceAll('"', '""')}"`;
}

function exportCsv() {
  const rows = getFilteredParticipants();
  if (!rows.length) {
    showToast("There are no matching participants to export", "error");
    return;
  }

  const headers = ["Participant No.", "Full Name", "Phone", "Payment Method", "Payment For", "Approved On"];
  const csv = [headers, ...rows.map((p) => [
    p.participant_number ? `#${String(p.participant_number).padStart(3, "0")}` : "",
    p.participant_name,
    p.phone,
    (p.payment_method || "").toUpperCase(),
    formatPaymentFor(p.payment_for),
    formatDate(p.verified_at),
  ])].map((row) => row.map(escapeCsv).join(",")).join("\n");

  const url = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8" }));
  const link = document.createElement("a");
  link.href = url;
  link.download = `ethio-car-equb-approved-${new Date().toISOString().slice(0, 10)}.csv`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
  showToast(`${rows.length} participant${rows.length === 1 ? "" : "s"} exported to CSV`);
}

async function downloadPdf() {
  try {
    els.downloadPdfBtn.disabled = true;
    els.downloadPdfBtn.textContent = "Generating…";

    const response = await fetch("/api/download-pdf");
    if (!response.ok) {
      throw new Error("PDF download failed");
    }

    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `ethio-car-equb-approved-${new Date().toISOString().slice(0, 10)}.pdf`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);

    showToast("PDF downloaded successfully");
  } catch (error) {
    console.error(error);
    showToast(error.message || "Failed to download PDF", "error");
  } finally {
    els.downloadPdfBtn.disabled = false;
    els.downloadPdfBtn.innerHTML = `
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
      Download PDF
    `;
  }
}

els.searchInput.addEventListener("input", () => renderTable(allParticipants));
els.methodFilter.addEventListener("change", () => renderTable(allParticipants));
els.exportCsvBtn.addEventListener("click", exportCsv);
els.downloadPdfBtn.addEventListener("click", downloadPdf);
els.refreshBtn.addEventListener("click", refreshDashboard);

refreshDashboard();
refreshTimer = setInterval(refreshDashboard, REFRESH_INTERVAL_MS);

window.addEventListener("beforeunload", () => {
  if (refreshTimer) clearInterval(refreshTimer);
});
