# 🗺️ Pricey — Roadmap di Sviluppo (Vibecoding)

Questo documento definisce la roadmap incrementale e iterativa per lo sviluppo di **Pricey**, basata su "vertical slices" (fette verticali end-to-end) per consentire uno sviluppo fluido, testabile e rifinibile a ogni passaggio (*vibecoding*).

---

## 🎯 Obiettivi e Decisioni di Progetto

- **Input Prodotti**: Ricerca per nome/modello del prodotto + inserimento diretto tramite **URL specifico**.
- **Canale Notifiche**: Notifiche **in-app** (dashboard/alert/toast) ed **Email** (SMTP / provider transazionale).
- **Architettura Backend**: FastAPI + SQLAlchemy / SQLModel + Pydantic + APScheduler.
- **Database**: SQLite per sviluppo locale immediato a zero-config, facilmente migrabile a PostgreSQL (tramite `docker-compose.yml`).
- **Architettura Scraper**: Modulare a plugin (`BaseScraper`) con supporto a siti multipli (Amazon, MediaWorld, Unieuro, Decathlon, Ikea, ecc.).
- **Frontend**: React + Vite, focalizzato su dashboard chiara per ricerca, tracking e storico prezzi.

---

## 📅 Fasi di Implementazione

### Fase 0 — Setup, Pulizia e Allineamento Architetturale
- [x] Sistemazione della cartella frontend (spostamento da `frontend/frontend` a `frontend/`).
- [x] Configurazione del file `.gitignore` globale (Python, Node, DB, file temporanei).
- [x] Configurazione ambiente backend (`requirements.txt` con dipendenze base: `fastapi`, `uvicorn`, `sqlmodel`/`sqlalchemy`, `pydantic`, `httpx`, `beautifulsoup4`).
- [x] Configurazione file `.env.example` per parametri di configurazione (DB URL, email settings, intervallo check).

### Fase 1 — Core Scraper Engine & Extraction Spike
- [x] Definizione dell'interfaccia astratta `BaseScraper`:
  - `search(query: str) -> list[ScrapedProduct]`
  - `get_product_details(url: str) -> ScrapedProduct`
- [x] Implementazione scraper IKEA (ricerca live via catalogo e scraping diretto URL) + parser universale `GenericScraper` (Schema.org / OpenGraph per store terzi).
- [x] Modulo Amazon preparato (con gestione e rilevazione sfide anti-bot).
- [x] Test automatizzati (`pytest`) per parser prezzi, dispatching e fallback.

### Fase 2 — Backend Core & Modelli Database
- [ ] Definizione modelli database:
  - `Product`: titolo, brand, categoria, immagine.
  - `MonitoredItem`: url, store_name, current_price, target_delta_percent, is_active.
  - `PriceHistory`: item_id, price, timestamp.
  - `Notification`: message, old_price, new_price, delta_percent, read_status, sent_at.
- [ ] Endpoint REST:
  - `POST /api/search`: ricerca prodotti sui siti supportati.
  - `POST /api/lookup-url`: recupera i dettagli di un prodotto da un URL incollato.
  - `POST /api/tracked`: aggiunge un prodotto/URL al monitoraggio con soglia personalizzata.
  - `GET /api/tracked`: elenca i prodotti monitorati e l'ultimo prezzo.
  - `GET /api/tracked/{id}/history`: restituisce lo storico prezzi per il grafico.

### Fase 3 — Frontend V1 (UI Interattiva & Dashboard)
- [ ] Pagina di Ricerca / Inserimento URL:
  - Barra per ricerca libera o inserimento link diretto.
  - Card di risultato con confronto store e prezzi rilevati.
  - Modale o tasto *"Aggiungi al monitoraggio"* con impostazione soglia delta (default 5%).
- [ ] Dashboard Prodotti Monitorati:
  - Card o tabella dei prodotti attivi con indicatore di calo/aumento di prezzo.
  - Dettaglio prodotto con grafico storico prezzi.
  - Centro notifiche in-app.

### Fase 4 — Background Scheduler & Notifiche
- [ ] Integrazione di `APScheduler` nel ciclo di vita di FastAPI.
- [ ] Task periodico di controllo prezzi:
  - Esegue lo scrape dei prodotti attivi.
  - Registra il nuovo prezzo in `PriceHistory`.
  - Calcola la variazione percentuale: $\text{delta} = \frac{P_{prev} - P_{new}}{P_{prev}} \times 100$.
- [ ] Se $\text{delta} \ge \text{target\_delta}$:
  - Genera notifica in-app nel DB.
  - Invia notifica email (servizio SMTP configurabile).

### Fase 5 — Gestione Utenti & Multi-account (Epic 05)
- [ ] Modello `User` con password hashing (`bcrypt`/`argon2`).
- [ ] Autenticazione JWT (`/api/auth/register`, `/api/auth/login`, `/api/auth/me`).
- [ ] Associazione di ogni `MonitoredItem` all'utente autenticato.
- [ ] Aggiornamento UI Frontend con form di Login/Registrazione e protezione route.

### Fase 6 — Espansione Store, Filtri Avanzati & Rifiniture
- [ ] Scraper aggiuntivi (Amazon, MediaWorld, Unieuro, con gestione bot/header o fallback).
- [ ] Filtri avanzati: prezzo massimo, filtro store, categorie.
- [ ] Configurazione Docker Compose completa (Backend + Frontend + PostgreSQL) pronta al deploy.

