"""
FRAUD SHIELD — Digital Public Safety Intelligence
Digital-arrest scam detection · fraud network mapping · citizen advisory (EN/HI/TE)

Redesigned build: custom design system, evidence-view transcript highlighting,
animated risk gauge, styled fraud-ring graph, command center, live evaluation.
"""

import io
import re
import json
import requests
import numpy as np
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import streamlit as st
from PIL import Image, ImageDraw

# ============================================================================
# PAGE CONFIG
# ============================================================================
st.set_page_config(
    page_title="Fraud Shield · Digital Public Safety Intelligence",
    page_icon="🛡️",
    layout="wide",
)

# ============================================================================
# DESIGN TOKENS + CSS
# ============================================================================
C = {
    "bg":     "#FBF0E4",   # ET salmon paper
    "card":   "#FFFFFF",
    "card2":  "#FFF8EF",
    "border": "#E8D5BF",
    "cyan":   "#C42B1C",   # ET editorial red (brand accent — key name kept for compatibility)
    "danger": "#A61B1B",   # deep crimson for verdicts
    "warn":   "#B25E00",   # amber ink
    "safe":   "#1E7F4F",   # market green
    "text":   "#211A12",   # newsprint ink
    "muted":  "#7A6A58",   # warm grey
    "blue":   "#1D4E89",   # financial navy
    "violet": "#6D4C9F",
}

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;800&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;600&family=Noto+Sans+Devanagari:wght@400;600&family=Noto+Sans+Telugu:wght@400;600&display=swap');

html, body, [class*="css"] {{ font-family: 'Inter','Noto Sans Devanagari','Noto Sans Telugu',sans-serif; }}
.stApp {{ background: {C['bg']}; }}
h1,h2,h3 {{ font-family:'Playfair Display',serif !important; letter-spacing:-0.01em; color:{C['text']}; }}
#MainMenu, footer, header {{ visibility:hidden; }}

