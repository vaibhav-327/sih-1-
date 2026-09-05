# MPLAD AI SENTINEL
### AI-Powered Detection of Anomalies, Fraud Risks & Inefficiencies in MPLADS Implementation

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React%20%2B%20TypeScript-61DAFB.svg)](https://react.dev/)
[![Scikit-Learn](https://img.shields.io/badge/ML-Isolation%20Forest%20%2B%20NLP-F7931E.svg)](https://scikit-learn.org/)
[![Status](https://img.shields.io/badge/Status-Hackathon--Ready-success.svg)]()

---

## 🏛️ Executive Summary & Product Philosophy

The **Members of Parliament Local Area Development Scheme (MPLADS)** enables Members of Parliament to recommend developmental works in their constituencies, focusing on creating durable community assets (drinking water, primary education, public health, sanitation, roads, and renewable energy).

Implementing thousands of decentralized projects across hundreds of parliamentary constituencies involves multi-tier financial sanctions, executing agencies, contractors, and milestone disbursements. 

**MPLAD AI SENTINEL** is an AI-powered implementation monitoring and decision-support intelligence platform that ingests authorized e-Sakshi data feeds and identifies unusual implementation patterns, cost outliers, geographic clusters, and contractor concentrations.

### 🛡️ Ethical AI & Governance Positioning
> **IMPORTANT**: MPLAD AI SENTINEL does **NOT** make definitive allegations of fraud or misconduct. Instead, it computes explainable **"Potential Risk Indicators"**, **"Implementation Anomalies"**, and **"Efficiency Gaps"** to assist authorities in **PRIORITIZING** where field verification and detailed physical audits are most urgently needed.

### 🧭 Core Operating Philosophy
```
CONNECT ──► ANALYZE ──► DETECT ──► EXPLAIN ──► INVESTIGATE
```
1. **CONNECT**: Securely ingest authorized e-Sakshi data feeds or structured CSV/XLSX exports.
2. **ANALYZE**: Profile project cohorts, contractor portfolios, and constituency baselines.
3. **DETECT**: Unsupervised Machine Learning (Isolation Forest) + NLP duplicate similarity + rule compliance.
4. **EXPLAIN**: Transparent factor contribution answering **WHERE, WHAT, WHY, and WHAT NEXT**.
5. **INVESTIGATE**: Actionable investigation workflow tracking site audits, DPR reviews, and field notes.

---

## 🔍 The Four Key Decision Questions

For every flagged work, Sentinel provides immediate answers to oversight authorities:

| # | Question | Sentinel Output |
|---|---|---|
| **1** | **WHERE is the problem?** | State, District, Parliamentary Constituency, Implementing Agency, and GPS Coordinates. |
| **2** | **WHAT is anomalous?** | Specific deviations (e.g., *+62% Cost Deviation vs Regional Median*, *45% Financial vs Physical Progress Gap*). |
| **3** | **WHY was it flagged?** | Multi-factor explainability score breakdown with component weights (Cost, Delay, Contractor, Duplicate, IF Anomaly). |
| **4** | **WHAT should the authority do next?** | Actionable next steps (e.g., *"Issue field inspection directive for measurement book verification", "Reconcile advance mobilization disbursements"*). |

---

## 🏗️ Architecture & Data Ingestion Pipeline

```
                 E-SAKSHI SYSTEM
                        │
         Official API / Authorized Export (CSV/XLSX/JSON)
                        │
                  DataSource Abstraction
          ┌─────────────┴─────────────┐
    ESakshiAPIDataSource      ESakshiFileDataSource      SyntheticDataSource (5,000 demo)
                        │
                  Validation Engine (Quality Score 0-100)
                        │
                  Feature Engineering (Efficiency Gap, Cost/Beneficiary)
                        │
         ┌──────────────┼──────────────┐
         ▼              ▼              ▼
   Isolation Forest  TF-IDF NLP   Cost & Delay
    Anomaly Engine  Similarity     Rule Engine
         └──────────────┬──────────────┘
                        │
                Unified Risk Engine (0-100 Score)
                        │
             SQLite / PostgreSQL Database
                        │
              FastAPI RESTful Backend
                        │
          React + TypeScript + Tailwind Dashboard
      ┌─────────────────┼─────────────────┐
  Executive Map    Contractor Graph   Investigation Alerts
```

Sentinel provides a modular `DataSource` interface. The dashboard dynamically displays the active data mode:
- `DATA SOURCE: e-SAKSHI` (Live API or verified file export)
- `DATA SOURCE: SYNTHETIC DEMO` (Comprehensive 5,000 record test cohort across 15 Indian States/UTs)

---

## ⚙️ Technology Stack

- **Frontend**:
  - React 18 & TypeScript
  - Tailwind CSS (Premium Dark Intelligence UI)
  - React Router v6
  - Recharts (Interactive visual analytics)
  - Leaflet & React-Leaflet (Geographic mapping of works across India)
  - Lucide React (Executive iconography)
- **Backend**:
  - Python 3.10+
  - FastAPI (High-performance asynchronous REST API)
  - Pydantic v2 (Schema validation & data integrity)
  - SQLAlchemy 2.0 (ORM supporting SQLite for MVP and PostgreSQL in production)
- **Data & Machine Learning**:
  - `scikit-learn`: Isolation Forest for unsupervised anomaly detection
  - `scikit-learn`: TF-IDF Vectorizer + Cosine Similarity for duplicate project identification
  - `pandas` & `numpy`: Feature engineering and cohort-based cost deviation statistics

---

## 🚀 Quick Start & Installation

### Prerequisites
- Python 3.10 or higher
- Node.js 18+ and npm

### 1. Clone & Setup Backend
```bash
# Navigate to workspace
cd SIH

# Install Python dependencies
pip install -r requirements.txt

# Seed the database with 5,000 realistic MPLADS project records
python scripts/seed_database.py

# Start the FastAPI backend server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```
*API documentation will be available at [http://localhost:8000/docs](http://localhost:8000/docs).*

### 2. Setup Frontend
```bash
# In a new terminal, navigate to the frontend directory
cd frontend

# Install dependencies (if not already installed)
npm install

# Start the Vite development server
npm run dev
```
*Frontend dashboard will be accessible at [http://localhost:5173](http://localhost:5173).*

### 3. Run Automated Tests
```bash
# Run unit tests and API integration suite
python run_tests.py

# Or via standard unittest runner
python -m unittest discover -s tests
```

---

## 🎬 3-Minute Live Hackathon Demo Script

Follow this structured workflow for a winning live presentation:

1. **Step 1: Landing Page (`/landing`)**
   - Introduce *MPLAD AI SENTINEL*: *"From public project data to explainable risk intelligence."*
   - Highlight the 5 core pillars: **CONNECT → ANALYZE → DETECT → EXPLAIN → INVESTIGATE**.
   - Note the ethical governance principle: assisting human oversight, not replacing it.

2. **Step 2: Executive Dashboard (`/dashboard`)**
   - Show live calculated KPIs from 5,000 projects: Total Sanctioned vs Utilized Funds, Implementation Status, Risk Donut, and Financial vs Physical Progress alignment scatter chart.
   - Point out that **zero dashboard statistics are hardcoded**—everything is dynamically computed.

3. **Step 3: Data Sources (`/data-sources`)**
   - Show the e-Sakshi connector architecture.
   - Explain how authorized exports (CSV/XLSX/JSON) are schema-mapped and validated with an automated **Data Quality Score (100/100)**.

4. **Step 4: AI Scan Demo (`RUN AI SCAN` Button)**
   - Click **"RUN AI SCAN"** in the top navigation bar.
   - Watch the 8-stage pipeline execute: Ingestion → Validation → Feature Engineering → Isolation Forest → NLP Cosine Similarity → Risk Synthesis → Insights → Alert Generation.
   - Review the summary findings modal.

5. **Step 5: Risk Detection & Drilldown (`/risks` & `/projects`)**
   - Open **Risk Detection** to see the prioritized list of high-risk projects.
   - Click on a project with **Risk Score: 85+ (CRITICAL)** to open the drilldown drawer.
   - Review the **4 Key Decision Questions (WHERE, WHAT, WHY, NEXT ACTION)** and progress gauges.

6. **Step 6: Map Intelligence (`/map`)**
   - Explore the interactive Leaflet map of India.
   - Filter by Risk Level (**CRITICAL / HIGH**) to identify regional implementation clusters.

7. **Step 7: Contractor & Constituency Intelligence (`/contractors` & `/constituencies`)**
   - Demonstrate contractor portfolio analytics (delay rates, project concentrations, high-risk ratios).
   - View the network relationship graph.

8. **Step 8: Alerts & Investigation Workflow (`/alerts`)**
   - Show active alerts. Update an alert status from `NEW` to `FIELD VERIFICATION` with assigned officer and inspection notes.
   - Show that updates persist into SQLite with full audit logging.

9. **Step 9: Conclusion**
   - *"Sentinel empowers district collectors and vigilance officers to target audits where they have the highest public impact."*

---

## 📡 Core API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/dashboard` | `GET` | Executive dashboard KPIs, charts, and risk distributions. |
| `/api/projects` | `GET` | Paginated project list with multi-parameter filtering (State, Risk, Contractor, Type). |
| `/api/projects/{id}` | `GET` | Full project profile and financial records. |
| `/api/projects/{id}/risk` | `GET` | Explainable risk factor breakdown with WHERE, WHAT, WHY, and NEXT ACTION. |
| `/api/contractors` | `GET` | Contractor portfolio metrics, delay rates, and concentration flags. |
| `/api/contractors/network/graph`| `GET` | Entity relationship graph (Contractor → Project → Constituency). |
| `/api/constituencies` | `GET` | Parliamentary constituency utilization and risk rankings. |
| `/api/map/projects` | `GET` | GeoJSON FeatureCollection of projects for Leaflet mapping. |
| `/api/insights` | `GET` | Dynamically synthesized executive insights across 6 operational vectors. |
| `/api/alerts` | `GET` | Prioritized investigation alert queues. |
| `/api/alerts/{id}` | `PUT` | Update investigation status (`UNDER REVIEW`, `FIELD VERIFICATION`, `RESOLVED`, `FALSE POSITIVE`). |
| `/api/model/scan` | `POST` | Execute full multi-stage AI monitoring scan. |
| `/api/model/metrics` | `GET` | ML model architecture, Isolation Forest metrics, and factor weighting. |
| `/api/data/upload` | `POST` | Upload and normalize authorized e-Sakshi CSV/XLSX/JSON exports. |
| `/api/data/validate` | `POST` | Validate dataset against 10 data integrity rules and output Quality Score. |

---

## 🔮 Future Roadmap

- **Satellite & Drone Imagery Verification**: Computer vision comparison of geo-tagged project coordinates over time to verify earthwork and roofing stages.
- **OCR of Invoices & Measurement Books**: Automated extraction of civil work item rates against state Schedule of Rates (SoR).
- **LLM-Powered Vigilance Assistant**: Conversational assistant for investigating officers to query DPR deviations.
- **Mobile Field Inspection App**: Offline-first mobile app for District Quality Monitors to record geotagged site inspection reports.

---

## 📄 License & Attribution
Developed for Smart India Hackathon (SIH) under Government Public Infrastructure Transparency initiatives.
*MPLAD AI SENTINEL — Transforming public project data into explainable risk intelligence.*
