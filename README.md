# 🏷️ Pricey — Smart E-commerce Price Tracker & Alerts

Pricey è una piattaforma moderna e modulare per il monitoraggio intelligente dei prezzi su e-commerce (Ikea, Amazon, Apple, Kasanova e store terzi compatibili con Schema.org / OpenGraph).

L'applicazione rileva i prezzi di prodotti, mantiene monitorati i link tramite controlli periodici in background e notifica automaticamente l'utente via **in-app** ed **email** quando il prezzo diminuisce della percentuale desiderata (soglia predefinita: **-5%**, configurabile per ciascun articolo).

---

## ✨ Funzionalità Principali

- 🔍 **Ricerca Prodotti & Catalogo**: ricerca live per nome/modello nei negozi supportati con filtri opzionali per prezzo massimo (`max_price`).
- 🔗 **Analisi URL Diretto**: basta incollare il link di un prodotto per estrarne istantaneamente titolo, prezzo attuale, immagine e disponibilità.
- 📉 **Configurazione Alert Personalizzata**: imposta la soglia di sconto desiderata (-5%, -10%, -15%, -20% o personalizzata) con calcolo in tempo reale del prezzo obiettivo e del risparmio minimo.
- 📊 **Grafico Storico Prezzi**: visualizzatore interattivo dell'andamento dei prezzi nel tempo per ciascun articolo monitorato.
- ⏰ **Scheduler Periodico in Background**: motore basato su `APScheduler` che verifica periodicamente i link attivi e traccia i cambiamenti in database.
- 🔔 **Notifiche In-App & Email**: centro notifiche con badge non lette in tempo reale ed email di avviso con template HTML.
- 👤 **Gestione Utenti Multi-Account**: registrazione e login con password hashing `bcrypt`, token `JWT` e isolamento completo dei dati per utente.
- 🐳 **Pronto per Docker**: configurazione multi-container con `docker-compose.yml`.

---

## 🛠️ Stack Tecnologico

- **Backend**: Python 3.12, FastAPI, SQLModel (SQLAlchemy), Pydantic, APScheduler, PyJWT, bcrypt, HTTPX, BeautifulSoup4.
- **Frontend**: React 19, Vite, Lucide React, CSS3 responsive.
- **Database**: SQLite (default zero-config per sviluppo locale) / PostgreSQL ready.
- **Container**: Docker, Docker Compose, Nginx (reverse proxy per frontend).

---

## 🚀 Avvio Rapido in Locale

### 1. Prerequisiti
- Python 3.10+
- Node.js 18+ e npm

### 2. Avvio Backend
Dalla cartella principale del progetto:

```powershell
# Installa le dipendenze
pip install -r backend/requirements.txt

# Avvia il server FastAPI (con auto-reload)
python run_backend.py
```
*Il backend sarà attivo su `http://127.0.0.1:8000` (documentazione Swagger interattiva su `http://127.0.0.1:8000/docs`).*

### 3. Avvio Frontend
In un altro terminale:

```powershell
cd frontend
npm install
npm run dev
```
*Apri `http://localhost:5173` nel browser.*

---

## 🐳 Avvio con Docker Compose

Puoi avviare l'intera applicazione (Backend + Frontend Nginx) con un singolo comando:

```bash
docker compose up --build
```

- **Frontend Web UI**: `http://localhost:3000`
- **Backend API & Swagger Docs**: `http://localhost:8000/docs`

---

## 🧪 Esecuzione dei Test Automatizzati

Il progetto include test unitari e di integrazione completi (`pytest`):

```powershell
python -m pytest tests -v
```

---

## 🗺️ Roadmap & Backlog

Per visualizzare i dettagli dei requisiti, delle user story e delle milestone implementate, consulta:
- [doc/Roadmap.md](doc/Roadmap.md) — Dettaglio di tutte le fasi da 0 a 6.
- [doc/ProductBacklog.md](doc/ProductBacklog.md) — Epiche e User Stories (US-01 a US-13).
- [doc/Diagrams.md](doc/Diagrams.md) — Diagrammi di flusso e casi d'uso.
