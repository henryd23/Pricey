import React, { useState, useEffect } from 'react';
import {
  TrendingDown,
  Trash2,
  ExternalLink,
  Sliders,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  ShoppingBag,
  Clock,
} from 'lucide-react';
import PriceChart from './PriceChart';
import {
  getTrackedItems,
  getTrackedItemDetail,
  deleteTrackedItem,
  updateThreshold,
  triggerPriceCheckNow,
} from '../api';

export default function DashboardView({ onNavigateToSearch, onShowToast }) {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isCheckingNow, setIsCheckingNow] = useState(false);
  const [error, setError] = useState(null);
  const [expandedId, setExpandedId] = useState(null);
  const [expandedDetails, setExpandedDetails] = useState({});

  const loadItems = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getTrackedItems();
      setItems(data);
    } catch (err) {
      setError(err.message || 'Errore durante il caricamento dei prodotti.');
    } finally {
      setLoading(false);
    }
  };

  const handleCheckNow = async () => {
    setIsCheckingNow(true);
    try {
      const res = await triggerPriceCheckNow();
      onShowToast(res.message);
      await loadItems();
    } catch (err) {
      alert(err.message);
    } finally {
      setIsCheckingNow(false);
    }
  };

  useEffect(() => {
    loadItems();
  }, []);

  const toggleExpand = async (id) => {
    if (expandedId === id) {
      setExpandedId(null);
      return;
    }
    setExpandedId(id);
    if (!expandedDetails[id]) {
      try {
        const detail = await getTrackedItemDetail(id);
        setExpandedDetails((prev) => ({ ...prev, [id]: detail }));
      } catch (err) {
        console.error('Failed to load item detail', err);
      }
    }
  };

  const handleDelete = async (id, title) => {
    if (!window.confirm(`Sei sicuro di voler interrompere il monitoraggio per "${title}"?`)) {
      return;
    }
    try {
      await deleteTrackedItem(id);
      setItems((prev) => prev.filter((item) => item.id !== id));
      onShowToast(`Monitoraggio rimosso per "${title}"`);
    } catch (err) {
      alert(err.message);
    }
  };

  const handleThresholdChange = async (id, currentVal) => {
    const input = window.prompt(
      'Inserisci la nuova percentuale di sconto minima desiderata per la notifica (%):',
      currentVal
    );
    if (!input) return;
    const val = parseFloat(input);
    if (isNaN(val) || val <= 0) {
      alert('Inserisci un valore percentuale valido (es. 5, 10)');
      return;
    }

    try {
      const updated = await updateThreshold(id, val);
      setItems((prev) =>
        prev.map((item) => (item.id === id ? { ...item, target_delta_percent: updated.target_delta_percent } : item))
      );
      onShowToast(`Soglia aggiornata a -${val}%`);
    } catch (err) {
      alert(err.message);
    }
  };

  if (loading) {
    return (
      <div className="state-card loading-state">
        <RefreshCw className="spin-icon text-blue" size={32} />
        <p>Caricamento prodotti monitorati...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="state-card error-state">
        <p>{error}</p>
        <button className="btn-secondary" onClick={loadItems}>
          Riprova
        </button>
      </div>
    );
  }

  return (
    <div className="dashboard-view">
      {/* Metrics Banner */}
      <div className="metrics-bar">
        <div className="metric-box">
          <span className="metric-label">Prodotti Monitorati</span>
          <span className="metric-value">{items.length}</span>
        </div>
        <div className="metric-box">
          <span className="metric-label">Soglia Predefinita</span>
          <span className="metric-value text-blue">-5%</span>
        </div>
        <div className="metric-box">
          <span className="metric-label">Frequenza Controlli</span>
          <span className="metric-value text-green">Ogni 60m</span>
        </div>
        <button
          className="btn-primary btn-check-now"
          onClick={handleCheckNow}
          disabled={isCheckingNow}
          title="Verifica immediatamente i prezzi di tutti i prodotti"
        >
          <RefreshCw className={isCheckingNow ? 'spin-icon' : ''} size={16} />
          {isCheckingNow ? 'Verifica in corso...' : 'Verifica Prezzi Ora'}
        </button>
      </div>

      {items.length === 0 ? (
        <div className="empty-dashboard-card">
          <ShoppingBag size={48} className="empty-icon text-blue" />
          <h3>Nessun prodotto monitorato al momento</h3>
          <p>
            Cerca i tuoi prodotti preferiti o incolla un link per iniziare a tracciare i prezzi e ricevere notifiche appena scendono!
          </p>
          <button className="btn-primary" onClick={onNavigateToSearch}>
            Inizia a Monitorare
          </button>
        </div>
      ) : (
        <div className="tracked-items-list">
          {items.map((item) => {
            const isDiscounted = item.current_price < item.initial_price;
            const dropPercent = isDiscounted
              ? (((item.initial_price - item.current_price) / item.initial_price) * 100).toFixed(1)
              : null;
            const isExpanded = expandedId === item.id;
            const history = expandedDetails[item.id]?.price_history || [];

            return (
              <div key={item.id} className="tracked-item-card">
                <div className="tracked-item-main">
                  {item.image_url ? (
                    <img src={item.image_url} alt={item.title} className="item-thumb" />
                  ) : (
                    <div className="no-img-placeholder mini">Nessuna foto</div>
                  )}

                  <div className="item-info-col">
                    <div className="item-tag-row">
                      <span className="store-badge">{item.store_name}</span>
                      <span className="threshold-badge">
                        <Sliders size={12} /> Alert: -{item.target_delta_percent}%
                      </span>
                    </div>

                    <h4 className="item-title">{item.title}</h4>

                    <div className="item-meta-row">
                      <span className="meta-time">
                        <Clock size={13} /> Ultimo controllo: {new Date(item.last_checked_at).toLocaleTimeString('it-IT', { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                  </div>

                  <div className="item-price-col">
                    <div className="price-stack">
                      <span className="current-price-display">
                        {item.current_price.toFixed(2)} €
                      </span>
                      {isDiscounted ? (
                        <div className="discount-pill">
                          <TrendingDown size={14} /> -{dropPercent}% (Iniziale: {item.initial_price.toFixed(2)}€)
                        </div>
                      ) : (
                        <span className="initial-price-sub">
                          Iniziale: {item.initial_price.toFixed(2)} €
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="item-actions-col">
                    <button
                      className="btn-icon-subtle"
                      onClick={() => handleThresholdChange(item.id, item.target_delta_percent)}
                      title="Modifica soglia di calo prezzo"
                    >
                      <Sliders size={18} />
                    </button>
                    <a
                      href={item.url}
                      target="_blank"
                      rel="noreferrer"
                      className="btn-icon-subtle"
                      title="Vai allo store"
                    >
                      <ExternalLink size={18} />
                    </a>
                    <button
                      className="btn-icon-subtle danger"
                      onClick={() => handleDelete(item.id, item.title)}
                      title="Interrompi monitoraggio"
                    >
                      <Trash2 size={18} />
                    </button>
                  </div>
                </div>

                {/* Expand / Collapse Price History Toggle */}
                <div className="expand-row">
                  <button
                    className="btn-expand-history"
                    onClick={() => toggleExpand(item.id)}
                  >
                    {isExpanded ? (
                      <>
                        <ChevronUp size={16} /> Nascondi Storico Prezzi
                      </>
                    ) : (
                      <>
                        <ChevronDown size={16} /> Mostra Storico Prezzi
                      </>
                    )}
                  </button>
                </div>

                {/* Expanded Details Drawer */}
                {isExpanded && (
                  <div className="history-drawer">
                    <h5>Andamento Storico Prezzo</h5>
                    <PriceChart history={history} currency={item.currency} />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

