import React, { useState } from 'react';
import { X, Bell, TrendingDown, Check } from 'lucide-react';

export default function TrackModal({ product, onClose, onConfirm }) {
  const [delta, setDelta] = useState(5.0);
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!product) return null;

  const currentPrice = product.price || 0;
  const targetPrice = currentPrice * (1 - delta / 100);
  const potentialSavings = currentPrice - targetPrice;

  const handleConfirm = async () => {
    setIsSubmitting(true);
    try {
      await onConfirm({
        url: product.url,
        title: product.title,
        price: product.price,
        image_url: product.image_url,
        store_name: product.store,
        target_delta_percent: parseFloat(delta),
      });
      onClose();
    } catch (err) {
      alert(err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const presetDeltas = [5, 10, 15, 20];

  return (
    <div className="modal-backdrop">
      <div className="modal-card">
        <div className="modal-header">
          <div className="modal-title-group">
            <Bell className="modal-icon text-blue" size={22} />
            <h3>Monitora Prezzo</h3>
          </div>
          <button className="btn-icon" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div className="modal-body">
          <div className="product-mini-preview">
            {product.image_url && (
              <img src={product.image_url} alt={product.title} className="mini-thumb" />
            )}
            <div>
              <span className="store-pill">{product.store}</span>
              <h4 className="preview-title">{product.title}</h4>
              <p className="preview-price">
                Prezzo attuale: <strong>{currentPrice.toFixed(2)} €</strong>
              </p>
            </div>
          </div>

          <div className="threshold-section">
            <label className="input-label">
              <TrendingDown size={16} />
              Soglia di calo prezzo desiderata (%):
            </label>

            <div className="preset-buttons">
              {presetDeltas.map((d) => (
                <button
                  key={d}
                  type="button"
                  className={`btn-chip ${delta === d ? 'active' : ''}`}
                  onClick={() => setDelta(d)}
                >
                  -{d}%
                </button>
              ))}
            </div>

            <div className="slider-wrapper">
              <input
                type="range"
                min="1"
                max="50"
                step="1"
                value={delta}
                onChange={(e) => setDelta(parseFloat(e.target.value))}
                className="range-slider"
              />
              <span className="slider-value">-{delta}%</span>
            </div>

            <div className="target-summary-box">
              <div className="summary-item">
                <span className="summary-label">Prezzo obiettivo notifica:</span>
                <span className="summary-val text-green">≤ {targetPrice.toFixed(2)} €</span>
              </div>
              <div className="summary-item">
                <span className="summary-label">Risparmio minimo:</span>
                <span className="summary-val text-blue">-{potentialSavings.toFixed(2)} €</span>
              </div>
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn-secondary" onClick={onClose} disabled={isSubmitting}>
            Annulla
          </button>
          <button className="btn-primary" onClick={handleConfirm} disabled={isSubmitting}>
            {isSubmitting ? 'Salvataggio...' : (
              <>
                <Check size={18} /> Avvia Monitoraggio
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

