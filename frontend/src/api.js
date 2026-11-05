/**
 * API client for Pricey backend.
 */

const API_BASE = '/api';

export async function searchProducts(query, maxPrice = null, limit = 6) {
  const res = await fetch(`${API_BASE}/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query,
      max_price: maxPrice ? parseFloat(maxPrice) : null,
      limit,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Errore durante la ricerca');
  }
  return res.json();
}

export async function lookupUrl(url) {
  const res = await fetch(`${API_BASE}/lookup-url`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Impossibile estrarre i dettagli da questo URL');
  }
  return res.json();
}

export async function getTrackedItems() {
  const res = await fetch(`${API_BASE}/tracked`);
  if (!res.ok) throw new Error('Errore nel recupero dei prodotti monitorati');
  return res.json();
}

export async function triggerPriceCheckNow() {
  const res = await fetch(`${API_BASE}/tracked/check-now`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Errore durante la verifica dei prezzi');
  return res.json();
}

export async function getTrackedItemDetail(id) {
  const res = await fetch(`${API_BASE}/tracked/${id}`);
  if (!res.ok) throw new Error('Errore nel recupero dello storico prezzi');
  return res.json();
}

export async function trackProduct(payload) {
  const res = await fetch(`${API_BASE}/tracked`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Errore durante l\'aggiunta al monitoraggio');
  }
  return res.json();
}

export async function updateThreshold(id, targetDeltaPercent) {
  const res = await fetch(`${API_BASE}/tracked/${id}/threshold`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ target_delta_percent: targetDeltaPercent }),
  });
  if (!res.ok) throw new Error('Errore nell\'aggiornamento della soglia');
  return res.json();
}

export async function deleteTrackedItem(id) {
  const res = await fetch(`${API_BASE}/tracked/${id}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error('Errore nella rimozione del monitoraggio');
  return true;
}

export async function getNotifications(unreadOnly = false) {
  const res = await fetch(`${API_BASE}/notifications?unread_only=${unreadOnly}`);
  if (!res.ok) throw new Error('Errore nel recupero delle notifiche');
  return res.json();
}

export async function getUnreadNotificationsCount() {
  const res = await fetch(`${API_BASE}/notifications/unread-count`);
  if (!res.ok) return { unread_count: 0 };
  return res.json();
}

export async function markNotificationRead(id) {
  const res = await fetch(`${API_BASE}/notifications/${id}/read`, {
    method: 'PATCH',
  });
  if (!res.ok) throw new Error('Errore');
  return res.json();
}

export async function markAllNotificationsRead() {
  const res = await fetch(`${API_BASE}/notifications/mark-all-read`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Errore');
  return res.json();
}

