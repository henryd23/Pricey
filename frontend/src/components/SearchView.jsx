import React, { useState } from 'react';
import { Search, Link as LinkIcon, Filter, ExternalLink, PlusCircle, Sparkles } from 'lucide-react';
import { searchProducts, lookupUrl } from '../api';

export default function SearchView({ onTrackClick }) {
  const [activeTab, setActiveTab] = useState('search'); // 'search' or 'url'
  
  // Search tab state
  const [searchQuery, setSearchQuery] = useState('');
  const [maxPrice, setMaxPrice] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [searchError, setSearchError] = useState(null);

  // URL tab state
  const [directUrl, setDirectUrl] = useState('');
  const [urlResult, setUrlResult] = useState(null);
  const [isLookingUp, setIsLookingUp] = useState(false);
  const [urlError, setUrlError] = useState(null);

  const handleSearchSubmit = async (e) => {
    e?.preventDefault();
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    setSearchError(null);
    try {
      const data = await searchProducts(searchQuery, maxPrice);
      setSearchResults(data);
      if (data.length === 0) {
        setSearchError('Nessun prodotto trovato. Prova con termini diversi o aumenta il prezzo massimo.');
      }
    } catch (err) {
      setSearchError(err.message || 'Errore durante la ricerca.');
    } finally {
      setIsSearching(false);
    }
  };

  const handleUrlSubmit = async (e) => {
    e?.preventDefault();
    if (!directUrl.trim()) return;

    setIsLookingUp(true);
    setUrlError(null);
    setUrlResult(null);
    try {
      const data = await lookupUrl(directUrl);
      setUrlResult(data);
    } catch (err) {
      setUrlError(err.message || 'Impossibile estrarre informazioni da questo link.');
    } finally {
      setIsLookingUp(false);
    }
  };

  const quickSearch = (term) => {
    setSearchQuery(term);
    setIsSearching(true);
    setSearchError(null);
    searchProducts(term, maxPrice)
      .then((data) => setSearchResults(data))
      .catch((err) => setSearchError(err.message))
      .finally(() => setIsSearching(false));
  };

  return (
    <div className="search-view">
      {/* Mode Switcher Tabs */}
      <div className="tab-pill-container">
        <button
          className={`tab-pill ${activeTab === 'search' ? 'active' : ''}`}
          onClick={() => setActiveTab('search')}
        >
          <Search size={18} /> Cerca nel Catalogo
        </button>
        <button
          className={`tab-pill ${activeTab === 'url' ? 'active' : ''}`}
          onClick={() => setActiveTab('url')}
        >
          <LinkIcon size={18} /> Inserisci Link Diretto
        </button>
      </div>

      {activeTab === 'search' && (
        <div className="search-box-card">
          <form onSubmit={handleSearchSubmit} className="search-form">
            <div className="input-with-icon query-input">
              <Search className="field-icon" size={20} />
              <input
                type="text"
                placeholder="Cosa stai cercando? (es. Billy, Sedia da gaming, Scrivania...)"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>

            <div className="input-with-icon filter-input">
              <Filter className="field-icon" size={18} />
              <input
                type="number"
                placeholder="Prezzo max (€)"
                value={maxPrice}
                onChange={(e) => setMaxPrice(e.target.value)}
                min="0"
                step="5"
              />
            </div>

            <button type="submit" className="btn-primary" disabled={isSearching || !searchQuery.trim()}>
              {isSearching ? 'Ricerca...' : 'Cerca Offerte'}
            </button>
          </form>

          {/* Quick suggestions */}
          <div className="quick-tags">
            <span className="quick-label">
              <Sparkles size={14} /> Suggerimenti veloci:
            </span>
            {['Billy', 'Kallax', 'Scrivania', 'Lampada', 'Armadio'].map((term) => (
              <button
                key={term}
                type="button"
                className="tag-btn"
                onClick={() => quickSearch(term)}
              >
                {term}
              </button>
            ))}
          </div>

          {searchError && <div className="alert-box error">{searchError}</div>}

          {/* Search Results Grid */}
          {searchResults.length > 0 && (
            <div className="results-container">
              <div className="results-header">
                <h3>Risultati trovati ({searchResults.length})</h3>
              </div>
              <div className="product-grid">
                {searchResults.map((prod, idx) => (
                  <div key={idx} className="product-card">
                    <div className="card-thumb-wrapper">
                      {prod.image_url ? (
                        <img src={prod.image_url} alt={prod.title} className="card-img" />
                      ) : (
                        <div className="no-img-placeholder">Nessuna foto</div>
                      )}
                      <span className="store-badge">{prod.store}</span>
                    </div>

                    <div className="card-content">
                      <h4 className="card-title" title={prod.title}>
                        {prod.title}
                      </h4>
                      <div className="card-price-row">
                        <span className="price-tag">{prod.price.toFixed(2)} €</span>
                        <a
                          href={prod.url}
                          target="_blank"
                          rel="noreferrer"
                          className="store-link-icon"
                          title="Apri link originale"
                        >
                          <ExternalLink size={16} />
                        </a>
                      </div>
                    </div>

                    <div className="card-actions">
                      <button
                        className="btn-track-action"
                        onClick={() => onTrackClick(prod)}
                      >
                        <PlusCircle size={16} /> Monitora Prezzo
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {activeTab === 'url' && (
        <div className="search-box-card">
          <form onSubmit={handleUrlSubmit} className="url-form">
            <div className="input-with-icon url-input-field">
              <LinkIcon className="field-icon" size={20} />
              <input
                type="url"
                placeholder="Incolla l'URL del prodotto (es. da Ikea, Kasanova, Amazon, ecc.)"
                value={directUrl}
                onChange={(e) => setDirectUrl(e.target.value)}
                required
              />
            </div>
            <button type="submit" className="btn-primary" disabled={isLookingUp || !directUrl.trim()}>
              {isLookingUp ? 'Analisi in corso...' : 'Analizza Pagina'}
            </button>
          </form>

          <p className="url-helper-text">
            💡 Supporta link diretti di prodotti da <strong>Ikea</strong> e dalla maggior parte dei negozi online compatibili con i metadati Schema.org / OpenGraph.
          </p>

          {urlError && <div className="alert-box error">{urlError}</div>}

          {urlResult && (
            <div className="single-result-preview">
              <div className="preview-card-inner">
                {urlResult.image_url && (
                  <img src={urlResult.image_url} alt={urlResult.title} className="preview-img" />
                )}
                <div className="preview-details">
                  <span className="store-badge">{urlResult.store}</span>
                  <h3>{urlResult.title}</h3>
                  <div className="preview-price-highlight">
                    {urlResult.price.toFixed(2)} €
                  </div>
                  <div className="preview-action-row">
                    <button
                      className="btn-primary"
                      onClick={() => onTrackClick(urlResult)}
                    >
                      <PlusCircle size={18} /> Monitora questo prodotto
                    </button>
                    <a
                      href={urlResult.url}
                      target="_blank"
                      rel="noreferrer"
                      className="btn-secondary"
                    >
                      <ExternalLink size={16} /> Visita negozio
                    </a>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

