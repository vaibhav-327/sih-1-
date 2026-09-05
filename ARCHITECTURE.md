# MPLAD AI SENTINEL — SYSTEM ARCHITECTURE SPECIFICATION

```
================================================================================
                               E-SAKSHI PORTAL
                    (Official API / Authorized File Export)
================================================================================
                                       │
                                       ▼
                       ┌──────────────────────────────┐
                       │    Data Ingestion Layer      │
                       │   - ESakshiAPIDataSource     │
                       │   - ESakshiFileDataSource    │
                       │   - SyntheticDataSource      │
                       └──────────────┬───────────────┘
                                       │
                                       ▼
                       ┌──────────────────────────────┐
                       │    Data Validation Service   │
                       │   - 10 Integrity Rule Checks │
                       │   - Data Quality Score (0-100│
                       │   - Provenance Tracking      │
                       └──────────────┬───────────────┘
                                       │
                                       ▼
                       ┌──────────────────────────────┐
                       │  Feature Engineering Service │
                       │   - Cost per Beneficiary     │
                       │   - Progress Efficiency Gap  │
                       │   - Schedule Overrun Days    │
                       │   - Contractor Concentration │
                       └──────────────┬───────────────┘
                                       │
            ┌──────────────────────────┼──────────────────────────┐
            ▼                          ▼                          ▼
 ┌──────────────────────┐   ┌──────────────────────┐   ┌──────────────────────┐
 │  Anomaly ML Engine   │   │     NLP Engine       │   │    Compliance & Rule │
 │   Isolation Forest   │   │  TF-IDF Vectorizer   │   │      Cost Deviation  │
 │ Unsupervised Outlier │   │  Cosine Similarity   │   │    Timeline Delays   │
 │   Detection (0-100)  │   │  Geospatial Radius   │   │  Progress Alignment  │
 └──────────┬───────────┘   └──────────┬───────────┘   └──────────┬───────────┘
            │                          │                          │
            └──────────────────────────┼──────────────────────────┘
                                       │
                                       ▼
                       ┌──────────────────────────────┐
                       │     Unified Risk Engine      │
                       │   - Composite Risk Score     │
                       │   - 4-Question Explainability│
                       │   - Risk Levels: LOW/MED/HIGH│
                       │   - Recommended Actions      │
                       └──────────────┬───────────────┘
                                       │
                                       ▼
                       ┌──────────────────────────────┐
                       │   Persistence & Cache Layer  │
                       │   - SQLite (MVP / Local)     │
                       │   - PostgreSQL Compatible    │
                       │   - Audit Trail & Logs       │
                       └──────────────┬───────────────┘
                                       │
                                       ▼
                       ┌──────────────────────────────┐
                       │     FastAPI REST Services    │
                       │   - Dashboard Analytics      │
                       │   - Project & Risk APIs      │
                       │   - Contractor Graph API     │
                       │   - Alerts & Workflow CRUD   │
                       └──────────────┬───────────────┘
                                       │
                                       ▼
                       ┌──────────────────────────────┐
                       │   React + TypeScript UI      │
                       │   - Executive Dashboard      │
                       │   - Interactive Leaflet Map  │
                       │   - Risk Drilldown Drawer    │
                       │   - Investigation Workflow   │
                       └──────────────────────────────┘
```

---

## 1. Component Descriptions

### 1.1 Data Ingestion & Abstraction (`backend/data_sources/`)
- **`DataSource` Base Class**: Abstract interface with `fetch_data()` contract producing a normalized schema.
- **`ESakshiAPIDataSource`**: Configurable REST connector supporting environment variables (`ESAKSHI_BASE_URL`, `ESAKSHI_API_KEY`, `ESAKSHI_USERNAME`, `ESAKSHI_PASSWORD`). Operates safely without hardcoding or exposing credentials.
- **`ESakshiFileDataSource`**: Ingestion adapter for CSV, XLSX, and JSON authorized exports using column mappings defined in `config/esakshi_mapping.json`.
- **`SyntheticDataSource`**: Generates 5,000+ realistic MPLADS projects across Indian States/UTs with realistic cost vs duration distributions, regional clustering, and injected risk patterns for live hackathon demonstration.