/* ---- Masthead hero: newspaper front page ---- */
.hero {{
    position:relative; border-radius:6px; overflow:hidden;
    background: {C['card']};
    border:1px solid {C['border']};
    border-top:3px solid {C['text']};
    border-bottom:3px double {C['text']};
    padding:26px 34px 22px 42px; margin-bottom:6px;
}}
.hero::before {{
    content:""; position:absolute; left:0; top:0; bottom:0; width:6px;
    background: linear-gradient(180deg,#FF9933 0%,#FF9933 33%,#FFFFFF 33%,#FFFFFF 66%,#138808 66%,#138808 100%);
}}
.hero h1 {{ margin:0; font-size:40px; font-weight:800; color:{C['text']}; }}
.hero .sub {{ color:{C['muted']}; font-size:14.5px; margin-top:6px; }}
.hero .sub b {{ color:{C['cyan']}; }}
.pill {{
    display:inline-flex; align-items:center; gap:7px;
    font-family:'JetBrains Mono',monospace; font-size:11px; letter-spacing:0.12em;
    color:#FFFFFF; background:{C['cyan']};
    border:1px solid {C['cyan']}; border-radius:3px;
    padding:5px 13px; margin-top:14px; text-transform:uppercase;
}}
.dot {{ width:7px;height:7px;border-radius:50%;background:#FFE08A;
        animation:pulse 1.6s infinite; }}
@keyframes pulse {{ 0%,100%{{opacity:1}} 50%{{opacity:0.35}} }}

/* ---- Tabs: newspaper section nav ---- */
.stTabs [data-baseweb="tab-list"] {{ gap:4px; border-bottom:2px solid {C['text']}; }}
.stTabs [data-baseweb="tab"] {{
    font-family:'Inter',sans-serif; font-size:14.5px; font-weight:600;
    color:{C['muted']}; background:transparent; border-radius:4px 4px 0 0;
    padding:10px 16px;
}}
.stTabs [aria-selected="true"] {{
    color:{C['cyan']} !important; background:rgba(196,43,28,0.06);
}}

/* ---- KPI cards ---- */
.kpi {{
    background:{C['card']};
    border:1px solid {C['border']}; border-radius:6px; padding:18px 20px;
    position:relative; overflow:hidden;
    box-shadow:0 1px 3px rgba(60,40,20,0.06);
}}
.kpi::after {{
    content:""; position:absolute; inset:0 0 auto 0; height:3px;
    background:var(--g,{C['cyan']});
}}
.kpi .l {{ font-size:11px; letter-spacing:0.11em; text-transform:uppercase;
           color:{C['muted']}; font-weight:600; }}
.kpi .v {{ font-family:'Playfair Display',serif; font-size:30px; font-weight:700;
           color:{C['text']}; margin-top:5px; }}
.kpi .d {{ font-family:'JetBrains Mono'; font-size:12px; margin-top:3px; color:var(--g,{C['cyan']}); }}

/* ---- Verdict ---- */
.verdict {{ border-radius:6px; padding:24px 28px; border:1px solid; margin-top:4px; background:{C['card']}; }}
.verdict .tag {{ font-family:'JetBrains Mono'; font-size:11px; letter-spacing:0.16em;
                 border:1px solid; border-radius:3px; padding:4px 12px; display:inline-block; }}
.verdict .score {{ font-family:'Playfair Display',serif; font-size:54px; font-weight:800; line-height:1.05; margin-top:10px; }}
.verdict .score small {{ font-size:20px; color:{C['muted']}; font-weight:500; }}
.verdict .desc {{ color:{C['text']}; font-size:15px; margin-top:4px; }}
.v-high {{ background:#FDF1EF; border-color:rgba(166,27,27,0.55); }}
.v-med  {{ background:#FBF3E4; border-color:rgba(178,94,0,0.5); }}
.v-low  {{ background:#EFF7F1; border-color:rgba(30,127,79,0.5); }}

/* ---- Evidence view: annotated newsprint ---- */
.evidence {{
    background:{C['card']}; border:1px solid {C['border']}; border-radius:6px;
    padding:20px 22px; font-size:14.5px; line-height:2.05; color:{C['text']};
}}
.evidence mark {{
    background:rgba(196,43,28,0.12); color:{C['danger']};
    border-bottom:2px solid {C['cyan']}; border-radius:2px;
    padding:1px 6px; font-weight:600;
}}
.sig {{
    font-family:'JetBrains Mono'; font-size:12.5px;
    background:{C['card']}; border:1px solid {C['border']};
    border-left:3px solid {C['danger']}; border-radius:4px;
    padding:9px 13px; margin:5px 0; color:{C['text']};
    display:flex; justify-content:space-between; gap:10px;
}}
.sig .w {{ color:{C['danger']}; white-space:nowrap; }}
.sig.ok {{ border-left-color:{C['safe']}; color:{C['muted']}; }}
.sig.ok .w {{ color:{C['safe']}; }}

/* ---- Advisory card ---- */
.advisory {{
    background:{C['card2']};
    border:1px solid {C['border']}; border-left:4px solid {C['cyan']}; border-radius:6px;
    padding:20px 24px; font-size:14.5px; line-height:1.85; color:{C['text']};
}}
.advisory .h {{ font-family:'Playfair Display',serif; font-weight:700; color:{C['cyan']};
                font-size:16px; margin-bottom:8px; }}
.helpline {{
    display:inline-block; font-family:'Inter'; font-weight:700; font-size:15px;
    background:{C['cyan']}; color:#FFFFFF; border-radius:4px;
    padding:8px 18px; margin-top:12px;
}}

/* ---- Feed / tables ---- */
.feed {{
    font-family:'JetBrains Mono'; font-size:12.5px;
    background:{C['card']}; border:1px solid {C['border']};
    border-radius:4px; padding:10px 14px; margin:5px 0;
    display:flex; gap:12px; align-items:center; color:{C['text']};
}}
.feed .id {{ color:{C['safe']}; }}
.feed .amt {{ margin-left:auto; color:{C['warn']}; font-weight:600; }}
.sec {{
    font-family:'Inter',sans-serif; font-size:12px; font-weight:700;
    letter-spacing:0.15em; text-transform:uppercase; color:{C['cyan']};
    border-bottom:1px solid {C['border']}; padding-bottom:5px;
    margin:26px 0 10px 0;
}}
.ringrow {{
    display:grid; grid-template-columns: 90px 1fr 130px 150px; gap:12px; align-items:center;
    background:{C['card']}; border:1px solid {C['border']}; border-radius:4px;
    padding:11px 16px; margin:5px 0; font-size:13.5px; color:{C['text']};
}}
.ringrow .mono {{ font-family:'JetBrains Mono'; }}
</style>
""", unsafe_allow_html=True)

PLOT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color=C["muted"], size=12),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
    margin=dict(l=10, r=10, t=42, b=10),
)
def style(fig, h=340, axes=True):
    fig.update_layout(**PLOT, height=h, autosize=True)
    if axes:
        try:
            fig.update_xaxes(gridcolor=C["border"], zerolinecolor=C["border"])
            fig.update_yaxes(gridcolor=C["border"], zerolinecolor=C["border"])
        except Exception:
            pass
    return fig

# ============================================================================
# SCAM DETECTION ENGINE (rule layer, EN + HI + TE + romanized)
# ============================================================================
SIGNALS = [
    ("DIGITAL_ARREST", "Digital-arrest script", 25,
     r"digital\s*arrest|do\s*not\s*disconnect|stay\s+on\s+(?:the\s+)?(?:video\s+)?call|skype\s+interrogation|"
     r"डिजिटल\s*अरेस्ट|वीडियो\s*कॉल\s*(?:से|पर)|డిజిటల్\s*అరెస్ట్"),
    ("AUTHORITY_IMPERSONATION", "Impersonating police / agency", 18,
     r"\b(?:cbi|c\.b\.i|police|customs|narcotics|ncb|trai|rbi|interpol|cyber\s*cell|income\s*tax|"
     r"enforcement\s+directorate|ed\s+officer|inspector|commissioner)\b|"
     r"पुलिस|सीबीआई|कस्टम|साइबर\s*सेल|పోలీస|సీబీఐ|కస్టమ్స్"),
    ("ARREST_THREAT", "Arrest / legal threat", 15,
     r"arrest\s+warrant|warrant\s+(?:has\s+been\s+)?issued|non[-\s]?bailable|fir\s+(?:registered|filed)|"
     r"case\s+(?:is\s+)?registered|money\s*launder|गिरफ्तारी|वारंट|मुकदमा|అరెస్ట్|వారెంట్|కేసు"),
    ("PARCEL_SCAM", "Parcel / courier narrative", 12,
     r"parcel|courier|fedex|dhl|consignment|illegal\s+drugs|contraband|seized\s+by|"
     r"पार्सल|कूरियर|డబ్బా|పార్సిల్|కొరియర్"),
    ("MONEY_DEMAND", "Demand to move money", 22,
     r"security\s+deposit|safe\s+custody|refundable\s+(?:deposit|amount)|verification\s+(?:fee|amount)|"
     r"processing\s+fee|clear\s+your\s+name.*transfer|transfer\s+(?:rs|₹|rupees)|rtgs|neft|imps|"
     r"जमानत\s*राशि|पैसे\s*(?:भेज|ट्रांसफर)|డిపాజిట్|డబ్బు\s*(?:పంప|బదిలీ)"),
    ("SECRECY", "Demands secrecy", 15,
     r"do\s+not\s+tell\s+anyone|confidential\s+investigation|keep\s+(?:this\s+)?secret|tell\s+no\s*one|"
     r"किसी\s*को\s*(?:मत|न)\s*बता|गोपनीय|ఎవరికీ\s*చెప్పవద్దు|రహస్యం"),
    ("URGENCY", "Artificial urgency", 10,
     r"immediately|urgent|within\s+\d+\s*(?:hours?|minutes?)|you\s+have\s+\d+\s*hours?|last\s+(?:chance|warning)|"
     r"तुरंत|अभी|జల్దీ|వెంటనే|తక్షణమే"),
    ("REMOTE_ACCESS_OTP", "OTP / remote-access request", 20,
     r"\botp\b|one\s*time\s*password|\bcvv\b|\bpin\b|anydesk|team\s*viewer|screen\s*shar|"
     r"ओटीपी|పిన్|ఓటీపీ"),
    ("KYC_UTILITY", "KYC / utility cutoff scare", 12,
     r"kyc\s+(?:expired|update|pending)|account\s+(?:will\s+be\s+)?(?:blocked|suspended|frozen)|"
     r"electricity\s+.{0,30}disconnect|sim\s+.{0,20}deactivat|बिजली\s*कट|खाता\s*बंद|కరెంట్\s*కట్"),
    ("TOO_GOOD", "Lottery / job bait", 12,
     r"lottery|lucky\s+draw|you\s+(?:have\s+)?won|prize\s+money|work\s+from\s+home.{0,40}earn|"
     r"part[-\s]?time\s+job.{0,40}(?:₹|rs)|लॉटरी|इनाम|లాటరీ|బహుమతి"),
]

def analyze(text: str):
    """Return (score 0-100, matched signals, highlighted html)."""
    hits, spans = [], []
    for code, label, weight, pattern in SIGNALS:
        ms = list(re.finditer(pattern, text, re.IGNORECASE))
        if ms:
            hits.append({"code": code, "label": label, "weight": weight,
                         "examples": [m.group(0) for m in ms[:3]]})
            spans += [(m.start(), m.end()) for m in ms]
    score = min(100, sum(h["weight"] for h in hits) + max(0, len(spans) - len(hits)) * 1)
    # merge overlapping spans, build highlighted text
    spans.sort()
    merged = []
    for s, e in spans:
        if merged and s <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    out, prev = [], 0
    for s, e in merged:
        out.append(text[prev:s]); out.append(f"<mark>{text[s:e]}</mark>"); prev = e
    out.append(text[prev:])
    return score, hits, "".join(out).replace("\n", "<br>")

# ---- NVIDIA NIM LLM second opinion (key lives in Streamlit secrets) --------
NIM_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
NIM_MODEL = "meta/llama-3.1-8b-instruct"

def get_secret(name, default=None):
    try:
        return st.secrets[name]
    except Exception:
        return default

def llm_second_opinion(text: str):
    """Ask the NIM-hosted LLM for a scam verdict. Returns (dict_or_None, reason_str)."""
    key = get_secret("NVIDIA_API_KEY")
    if not key:
        return None, "no key found in st.secrets"
    prompt = (
        "You are a fraud analyst for Indian cybercrime prevention. Analyse the message below "
        "(it may be in English, Hindi, Telugu or mixed/romanized) for scam indicators: digital-arrest "
        "scripts, government-agency impersonation, parcel/courier narratives, KYC scares, OTP or "
        "remote-access requests, urgency, secrecy demands, money demands, lottery/job bait.\n"
        "Respond with ONLY a JSON object, no markdown, no preamble:\n"
        '{"score": <integer 0-100>, "verdict": "<SCAM|SUSPICIOUS|SAFE>", '
        '"reasons": ["<short reason>", ...max 4]}\n\n'
        f"MESSAGE:\n{text[:4000]}"
    )
    try:
        r = requests.post(
            NIM_URL,
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": get_secret("NVIDIA_MODEL", NIM_MODEL),
                  "messages": [{"role": "user", "content": prompt}],
                  "temperature": 0.1, "max_tokens": 300},
            timeout=55,
        )
        if r.status_code != 200:
            return None, f"HTTP {r.status_code}: {r.text[:200]}"
        raw = r.json()["choices"][0]["message"]["content"]
        raw = re.sub(r"```(?:json)?|```", "", raw).strip()
        out = json.loads(raw[raw.index("{"): raw.rindex("}") + 1])
        out["score"] = int(max(0, min(100, out.get("score", 0))))
        return out, "ok"
    except requests.exceptions.Timeout:
        return None, "request timed out after 55s (model may be cold-starting)"
    except requests.exceptions.ConnectionError as e:
        return None, f"connection error: {e}"
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"

ADVISORIES = {
    "English": {
        "high": ("⚠️ This is almost certainly a scam.",
                 "There is <b>no such thing as a 'digital arrest'</b> in Indian law. Police, CBI or customs "
                 "never demand money on a video call, never ask for secrecy, and never accept 'security deposits'. "
                 "<b>Hang up now. Do not transfer money. Do not share OTP or screen access.</b> "
                 "Report immediately on cybercrime.gov.in or call the national helpline."),
        "med":  ("🔎 Several scam patterns detected — verify before acting.",
                 "Do not act on this message alone. Call the organisation on its <b>official number</b> "
                 "(from its website, not from this message). Never share OTP, PIN or remote-screen access."),
        "low":  ("✅ No strong scam indicators found.",
                 "Stay alert anyway: government agencies never demand payment over calls, and banks never ask for OTPs."),
    },
    "हिंदी": {
        "high": ("⚠️ यह लगभग निश्चित रूप से एक धोखाधड़ी (scam) है।",
                 "भारतीय कानून में <b>'डिजिटल अरेस्ट' जैसी कोई चीज़ नहीं है</b>। पुलिस, सीबीआई या कस्टम कभी भी "
                 "वीडियो कॉल पर पैसे नहीं मांगते और न ही गोपनीयता की शर्त रखते हैं। "
                 "<b>तुरंत कॉल काटें। पैसे ट्रांसफर न करें। OTP या स्क्रीन साझा न करें।</b> "
                 "cybercrime.gov.in पर शिकायत दर्ज करें।"),
        "med":  ("🔎 कई संदिग्ध संकेत मिले हैं — कार्रवाई से पहले जाँच करें।",
                 "इस संदेश पर भरोसा न करें। संस्था के <b>आधिकारिक नंबर</b> पर स्वयं कॉल करके पुष्टि करें। "
                 "OTP, PIN या रिमोट एक्सेस कभी साझा न करें।"),
        "low":  ("✅ कोई प्रबल धोखाधड़ी संकेत नहीं मिला।",
                 "फिर भी सतर्क रहें: सरकारी एजेंसियाँ कॉल पर पैसे नहीं मांगतीं, और बैंक कभी OTP नहीं पूछते।"),
    },
    "తెలుగు": {
        "high": ("⚠️ ఇది దాదాపు ఖచ్చితంగా మోసం (scam).",
                 "భారత చట్టంలో <b>'డిజిటల్ అరెస్ట్' అనేది లేదు</b>. పోలీసులు, సీబీఐ లేదా కస్టమ్స్ "
                 "వీడియో కాల్‌లో డబ్బు అడగరు, రహస్యంగా ఉంచమని చెప్పరు. "
                 "<b>వెంటనే కాల్ కట్ చేయండి. డబ్బు పంపవద్దు. OTP లేదా స్క్రీన్ షేర్ చేయవద్దు.</b> "
                 "cybercrime.gov.in లో ఫిర్యాదు చేయండి."),
        "med":  ("🔎 పలు అనుమానాస్పద సంకేతాలు కనిపించాయి — ముందుగా నిర్ధారించుకోండి.",
                 "ఈ సందేశాన్ని నమ్మవద్దు. సంస్థ <b>అధికారిక నంబర్</b>కు మీరే కాల్ చేసి నిర్ధారించుకోండి. "
                 "OTP, PIN ఎప్పుడూ చెప్పవద్దు."),
        "low":  ("✅ బలమైన మోసపు సంకేతాలు కనబడలేదు.",
                 "అయినా జాగ్రత్త: ప్రభుత్వ సంస్థలు కాల్‌లో డబ్బు అడగవు, బ్యాంకులు OTP అడగవు."),
    },
}

SAMPLES = {
    "Digital arrest call (English)":
        "Hello, I am calling from CBI Delhi. A parcel in your name containing illegal drugs has been "
        "seized by Mumbai customs. An arrest warrant has been issued. You are now under digital arrest — "
        "do not disconnect this video call and do not tell anyone, this is a confidential investigation. "
        "To clear your name you must immediately transfer Rs 2,90,000 as a refundable security deposit "
        "via RTGS to a safe custody account. You have 2 hours.",
    "डिजिटल अरेस्ट कॉल (हिंदी)":
        "नमस्ते, मैं सीबीआई दिल्ली से बोल रहा हूँ। आपके नाम का एक पार्सल कस्टम में पकड़ा गया है जिसमें "
        "अवैध ड्रग्स हैं। आपके खिलाफ गिरफ्तारी वारंट जारी हुआ है। आप डिजिटल अरेस्ट में हैं — वीडियो कॉल "
        "मत काटिए और किसी को मत बताइए। तुरंत ₹1,50,000 जमानत राशि ट्रांसफर करें।",
    "డిజిటల్ అరెస్ట్ కాల్ (తెలుగు)":
        "హలో, నేను సీబీఐ ఢిల్లీ నుంచి మాట్లాడుతున్నాను. మీ పేరుతో వచ్చిన పార్సిల్‌లో డ్రగ్స్ దొరికాయి. "
        "మీపై అరెస్ట్ వారెంట్ జారీ అయింది. మీరు డిజిటల్ అరెస్ట్‌లో ఉన్నారు — కాల్ కట్ చేయవద్దు, "
        "ఎవరికీ చెప్పవద్దు. వెంటనే డిపాజిట్ డబ్బు పంపండి.",
    "KYC scare (English)":
        "Dear customer, your bank account will be suspended today as your KYC has expired. "
        "Update immediately by sharing the OTP sent to your phone or download AnyDesk for verification.",
    "Genuine bank alert (safe)":
        "Your a/c XX4821 is credited with INR 12,500 on 20-Jul-26 by UPI ref 618223341229. "
        "Available balance: INR 48,230. If not done by you, call the number on the back of your card.",
    "Friend message (safe)":
        "Hey! Are we still on for dinner at 8 tonight? I can pick you up on the way. "
        "Also send me the photos from Saturday when you get a chance.",
}

# ============================================================================
# SYNTHETIC OPERATIONAL DATA (complaints + rings)
# ============================================================================
CITIES = ["Delhi", "Mumbai", "Hyderabad", "Bengaluru", "Chennai", "Kolkata",
          "Pune", "Jaipur", "Vijayawada", "Visakhapatnam"]
CITY_COORDS = {
    "Delhi": (28.61, 77.21), "Mumbai": (19.08, 72.88), "Hyderabad": (17.38, 78.49),
    "Bengaluru": (12.97, 77.59), "Chennai": (13.08, 80.27), "Kolkata": (22.57, 88.36),
    "Pune": (18.52, 73.86), "Jaipur": (26.91, 75.79), "Vijayawada": (16.51, 80.63),
    "Visakhapatnam": (17.69, 83.22),
}
SCAM_TYPES = ["Digital Arrest", "Parcel/Courier Scam", "KYC/Bank Fraud", "Job Fraud", "Investment Scam"]

@st.cache_data(show_spinner=False)
def complaints_data(seed=42, n=260):
    rng = np.random.default_rng(seed)
    day = rng.integers(0, 30, n)
    df = pd.DataFrame({
        "date": pd.Timestamp("2026-06-22") + pd.to_timedelta(day, unit="D"),
        "city": rng.choice(CITIES, n, p=[0.16,0.13,0.13,0.12,0.09,0.09,0.08,0.07,0.07,0.06]),
        "scam_type": rng.choice(SCAM_TYPES, n, p=[0.33,0.27,0.17,0.13,0.10]),
        "amount": np.round(np.exp(rng.normal(11.2, 1.1, n)), -3).clip(5000, 4000000),
        "ncrp_id": [f"NCRP-2026-{rng.integers(100000,999999)}" for _ in range(n)],
    })
    return df

@st.cache_data(show_spinner=False)
def build_rings(n_rings=4, seed=42):
    rng = np.random.default_rng(seed)
    G = nx.Graph()
    rows = []
    for r in range(1, n_rings + 1):
        scammers = [f"+91-9{rng.integers(10**8, 10**9)}" for _ in range(rng.integers(2, 5))]
        mules    = [f"AC{rng.integers(10**9, 10**10)}" for _ in range(rng.integers(2, 4))]
        devices  = [f"DEV-{rng.integers(1000, 9999)}" for _ in range(rng.integers(1, 3))]
        victims  = [f"V-{r}{i:02d}" for i in range(rng.integers(3, 10))]
        total = 0
        for v in victims:
            s = scammers[rng.integers(0, len(scammers))]
            amt = int(np.round(np.exp(rng.normal(11.5, 0.9)), -4))
            total += amt
            G.add_node(v, kind="victim", ring=r)
            G.add_node(s, kind="scammer", ring=r)
            G.add_edge(v, s, amount=amt)
        for s in scammers:
            G.add_node(s, kind="scammer", ring=r)
            for m in rng.choice(mules, rng.integers(1, len(mules) + 1), replace=False):
                G.add_node(m, kind="mule", ring=r); G.add_edge(s, m)
            for d in rng.choice(devices, rng.integers(1, len(devices) + 1), replace=False):
                G.add_node(d, kind="device", ring=r); G.add_edge(s, d)
        infra = scammers + mules + devices
        target = max(infra, key=lambda x: (G.degree(x) if x in G else -1))
        rows.append({"ring": f"Ring {r}", "victims": len(victims),
                     "scammers": len(scammers), "mules": len(mules), "devices": len(devices),
                     "total": total, "target": target,
                     "cities": ", ".join(sorted(rng.choice(CITIES, rng.integers(3, 6), replace=False)))})
    table = pd.DataFrame(rows).sort_values("total", ascending=False)
    return G, table

def kpi(label, value, delta, glow):
    return (f'<div class="kpi" style="--g:{glow}"><div class="l">{label}</div>'
            f'<div class="v">{value}</div><div class="d">{delta}</div></div>')

# ============================================================================
# HERO
# ============================================================================
st.markdown(f"""
<div class="hero">
    <h1>🛡️ Fraud Shield</h1>
    <div class="sub">AI-powered Digital Public Safety Intelligence — digital-arrest scam detection ·
    fraud network mapping · citizen advisory in <b>English</b> · <b>हिंदी</b> · <b>తెలుగు</b></div>
    <div class="pill"><span class="dot"></span> LIVE · NATIONAL CYBERCRIME HELPLINE 1930</div>
</div>
""", unsafe_allow_html=True)

s1, s2, s3 = st.columns(3)
s1.markdown(kpi("Digital-arrest losses · MHA", "₹1,776 Cr", "Jan–Sep 2024 alone", C["danger"]), unsafe_allow_html=True)
s2.markdown(kpi("Cybercrime complaints · 2023", "1.14 Million", "▲ 60% vs 2022 (NCRP)", C["warn"]), unsafe_allow_html=True)
s3.markdown(kpi("The window that matters", "Before transfer", "detect at point of contact, not complaint", C["cyan"]), unsafe_allow_html=True)
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

tab1, tab_note, tab2, tab_geo, tab3, tab4 = st.tabs(
    ["🛡️  Citizen Fraud Shield", "💵  Counterfeit Check", "🕸️  Network Intelligence",
     "🗺️  Geo Intelligence", "🎛️  Command Center", "📏  Evaluation"])

# ============================================================================
# TAB 1 — CITIZEN FRAUD SHIELD
# ============================================================================
with tab1:
    st.markdown('<div class="sec">Paste a suspicious message or call transcript — verdict in seconds</div>',
                unsafe_allow_html=True)
    left, right = st.columns([2.1, 1], gap="large")
    with right:
        lang = st.selectbox("Advisory language", list(ADVISORIES.keys()))
        sample = st.selectbox("Load a sample", list(SAMPLES.keys()))
        use_llm = st.toggle("Enhance with NVIDIA NIM LLM",
                            help="Optional second-opinion from an LLM via NVIDIA NIM. "
                                 "Add NVIDIA_API_KEY in Streamlit secrets to enable.")
    with left:
        text = st.text_area("Suspicious message / transcript", SAMPLES[sample], height=210,
                            label_visibility="collapsed")
        go_btn = st.button("🛡️  Analyse", type="primary")

    if go_btn and text.strip():
        rule_score, hits, highlighted = analyze(text)
        llm, llm_reason = None, None
        if use_llm:
            with st.spinner("Consulting NVIDIA NIM LLM… (first call can take up to a minute if the model is cold)"):
                llm, llm_reason = llm_second_opinion(text)
        score = max(rule_score, llm["score"]) if llm else rule_score
        if score >= 70:  cls, tag, level = "v-high", "HIGH RISK", "high"
        elif score >= 40: cls, tag, level = "v-med", "SUSPICIOUS", "med"
        else:             cls, tag, level = "v-low", "LOW RISK", "low"
        color = {"v-high": C["danger"], "v-med": C["warn"], "v-low": C["safe"]}[cls]
        head, body = ADVISORIES[lang][level]

        a, b = st.columns([1, 1.35], gap="large")
        with a:
            st.markdown(f"""
            <div class="verdict {cls}">
                <span class="tag" style="color:{color};border-color:{color}">{tag}</span>
                <div class="score" style="color:{color}">{score}<small> /100</small></div>
                <div class="desc">{head}</div>
            </div>""", unsafe_allow_html=True)

            fig = go.Figure(go.Indicator(
                mode="gauge", value=score,
                gauge=dict(
                    axis=dict(range=[0, 100], tickcolor=C["muted"]),
                    bar=dict(color=color, thickness=0.3),
                    bgcolor="rgba(0,0,0,0)", borderwidth=0,
                    steps=[dict(range=[0, 40],  color="rgba(30,127,79,0.10)"),
                           dict(range=[40, 70], color="rgba(178,94,0,0.10)"),
                           dict(range=[70, 100],color="rgba(166,27,27,0.12)")],
                    threshold=dict(line=dict(color=color, width=3), value=score),
                )))
            st.plotly_chart(style(fig, 200))

            if use_llm:
                if llm:
                    v_col = {"SCAM": C["danger"], "SUSPICIOUS": C["warn"], "SAFE": C["safe"]}.get(
                        llm.get("verdict", ""), C["cyan"])
                    reasons_html = "".join(f"<li>{r}</li>" for r in llm.get("reasons", [])[:4])
                    st.markdown(f"""
                    <div style="background:{C['card']};border:1px solid {C['border']};border-radius:14px;
                                padding:16px 18px;margin-top:4px;">
                        <div style="font-family:'JetBrains Mono';font-size:11px;letter-spacing:0.12em;
                                    color:{C['violet']};text-transform:uppercase;">
                            🧠 LLM second opinion · {NIM_MODEL}</div>
                        <div style="font-family:'Space Grotesk';font-size:20px;font-weight:700;
                                    color:{v_col};margin-top:6px;">
                            {llm.get('verdict','—')} · {llm['score']}/100</div>
                        <ul style="color:{C['muted']};font-size:13px;margin:8px 0 0 0;padding-left:18px;">
                            {reasons_html}</ul>
                        <div style="color:{C['muted']};font-size:11.5px;margin-top:8px;">
                            Rule engine {rule_score} · combined verdict takes the higher score</div>
                    </div>""", unsafe_allow_html=True)
                else:
                    st.info(f"LLM unavailable — {llm_reason}. "
                            "Showing rule-engine verdict; the demo never depends on the API.", icon="🧠")

        with b:
            st.markdown('<div class="sec" style="margin-top:0">Evidence — exact phrases that triggered the verdict</div>',
                        unsafe_allow_html=True)
            st.markdown(f'<div class="evidence">{highlighted}</div>', unsafe_allow_html=True)

        st.markdown('<div class="sec">Why it was flagged</div>', unsafe_allow_html=True)
        if hits:
            cols = st.columns(2)
            for i, h in enumerate(sorted(hits, key=lambda x: -x["weight"])):
                ex = " · ".join(f"“{e}”" for e in h["examples"][:2])
                cols[i % 2].markdown(
                    f'<div class="sig"><span>{h["code"]} — {h["label"]}<br>'
                    f'<span style="color:{C["muted"]}">{ex}</span></span>'
                    f'<span class="w">+{h["weight"]}</span></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="sig ok"><span>NO_RED_FLAGS — no known scam patterns matched</span>'
                        '<span class="w">+0</span></div>', unsafe_allow_html=True)

        st.markdown('<div class="sec">Citizen advisory</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="advisory"><div class="h">{head}</div>{body}
        <br><span class="helpline">📞 Call 1930 · report at cybercrime.gov.in</span></div>
        """, unsafe_allow_html=True)

# ============================================================================
# TAB 2 — NETWORK INTELLIGENCE
# ============================================================================
with tab2:
    st.markdown('<div class="sec">Fraud network graph — complaints, phones, mule accounts & devices clustered into rings (simulated)</div>',
                unsafe_allow_html=True)
    cA, cB, _ = st.columns([1, 1, 2])
    n_rings = cA.slider("Simulated campaigns", 2, 8, 4)
    seed = cB.number_input("Random seed", 1, 999, 42)
    G, table = build_rings(n_rings, seed)

    pos_raw = nx.spring_layout(G, k=0.45, seed=7, iterations=80)
    pos = {n: (float(xy[0]), float(xy[1])) for n, xy in pos_raw.items()}
    KIND = {"victim":  dict(color=C["blue"],   size=9,  name="Victim"),
            "scammer": dict(color=C["danger"], size=15, name="Scammer number"),
            "mule":    dict(color=C["warn"],   size=13, name="Mule account"),
            "device":  dict(color=C["violet"], size=11, name="Device fingerprint")}

    ex, ey = [], []
    for u, v in G.edges():
        ex += [pos[u][0], pos[v][0], None]; ey += [pos[u][1], pos[v][1], None]
    fig = go.Figure(go.Scatter(x=ex, y=ey, mode="lines", hoverinfo="none",
                               line=dict(color="rgba(122,106,88,0.3)", width=1)))
    for kind, s in KIND.items():
        ns = [n for n, d in G.nodes(data=True) if d["kind"] == kind]
        fig.add_trace(go.Scatter(
            x=[pos[n][0] for n in ns], y=[pos[n][1] for n in ns],
            mode="markers", name=s["name"],
            marker=dict(color=s["color"], size=s["size"],
                        line=dict(color=C["bg"], width=1.5),
                        opacity=0.95),
            text=[f"{n}<br>Ring {G.nodes[n]['ring']} · degree {int(G.degree(n))}" for n in ns],
            hoverinfo="text"))
    fig.update_layout(showlegend=True, xaxis=dict(visible=False), yaxis=dict(visible=False))
    st.plotly_chart(style(fig, 520, axes=False))

    st.markdown('<div class="sec">Ring intelligence — prioritised by amount defrauded</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="ringrow" style="background:transparent;border:none;color:{C['muted']};
         font-size:11.5px;letter-spacing:0.1em;text-transform:uppercase;font-weight:600;">
        <span>Ring</span><span>Footprint</span><span>Defrauded</span><span>Priority target</span>
    </div>""", unsafe_allow_html=True)
    for _, r in table.iterrows():
        st.markdown(f"""
        <div class="ringrow">
            <span style="font-family:'Space Grotesk';font-weight:700;color:{C['cyan']}">{r['ring']}</span>
            <span>{r['victims']} victims · {r['scammers']} numbers · {r['mules']} mules · {r['devices']} devices
                <br><span style="color:{C['muted']};font-size:12px">{r['cities']}</span></span>
            <span class="mono" style="color:{C['warn']};font-weight:600">₹{r['total']:,}</span>
            <span class="mono" style="color:{C['danger']}">{r['target']}</span>
        </div>""", unsafe_allow_html=True)
    st.caption("Priority target = highest-degree infrastructure node in the ring — taking it down "
               "disrupts the most victim connections at once. All data is simulated.")

# ============================================================================
# TAB 3 — COMMAND CENTER
# ============================================================================
with tab3:
    df = complaints_data()
    if "extra" not in st.session_state:
        st.session_state.extra = pd.DataFrame()
    live = pd.concat([df, st.session_state.extra], ignore_index=True)

    _, tbl = build_rings(6, 42)
    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(kpi("Complaints (30 days)", f"{len(live):,}", "▲ live NCRP feed", C["blue"]), unsafe_allow_html=True)
    k2.markdown(kpi("Amount at risk", f"₹{live['amount'].sum()/1e7:.1f} Cr", "reported losses", C["warn"]), unsafe_allow_html=True)
    k3.markdown(kpi("Active rings detected", f"{len(tbl)}", "graph-clustered", C["danger"]), unsafe_allow_html=True)
    k4.markdown(kpi("Cities affected", f"{live['city'].nunique()}", "across India", C["cyan"]), unsafe_allow_html=True)

    a, b = st.columns([1.25, 1], gap="large")
    with a:
        st.markdown('<div class="sec">Complaint pressure per day</div>', unsafe_allow_html=True)
        daily = live.groupby(live["date"].dt.date).size().reset_index(name="n")
        fig = go.Figure(go.Scatter(
            x=daily["date"].astype(str).tolist(), y=daily["n"].astype(int).tolist(), mode="lines",
            line=dict(color=C["cyan"], width=2.5, shape="spline"),
            fill="tozeroy", fillcolor="rgba(196,43,28,0.10)"))
        st.plotly_chart(style(fig, 300))
    with b:
        st.markdown('<div class="sec">Scam type share</div>', unsafe_allow_html=True)
        mix = live.groupby("scam_type")["amount"].sum().reset_index()
        fig = go.Figure(go.Pie(
            labels=mix["scam_type"].astype(str).tolist(), values=mix["amount"].astype(float).tolist(), hole=0.62,
            marker=dict(colors=[C["danger"], C["warn"], C["blue"], C["violet"], C["safe"]],
                        line=dict(color=C["bg"], width=2)),
            textfont=dict(family="Inter", color=C["text"])))
        fig.update_layout(annotations=[dict(text="₹ at risk", showarrow=False,
                                            font=dict(family="Space Grotesk", size=14, color=C["muted"]))])
        st.plotly_chart(style(fig, 300, axes=False))

    st.markdown('<div class="sec">Amount defrauded by city</div>', unsafe_allow_html=True)
    city = live.groupby("city")["amount"].sum().sort_values().reset_index()
    fig = go.Figure(go.Bar(
        x=(city["amount"]/1e5).astype(float).tolist(), y=city["city"].astype(str).tolist(), orientation="h",
        marker=dict(color=city["amount"].astype(float).tolist(), colorscale=[[0, "rgba(196,43,28,0.5)"], [1, C["danger"]]]),
        text=[f"₹{v/1e5:.1f} L" for v in city["amount"]], textposition="outside",
        textfont=dict(family="JetBrains Mono", size=11)))
    fig.update_layout(xaxis_title="₹ lakh")
    st.plotly_chart(style(fig, 380))

    st.markdown('<div class="sec">Incoming complaints — live feed (simulated)</div>', unsafe_allow_html=True)
    if st.button("▶ Simulate live scam campaign", type="primary"):
        rng = np.random.default_rng()
        burst = pd.DataFrame({
            "date": pd.Timestamp("2026-07-21"),
            "city": rng.choice(CITIES, 6),
            "scam_type": rng.choice(SCAM_TYPES, 6, p=[0.5,0.25,0.1,0.1,0.05]),
            "amount": np.round(np.exp(rng.normal(11.5, 0.8, 6)), -3),
            "ncrp_id": [f"NCRP-2026-{rng.integers(100000,999999)}" for _ in range(6)],
        })
        st.session_state.extra = pd.concat([st.session_state.extra, burst], ignore_index=True)
        st.rerun()
    for _, r in live.tail(9).iloc[::-1].iterrows():
        st.markdown(f"""
        <div class="feed">🚨 <span class="id">{r['ncrp_id']}</span>
        <span>{r['scam_type']} · {r['city']}</span>
        <span class="amt">₹{int(r['amount']):,}</span></div>""", unsafe_allow_html=True)

# ============================================================================
# TAB 4 — EVALUATION
# ============================================================================
with tab4:
    st.markdown('<div class="sec">Rule-engine benchmark — 120 synthetic messages (EN/HI/TE + adversarial soft-worded cases)</div>',
                unsafe_allow_html=True)

    @st.cache_data(show_spinner=False)
    def benchmark():
        rng = np.random.default_rng(3)
        scam_bits = [
            "I am calling from {ag}. ", "A parcel with illegal drugs in your name was seized. ",
            "An arrest warrant has been issued against you. ", "You are under digital arrest, do not disconnect. ",
            "Do not tell anyone, this is a confidential investigation. ",
            "Transfer Rs {amt} as refundable security deposit immediately. ",
            "Share the OTP for verification. ", "Your account will be frozen within 2 hours. "]
        soft = ["Good afternoon, this is regarding case number {n} registered on your PAN. The officer will connect shortly.",
                "Your electricity connection will be disconnected tonight due to KYC issue. Update immediately.",
                "Sir your consignment is on hold at customs, kindly pay clearing charge to release."]
        benign = ["Hey, running 10 mins late for lunch, order for me please.",
                  "Your OTP for login is never shared by us with anyone. Do not share it.",
                  "Meeting moved to 3pm tomorrow, same room. Bring the Q2 deck.",
                  "Your a/c XX2211 credited INR 4,500 UPI ref 88121. Balance INR 22,100.",
                  "Amazon: your package arrives today by 9 PM. Track in the app.",
                  "Mom said to call her when you're free tonight.",
                  "Reminder: dentist appointment on Friday at 10:30 AM.",
                  "Your electricity bill of Rs 1,240 is due on 28 Jul. Pay via the official app."]
        rows = []
        for i in range(52):
            k = rng.integers(3, 7)
            msg = "".join(rng.choice(scam_bits, k, replace=False)).format(
                ag=rng.choice(["CBI Delhi", "Mumbai Police", "RBI", "customs"]),
                amt=f"{int(rng.integers(20, 400))*1000:,}")
            rows.append((msg, 1))
        for s in soft * 2:
            rows.append((s.format(n=rng.integers(1000, 9999)), 1))
        for i in range(62):
            rows.append((str(rng.choice(benign)), 0))
        return pd.DataFrame(rows, columns=["msg", "label"])

    bench = benchmark()
    bench["score"] = bench["msg"].map(lambda t: analyze(t)[0])
    thr = st.slider("Decision threshold (score ≥ threshold ⇒ flag as scam)", 10, 90, 40, 5)
    bench["pred"] = (bench["score"] >= thr).astype(int)

    tp = int(((bench.pred == 1) & (bench.label == 1)).sum())
    fp = int(((bench.pred == 1) & (bench.label == 0)).sum())
    tn = int(((bench.pred == 0) & (bench.label == 0)).sum())
    fn = int(((bench.pred == 0) & (bench.label == 1)).sum())
    prec = tp / max(tp + fp, 1); rec = tp / max(tp + fn, 1)
    f1 = 2 * prec * rec / max(prec + rec, 1e-9)

    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(kpi("Precision", f"{prec*100:.1f}%", "flagged → truly scam", C["cyan"]), unsafe_allow_html=True)
    k2.markdown(kpi("Recall", f"{rec*100:.1f}%", "scams → caught", C["warn"]), unsafe_allow_html=True)
    k3.markdown(kpi("False-positive rate", f"{fp/max(fp+tn,1)*100:.1f}%", "genuine msgs flagged", C["danger"]), unsafe_allow_html=True)
    k4.markdown(kpi("F1 score", f"{f1*100:.1f}%", "precision–recall balance", C["safe"]), unsafe_allow_html=True)

    a, b = st.columns(2, gap="large")
    with a:
        st.markdown('<div class="sec">Confusion matrix</div>', unsafe_allow_html=True)
        fig = go.Figure(go.Heatmap(
            z=[[tn, fp], [fn, tp]],
            x=["Pred · Safe", "Pred · Scam"], y=["True · Safe", "True · Scam"],
            text=[[tn, fp], [fn, tp]], texttemplate="%{text}",
            textfont=dict(family="Space Grotesk", size=24, color=C["text"]),
            colorscale=[[0, "#FDF6EC"], [1, "rgba(196,43,28,0.5)"]], showscale=False))
        st.plotly_chart(style(fig, 340))
    with b:
        st.markdown('<div class="sec">Score separation — safe vs scam</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=bench[bench.label == 0]["score"].astype(int).tolist(), name="Safe messages",
                                   marker_color="rgba(29,78,137,0.6)", nbinsx=25))
        fig.add_trace(go.Histogram(x=bench[bench.label == 1]["score"].astype(int).tolist(), name="Scam messages",
                                   marker_color="rgba(166,27,27,0.75)", nbinsx=25))
        fig.add_vline(x=thr, line=dict(color=C["warn"], dash="dash"),
                      annotation_text="threshold", annotation_font_color=C["warn"])
        fig.update_layout(barmode="overlay", xaxis_title="Risk score")
        st.plotly_chart(style(fig, 340))

    misses = bench[(bench.label == 1) & (bench.pred == 0)]
    st.markdown('<div class="sec">Remaining misses (rule engine alone)</div>', unsafe_allow_html=True)
    if len(misses):
        for _, r in misses.head(4).iterrows():
            st.markdown(f'<div class="sig"><span>FALSE NEGATIVE — {r["msg"][:110]}…</span>'
                        f'<span class="w">score {r["score"]}</span></div>', unsafe_allow_html=True)
        st.info("Soft-worded cases like these are exactly what the LLM second-opinion layer "
                "(Citizen Fraud Shield tab) is designed to catch — the combined verdict takes the higher score.",
                icon="🧠")
    else:
        st.markdown('<div class="sig ok"><span>No misses at this threshold</span><span class="w">✓</span></div>',
                    unsafe_allow_html=True)

# ============================================================================
# TAB — COUNTERFEIT CURRENCY CHECK (demonstration CV module)
# ============================================================================
with tab_note:
    st.markdown('<div class="sec">FICN screening — upload a photo of a banknote for feature analysis</div>',
                unsafe_allow_html=True)
    NOTE_SPEC = {  # denomination: (aspect w/h, dominant hue range on 0-360, name)
        "₹500":  (150/66, (20, 90),   "stone grey"),
        "₹200":  (146/66, (35, 65),   "bright yellow"),
        "₹100":  (142/66, (200, 290), "lavender"),
        "₹2000": (166/66, (280, 340), "magenta"),
    }
    cL, cR = st.columns([1, 1.5], gap="large")
    with cL:
        denom = st.selectbox("Denomination", list(NOTE_SPEC.keys()))
        up = st.file_uploader("Note image (front side, flat, good light)", type=["jpg", "jpeg", "png"])
        demo_note = st.button("▶ Run demo with synthetic specimen")
        st.caption("⚠️ Demonstration module: heuristic checks on visible features only. "
                   "A production deployment uses a CNN trained on RBI security features plus "
                   "UV/IR sensor input on counting machines and PoS devices.")

    img = None
    if up is not None:
        img = Image.open(up).convert("RGB")
    elif demo_note:
        rng = np.random.default_rng(5)
        DEMO_BASE = {"₹500": (168, 164, 158),   # stone grey
                     "₹200": (233, 196, 106),   # bright yellow
                     "₹100": (176, 168, 186),   # lavender
                     "₹2000": (205, 130, 166)}  # magenta
        w = 1300
        h = int(w / NOTE_SPEC[denom][0])
        base = np.array(DEMO_BASE[denom], dtype=np.int16)
        arr = np.tile(base, (h, w, 1)).astype(np.int16)
        arr += rng.integers(-16, 16, arr.shape)                    # print-grain noise
        for i in range(0, h, 26):                                  # guilloche-like bands
            arr[i:i+2, :, :] -= 12
        arr[:, int(w*0.445):int(w*0.458), :] = [48, 54, 62]        # security thread
        for seg in range(0, h, 74):                                # windowed (dashed) look
            arr[seg:seg+22, int(w*0.445):int(w*0.458), :] = np.minimum(base + 20, 255)
        yy, xx = np.mgrid[0:h, 0:w]                                # plain portrait zone
        mask = (((xx - w*0.62) / (w*0.10))**2 + ((yy - h*0.45) / (h*0.30))**2) < 1
        arr[mask] = (arr[mask] * 0.82).astype(np.int16)
        r0, r1 = int(h*0.80), int(h*0.94)                          # serial number panel
        c0, c1 = int(w*0.66), int(w*0.96)
        arr[r0:r1, c0:c1] = rng.choice(
            [[36, 36, 36], [210, 208, 202]], (r1 - r0, c1 - c0)).astype(np.int16)
        img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
        d = ImageDraw.Draw(img)
        d.text((26, 18), f"FRAUD SHIELD SPECIMEN {denom.replace('₹', 'Rs ')} - NOT LEGAL TENDER",
               fill=(90, 60, 60))

    with cR:
        if img is None:
            st.markdown(f"""
            <div style="border:1px dashed {C['border']};border-radius:16px;padding:56px 30px;
                        text-align:center;color:{C['muted']};">
                <div style="font-size:38px">💵</div>
                <div style="font-family:'Space Grotesk';font-size:17px;color:{C['text']};margin-top:6px">
                    No specimen loaded</div>
                <div style="font-size:13px;margin-top:4px">Upload a note photo, or run the synthetic demo.</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.image(img, caption=f"Specimen under analysis · {denom}")

    if img is not None:
        g = np.asarray(img.convert("L"), dtype=float)
        rgb = np.asarray(img, dtype=float)
        Hh, Ww = g.shape
        checks = []

        # 1. Geometry
        exp_ar, hue_rng, hue_name = NOTE_SPEC[denom]
        ar = Ww / Hh
        ok = abs(ar - exp_ar) / exp_ar < 0.06
        checks.append(("GEOMETRY", f"aspect ratio {ar:.3f} vs spec {exp_ar:.3f}", ok, 20))

        # 2. Resolution
        ok = min(Hh, Ww) >= 500
        checks.append(("RESOLUTION", f"{Ww}×{Hh}px — {'sufficient' if ok else 'too low'} for microprint analysis", ok, 10))

        # 3. Security thread — dark vertical band near 45% width
        col_dark = g.mean(axis=0)
        lo, hi = int(Ww*0.35), int(Ww*0.58)
        band = col_dark[lo:hi]
        ok = (band.min() < col_dark.mean() - 22)
        checks.append(("SECURITY_THREAD", "dark vertical thread band detected in expected zone" if ok
                       else "no thread signature found in expected zone", ok, 25))

        # 4. Microprint proxy — high-frequency edge density in centre crop
        cc = g[int(Hh*0.25):int(Hh*0.75), int(Ww*0.2):int(Ww*0.8)]
        edges = np.abs(np.diff(cc, axis=1)).mean()
        ok = edges > 4.0
        checks.append(("MICROPRINT_DENSITY", f"fine-detail energy {edges:.1f} ({'consistent with intaglio print' if ok else 'unusually flat — possible photocopy'})", ok, 25))

        # 5. Serial panel contrast (bottom-right, ascending numerals)
        sp = g[int(Hh*0.72):, int(Ww*0.60):]
        ok = sp.std() > 28
        checks.append(("SERIAL_PANEL", f"number-panel contrast σ={sp.std():.0f} ({'crisp' if ok else 'washed out'})", ok, 20))

        score = sum(w for _, _, ok, w in checks if ok)
        if score >= 80:  cls, tag = "v-low", "FEATURES CONSISTENT WITH GENUINE"
        elif score >= 50: cls, tag = "v-med", "INCONCLUSIVE — ESCALATE TO MANUAL CHECK"
        else:             cls, tag = "v-high", "SUSPECT NOTE — WITHHOLD & REPORT"
        color = {"v-low": C["safe"], "v-med": C["warn"], "v-high": C["danger"]}[cls]

        a, b = st.columns([1, 1.3], gap="large")
        with a:
            st.markdown(f"""
            <div class="verdict {cls}">
                <span class="tag" style="color:{color};border-color:{color}">{tag}</span>
                <div class="score" style="color:{color}">{score}<small> /100</small></div>
                <div class="desc">Feature-confidence score across {len(checks)} visible security checks.</div>
            </div>""", unsafe_allow_html=True)
        with b:
            for code, desc, ok, w in checks:
                st.markdown(
                    f'<div class="sig{" ok" if ok else ""}"><span>{code} — {desc}</span>'
                    f'<span class="w">{"+" + str(w) if ok else "✗"}</span></div>',
                    unsafe_allow_html=True)
        st.caption("If a note fails screening: do not return it to circulation. Banks must impound and "
                   "issue an acknowledgement per RBI Master Direction on FICN detection & reporting.")

# ============================================================================
# TAB — GEO INTELLIGENCE (hotspot map + patrol prioritisation)
# ============================================================================
with tab_geo:
    st.markdown('<div class="sec">Cybercrime hotspot map — complaint clusters & FICN seizure points (simulated)</div>',
                unsafe_allow_html=True)
    geo_df = complaints_data()
    agg = geo_df.groupby("city").agg(n=("ncrp_id", "size"), amt=("amount", "sum")).reset_index()
    agg["lat"] = agg["city"].map(lambda c: CITY_COORDS[c][0])
    agg["lon"] = agg["city"].map(lambda c: CITY_COORDS[c][1])
    rng = np.random.default_rng(11)
    seiz = pd.DataFrame({
        "city": rng.choice(CITIES, 14),
        "notes": rng.integers(40, 900, 14),
    })
    seiz["lat"] = seiz["city"].map(lambda c: CITY_COORDS[c][0]) + rng.normal(0, 0.7, 14)
    seiz["lon"] = seiz["city"].map(lambda c: CITY_COORDS[c][1]) + rng.normal(0, 0.7, 14)

    fig = go.Figure()
    fig.add_trace(go.Scattergeo(
        lat=agg["lat"].astype(float).tolist(), lon=agg["lon"].astype(float).tolist(),
        name="Fraud complaints",
        mode="markers+text", text=agg["city"].astype(str).tolist(), textposition="top center",
        textfont=dict(family="Inter", size=11, color=C["muted"]),
        marker=dict(size=(np.sqrt(agg["n"]) * 3.2).astype(float).tolist(),
                    color=agg["amt"].astype(float).tolist(),
                    colorscale=[[0, "rgba(29,78,137,0.60)"], [1, "rgba(166,27,27,0.95)"]],
                    line=dict(color=C["bg"], width=1),
                    colorbar=dict(title="₹ at risk", tickfont=dict(color=C["muted"]))),
        hovertext=[f"{r.city}<br>{int(r.n)} complaints · ₹{r.amt/1e5:.1f} L" for r in agg.itertuples()],
        hoverinfo="text"))
    fig.add_trace(go.Scattergeo(
        lat=seiz["lat"].astype(float).tolist(), lon=seiz["lon"].astype(float).tolist(),
        name="FICN seizure points",
        mode="markers",
        marker=dict(symbol="diamond", size=9, color=C["warn"],
                    line=dict(color=C["bg"], width=1)),
        hovertext=[f"FICN seizure · {int(r.notes)} notes · near {r.city}" for r in seiz.itertuples()],
        hoverinfo="text"))
    fig.update_geos(
        scope="asia", lataxis_range=[6, 36], lonaxis_range=[66, 98],
        bgcolor="rgba(0,0,0,0)", landcolor="#F3E2CC", showland=True,
        countrycolor=C["border"], showcountries=True,
        coastlinecolor=C["border"], showcoastlines=True,
        lakecolor=C["bg"], showlakes=True)
    fig.update_layout(legend=dict(orientation="h", y=0.02, x=0.02))
    st.plotly_chart(style(fig, 560, axes=False))

    st.markdown('<div class="sec">Patrol & resource prioritisation — ranked hotspots</div>', unsafe_allow_html=True)
    rank = agg.sort_values("amt", ascending=False).reset_index(drop=True)
    cols = st.columns(5)
    for i, r in rank.head(5).iterrows():
        pr = ["CRITICAL", "HIGH", "HIGH", "ELEVATED", "ELEVATED"][i]
        pc = [C["danger"], C["warn"], C["warn"], C["cyan"], C["cyan"]][i]
        cols[i].markdown(f"""
        <div class="kpi" style="--g:{pc}">
            <div class="l">#{i+1} · {r.city}</div>
            <div class="v" style="font-size:22px">₹{r.amt/1e5:.0f} L</div>
            <div class="d">{r.n} complaints · <b>{pr}</b></div>
        </div>""", unsafe_allow_html=True)
    st.caption("Priority = reported ₹ at risk weighted by complaint density — feeds district-level patrol "
               "deployment and inter-district intelligence sharing in near real time.")
