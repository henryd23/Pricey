import React, { useState, useEffect } from 'react';
import { Search, Eye, Bell, Tag, Sparkles, Check } from 'lucide-react';
import SearchView from './components/SearchView';
import DashboardView from './components/DashboardView';
import NotificationsView from './components/NotificationsView';
import TrackModal from './components/TrackModal';
import { getUnreadNotificationsCount, trackProduct } from './api';
import './App.css';

export default function App() {
  const [activeTab, setActiveTab] = useState('search'); // 'search' | 'dashboard' | 'notifications'
  const [unreadCount, setUnreadCount] = useState(0);
  const [modalProduct, setModalProduct] = useState(null);
  const [toastMessage, setToastMessage] = useState(null);

  const fetchUnread = async () => {
    try {
      const data = await getUnreadNotificationsCount();
      setUnreadCount(data.unread_count || 0);
    } catch (e) {
      // ignore
    }
  };

  useEffect(() => {
    fetchUnread();
    const interval = setInterval(fetchUnread, 30000); // Poll unread count every 30s
    return () => clearInterval(interval);
  }, []);

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  const handleTrackConfirm = async (payload) => {
    await trackProduct(payload);
    showToast(`"${payload.title.slice(0, 30)}..." aggiunto al monitoraggio!`);
    fetchUnread();
    setActiveTab('dashboard'); // Switch to dashboard to see tracked product
  };

  return (
    <div className="app-shell">
      {/* Navigation Header */}
      <header className="navbar">
        <div className="navbar-container">
          <div className="brand" onClick={() => setActiveTab('search')}>
            <div className="brand-logo-icon">
              <Tag size={22} className="text-white" />
            </div>
            <div>
              <h1 className="brand-title">Pricey</h1>
              <span className="brand-tagline">Price Tracker & Smart Alerts</span>
            </div>
          </div>

          <nav className="nav-links">
            <button
              className={`nav-btn ${activeTab === 'search' ? 'active' : ''}`}
              onClick={() => setActiveTab('search')}
            >
              <Search size={18} />
              <span>Cerca & Traccia</span>
            </button>

            <button
              className={`nav-btn ${activeTab === 'dashboard' ? 'active' : ''}`}
              onClick={() => setActiveTab('dashboard')}
            >
              <Eye size={18} />
              <span>Monitorati</span>
            </button>

            <button
              className={`nav-btn ${activeTab === 'notifications' ? 'active' : ''}`}
              onClick={() => setActiveTab('notifications')}
            >
              <div className="icon-with-badge">
                <Bell size={18} />
                {unreadCount > 0 && <span className="badge-pill">{unreadCount}</span>}
              </div>
              <span>Notifiche</span>
            </button>
          </nav>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="main-content">
        <div className="content-container">
          {activeTab === 'search' && (
            <SearchView onTrackClick={(product) => setModalProduct(product)} />
          )}

          {activeTab === 'dashboard' && (
            <DashboardView
              onNavigateToSearch={() => setActiveTab('search')}
              onShowToast={showToast}
            />
          )}

          {activeTab === 'notifications' && (
            <NotificationsView onNotificationsUpdated={fetchUnread} />
          )}
        </div>
      </main>

      {/* Track Product Modal */}
      {modalProduct && (
        <TrackModal
          product={modalProduct}
          onClose={() => setModalProduct(null)}
          onConfirm={handleTrackConfirm}
        />
      )}

      {/* Toast Alert */}
      {toastMessage && (
        <div className="toast-notification">
          <Check size={18} className="text-green" />
          <span>{toastMessage}</span>
        </div>
      )}
    </div>
  );
}
