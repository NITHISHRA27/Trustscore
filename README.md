# TRUSTSCORE — Automated Deepfake & Misinformation Trust Score Analyzer

**Team DRACARYS** · Nithish R A · Poornashree S · Annie Mathew · *Media & Information Integrity*

> Verify. Understand. Stay Informed.

TrustScore checks **text, URLs, images, videos and documents** and explains *why* content gets its score. It does not hand out a REAL/FAKE label. Every result shows:

- the **TrustScore** (0–100),
- a separate **evidence confidence** (how much we actually know),
- the **risk indicators** found,
- the supporting and contradicting **sources**,
- the method used and its limitations.

The existing Flet desktop app, FastAPI backend, SQLite database, login, document issuance and SATHYAM document pipeline are all kept and extended.

---

## Quick start (Windows)

```powershell
setup_windows.bat          # creates/uses .venv, installs requirements, copies .env.example -> .env
start_app.bat              # backend + desktop app
```

Or run the two halves separately: `start_backend.bat`, then `start_frontend.bat`.
API docs: <http://127.0.0.1:8000/docs> · Demo login: `demo@http.local` / `demo123`

**Using your existing `.venv`:** run `pip install -r requirements.txt` once. This adds `flet-charts` and `trafilatura`.
**Tesseract OCR** (optional, for scanned documents): install it and add it to PATH. PDF text layers work without it.

---

## What works without any API key

| Module | Offline / free capabilities |
|---|---|
| **Text** | Claim extraction, entities (people, organisations, places, dates, numbers), manipulation-pattern scan (urgency, sensationalism, conspiracy framing, miracle cures, scam lures, forward chains), source-attribution analysis. **GDELT** news and **Wikipedia** lookups work free over the internet. |
| **URL** | SSRF-safe fetching with redirect chain, article/author/date extraction, TLS certificate inspection, domain age (RDAP, free), publisher-type reference lists (official, fact-checker, newsroom, satire, user-generated), corroboration search |
| **Image** | EXIF, XMP and PNG metadata; AI-generator signatures (Stable Diffusion parameters, ComfyUI, DALL·E, Firefly, Midjourney, IPTC `trainedAlgorithmicMedia`); C2PA detection; Error Level Analysis heatmap; perceptual-hash near-duplicate check |
| **Video** | Decoding integrity, stream properties, keyframes, frame-continuity analysis |
| **Document** | PDF text layer and Tesseract OCR; field validation including the **Aadhaar Verhoeff checksum**; QR and barcode decoding cross-checked against the issuance registry; SHA-256 registry match; PDF forensics (producer, modified-after-creation, incremental updates, embedded JavaScript) |
| **Ignis 🐉** | Dragon assistant: tells you which check fits your content, explains scores, terms and limitations, and can start an analysis straight from the chat |

### Optional integrations (`.env`)

| Key | Adds |
|---|---|
| `GOOGLE_FACTCHECK_API_KEY` (free) | Professional fact-check ratings. A "False" rating becomes decisive contradicting evidence. |
| `TAVILY_API_KEY` (free tier) | Web search for supporting and contradicting coverage |
| `GOOGLE_SAFE_BROWSING_API_KEY` (free) | Malware and phishing URL check |
| `ENABLE_HF_MODELS=true` + `pip install -r requirements-ml.txt` | Transformer NER, NLI stance detection (supports/contradicts), sentence embeddings, AI-image detector model |
| `ANTHROPIC_API_KEY` | Smarter answers from Ignis on open questions, plus LLM stance judgement of retrieved snippets |

Keys are read only by the backend and never sent to the desktop app. **Settings → Integrations** shows what is configured and whether each provider was reachable on its last run.

---

## Scoring methodology (`app/config/scoring.json`)

1. Each module emits **signals** (0–100, with a reliability/confidence value) that belong to five groups: source credibility, evidence quality, content consistency, manipulation indicators, and metadata & provenance.
2. **TrustScore** = confidence-weighted average of the **completed** signals only. Checks that couldn't run are excluded and never counted as negative.
3. **Evidence confidence** = 45% check coverage + 40% independent evidence strength + 15% mean signal reliability.
4. **Category rules:**
   - **High Risk**: a decisive red flag (fact-check rated false, Safe Browsing listing, AI-generator metadata, invalid C2PA, unknown registry ID in a QR code), or a score below 45 together with multiple independent high-severity indicators.
   - **Insufficient Evidence**: confidence below 35%.
   - **High Trust**: score ≥ 75 and confidence ≥ 50%.
   - **Needs Review**: anything else.
5. Safeguards: an **AI detector on its own can never produce High Risk**. **No search results means "unverified", never "false".** HTTPS is reported as transport security, not credibility.

The weights are transparent design choices for this prototype. They are **not** validated or calibrated probabilities.

---

## API overview

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/analyze/text` | `{"text": "...", "mode": "sync"\|"async"}` |
| POST | `/api/analyze/url` | `{"url": "...", "mode": ...}` |
| POST | `/api/analyze/media?mode=async` | multipart `file`: image or video |
| POST | `/api/analyze/document/upload?mode=async` | multipart `file` + `document_type` |
| POST | `/api/analyze/document` | re-analyse an uploaded document by ID |
| GET | `/api/analyses/{id}/status` | live progress stages + result |
| GET | `/api/history` | filters: `input_type`, `category`, `date_from`, `date_to`, `q` |
| GET / PATCH / DELETE | `/api/history/{id}` · `/review` | full report · mark reviewed · delete |
| GET | `/api/dashboard` | category counts, recent activity, insights, module status |
| GET | `/api/reports` | aggregates, trend, stance totals, signal-group averages (same filters) |
| GET | `/api/reports/{id}/pdf` | PDF export (ReportLab, with charts) |
| GET | `/api/modules/status` | module availability and integrations |
| POST | `/api/assistant/chat` | Ignis assistant |
| GET | `/verify/{registry_id}` | public issuance-registry lookup (target of issued QR codes) |

The legacy `/api/documents`, `/api/verification`, `/api/issuance`, `/api/auth` and `/mock/*` routes still work.

## Database

The SQLite database is upgraded in place on startup. New columns are added to `trust_analyses`, two tables are created (`evidence_records`, `report_exports`), and old classifications are mapped to the new categories. Existing data is preserved.

## Security

- SSRF protection: public IPs only, re-validated on every redirect, at most 5 redirects, 2 MB cap.
- Upload type and size limits, with images re-decoded before analysis.
- Per-user rate limiting.
- CORS restricted to localhost.
- Rotating log file in `logs/`.
- Uploads are **no longer** auto-registered as "trusted" hashes. Before, every upload matched its own hash.
- The authority check **no longer** substitutes a placeholder name ("DEMO CITIZEN") when OCR finds none.

## Known limitations (honest list)

- Government connectors (UIDAI/ECI/PAN/department) are **simulated** and excluded from the score.
- AI-image detection needs the optional model, and even then it is only an indicator. There is no dedicated deepfake or audio model.
- Without a stance method (fact-check rating, NLI model or LLM), retrieved news is shown as *related coverage*, not as support.
- Reverse-image search is not integrated. Near-duplicates are matched only against your own TrustScore history.

## Tests

```powershell
pip install -r requirements-dev.txt
python -m pytest -q
```

The tests cover the engine rules, SSRF protection, the Verhoeff checksum, and the full text and URL pipelines against recorded-style responses from Google Fact Check, Tavily, GDELT, Wikipedia and RDAP.
