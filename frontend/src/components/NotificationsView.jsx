import React, { useState, useEffect } from 'react';
import { Bell, CheckCheck, TrendingDown, ExternalLink, RefreshCw, Check } from 'lucide-react';
import { getNotifications, markNotificationRead, markAllNotificationsRead } from '../api';

export default function NotificationsView({ onNotificationsUpdated }) {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadNotifications = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getNotifications();
      setNotifications(data);
    } catch (err) {
      setError(err.message || 'Errore durante il caricamento delle notifiche.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadNotifications();
  }, []);

  const handleMarkRead = async (id) => {
    try {
      await markNotificationRead(id);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      );
      if (onNotificationsUpdated) onNotificationsUpdated();
    } catch (err) {
      console.error(err);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await markAllNotificationsRead();
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
      if (onNotificationsUpdated) onNotificationsUpdated();
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) {
    return (
      <div className="state-card loading-state">
        <RefreshCw className="spin-icon text-blue" size={32} />
        <p>Caricamento notifiche...</p>
      </div>
    );
  }

  return (
    <div className="notifications-view">
      <div className="notifications-header">
        <div>
          <h3>Centro Notifiche</h3>
          <p className="subtext">
            Avvisi generati quando i prezzi dei tuoi prodotti monitorati scendono oltre la soglia configurata.
          </p>
        </div>

        {notifications.some((n) => !n.is_read) && (
          <button className="btn-secondary" onClick={handleMarkAllRead}>
            <CheckCheck size={16} /> Segna tutte come lette
          </button>
        )}
      </div>

      {error && <div className="alert-box error">{error}</div>}

      {notifications.length === 0 ? (
        <div className="empty-notifications-card">
          <Bell size={44} className="empty-icon text-gray" />
          <h4>Nessuna notifica presente</h4>
          <p>
            Quando Pricey rileverà un calo di prezzo sui tuoi articoli monitorati, riceverai un avviso qui.
          </p>
        </div>
      ) : (
        <div className="notifications-list">
          {notifications.map((n) => (
            <div
              key={n.id}
              className={`notification-card ${n.is_read ? 'read' : 'unread'}`}
            >
              <div className="notification-icon-wrapper">
                <TrendingDown size={22} className="text-green" />
              </div>

              <div className="notification-content">
                <div className="notification-top-row">
                  <span className="notif-badge">
                    -{n.delta_percent.toFixed(1)}% di sconto
                  </span>
                  <span className="notif-time">
                    {new Date(n.created_at).toLocaleString('it-IT')}
                  </span>
                </div>

                <p className="notif-message">{n.message}</p>

                <div className="price-comparison-row">
                  <span className="old-price-strike">{n.old_price.toFixed(2)} €</span>
                  <span className="arrow-sep">→</span>
                  <span className="new-price-bold">{n.new_price.toFixed(2)} €</span>
                </div>
              </div>

              <div className="notification-actions">
                {!n.is_read && (
                  <button
                    className="btn-mark-read"
                    onClick={() => handleMarkRead(n.id)}
                    title="Segna come letto"
                  >
                    <Check size={16} /> Letto
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