### 1.2 Data Validation & Provenance (`backend/services/validation_service.py`)
- **10 Core Validation Rules**:
  1. Negative Sanctioned / Released / Utilized amounts.
  2. Released Amount > Sanctioned Amount.
  3. Utilized Amount > Released Amount.
  4. Physical Progress > 100% or < 0%.
  5. Financial Progress > 100% or < 0%.
  6. Expected Completion Date earlier than Start Date.
  7. Missing or duplicate Project IDs.
  8. Missing Contractor or Implementing Agency.
  9. Invalid GPS Coordinates (outside India boundaries).
  10. Extreme timeline duration inconsistencies.
- **Data Quality Score**: Computed as `100 - penalties` (with 100 representing full schema compliance).
- **Data Provenance**: Every record preserves `source`, `source_file`, `source_record_id`, `import_timestamp`, and `data_version`.

### 1.3 Machine Learning & Risk Pipeline (`backend/ml/`)
- **Unsupervised Isolation Forest (`anomaly_detector.py`)**: Identifies multi-dimensional outliers across normalized feature vectors (cost per beneficiary, duration, progress variance, contractor volume) using reproducible `random_state=42`.
- **Cohort Cost Anomaly Analyzer (`cost_analyzer.py`)**: Calculates percentiles and median baselines grouped by `(project_type, state)` cohorts to detect statistically significant cost inflation.
- **NLP Duplicate Detection (`nlp_similarity.py`)**: Tokenizes and vectorizes project descriptions with TF-IDF, applying Cosine Similarity combined with Haversine geospatial proximity (< 5 km) to detect potential duplicate works.
- **Unified Risk Engine (`risk_engine.py`)**: Aggregates multi-vector risk indicators into a calibrated 0–100 risk score and generates structured explainability objects answering:
  - **WHERE** is the project?
  - **WHAT** is anomalous?
  - **WHY** was it flagged?
  - **WHAT NEXT** should authorities do?

### 1.4 API Services Layer (`backend/routes/`)
- Asynchronous FastAPI endpoints for dashboard KPIs, paginated projects with full-text search and faceted filtering, contractor network graphs, GeoJSON spatial queries, and investigation alerts management.

### 1.5 Frontend Client Architecture (`frontend/src/`)
- Single-page application built with React 18, TypeScript, Tailwind CSS, Recharts for dynamic charts, and Leaflet for geospatial intelligence. Zero static hardcoded metrics—all UI elements hydrate from the backend API.

---

## 2. Risk Classification Standards

| Risk Level | Composite Score Range | Action Directive | Color Code |
|---|---|---|---|
| **LOW** | 0 – 30 | Routine monitoring | Emerald (`#10b981`) |
| **MEDIUM** | 31 – 60 | Schedule desk review | Amber (`#f59e0b`) |
| **HIGH** | 61 – 80 | Priority physical field inspection | Orange (`#f97316`) |
| **CRITICAL** | 81 – 100 | Urgent audit & measurement book reconciliation | Rose (`#f43f5e`) |

---

## 3. Database Schema

- `projects`: Primary project master, financial ledger, progress metrics, and risk factors.
- `contractors`: Aggregated contractor performance, concentration ratios, and delay indices.
- `constituencies`: Lok Sabha / Rajya Sabha constituency utilization and progress rates.
- `transactions`: Milestone payments, fund releases, and voucher disbursements.
- `milestones`: Physical construction milestones and inspection verifications.
- `alerts`: Active investigation items with officer assignments and notes.
- `audit_logs`: Immutable tracking of system actions, model runs, and status updates.
- `model_runs`: Training runs, parameters, metrics, and anomaly counts.

---

## 4. Production Transition: SQLite to PostgreSQL

To deploy in production:
1. Set environment variable: `DATABASE_URL=postgresql://user:pass@dbhost:5432/mplad_sentinel`
2. SQLAlchemy models in `backend/models/` will connect directly without code alterations.
3. Replace SQLite JSON storage with native PostgreSQL `JSONB` for accelerated indexing.
