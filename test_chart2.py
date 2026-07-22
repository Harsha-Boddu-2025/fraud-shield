import re
import numpy as np
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Test 2", layout="wide")

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
    title_font=dict(family="Space Grotesk", size=15, color=C["text"]),
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



st.markdown('<div class="sec">Fraud network graph test</div>', unsafe_allow_html=True)
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
        text=[f"{n}<br>Ring {G.nodes[n]['ring']} - degree {int(G.degree(n))}" for n in ns],
        hoverinfo="text"))
fig.update_layout(showlegend=True, xaxis=dict(visible=False), yaxis=dict(visible=False))
st.plotly_chart(style(fig, 520, axes=False))

st.write("If the network graph above rendered with no 'undefined' text, the CSS/structure is fine.")
