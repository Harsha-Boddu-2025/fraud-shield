# 🛡️ Fraud Shield — AI for Digital Public Safety

**Economic Times AI Challenge** · Theme: Smart Cities / Public Safety / Digital Trust

An AI-powered Digital Public Safety Intelligence platform that shifts fraud response from **reactive case investigation to predictive threat neutralisation** — detecting digital-arrest scams, counterfeit currency and organised fraud networks **before mass victimisation occurs**.

> India registered **1.14M cybercrime complaints in 2023 (+60% YoY)**. Digital-arrest scams alone defrauded citizens of **₹1,776 crore** in Jan–Sep 2024 (MHA). Fraud Shield detects threats at the **point of contact**, not the point of complaint.

**Live demo:** https://fraud-shield-et.streamlit.app/

## Six modules
| Module | Problem-statement area |
|---|---|
| 🛡️ Citizen Fraud Shield | Digital Arrest Scam Detection & Alerting — hybrid rule-engine + **NVIDIA NIM LLM** verdict on any message/transcript, evidence highlighting, advisories in English/हिंदी/తెలుగు, 1930 helpline routing |
| 💵 Counterfeit Check | Counterfeit Currency Identification — CV feature screening (geometry, security thread, microprint density, serial panel) with escalation policy |
| 🕸️ Network Intelligence | Fraud Network Graph Intelligence — victims, scammer numbers, mules & devices clustered into rings with priority takedown targets |
| 🗺️ Geo Intelligence | Geospatial Crime Pattern Intelligence — India hotspot map of complaints + FICN seizures, ranked patrol prioritisation |
| 🎛️ Command Center | Real-time public safety coordination — live NCRP-style feed, ₹ at risk, city & scam-type exposure |
| 📏 Evaluation | 120-message multilingual benchmark with adjustable threshold, confusion matrix, score separation |

## LLM layer (NVIDIA NIM)
- Endpoint: `https://integrate.api.nvidia.com/v1` (OpenAI-compatible)
- Model: `meta/llama-3.3-70b-instruct` (override with `NVIDIA_MODEL` secret)
- Setup — in Streamlit Cloud → App → Settings → **Secrets**:
```toml
NVIDIA_API_KEY = "nvapi-xxxxxxxxxxxx"
```
The key is server-side only — end users never configure anything. Without a key the platform degrades gracefully to the transparent rule engine, so the demo never depends on the API.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deliverables in this repo
- `app.py` — working prototype (this app)
- `deliverables/architecture.png` — architecture diagram
- `deliverables/FraudShield_Deck.pptx` — presentation deck
- `deliverables/DEMO_SCRIPT.md` — 2-minute demo video script

*All complaint, network and seizure data in the app is simulated for demonstration. Counterfeit screening is a heuristic demonstration; production deployment uses CNN models trained on RBI security features with UV/IR sensor input.*
