import numpy as np
import networkx as nx
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Test 4", layout="wide")
st.title("Test 4 — chart construction only, no CSS, no widgets")

C = {
    "bg": "#FBF0E4", "border": "#E8D5BF", "text": "#211A12", "muted": "#7A6A58",
    "blue": "#1D4E89", "danger": "#A61B1B", "warn": "#B25E00", "violet": "#6D4C9F",
}

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

rng = np.random.default_rng(42)
G = nx.Graph()
for r in range(1, 5):
    scammers = [f"+91-9{rng.integers(10**8, 10**9)}" for _ in range(rng.integers(2, 5))]
    mules = [f"AC{rng.integers(10**9, 10**10)}" for _ in range(rng.integers(2, 4))]
    devices = [f"DEV-{rng.integers(1000, 9999)}" for _ in range(rng.integers(1, 3))]
    victims = [f"V-{r}{i:02d}" for i in range(rng.integers(3, 10))]
    for v in victims:
        s = scammers[rng.integers(0, len(scammers))]
        G.add_node(v, kind="victim", ring=r); G.add_node(s, kind="scammer", ring=r)
        G.add_edge(v, s)
    for s in scammers:
        G.add_node(s, kind="scammer", ring=r)
        for m in rng.choice(mules, rng.integers(1, len(mules) + 1), replace=False):
            G.add_node(m, kind="mule", ring=r); G.add_edge(s, m)
        for d in rng.choice(devices, rng.integers(1, len(devices) + 1), replace=False):
            G.add_node(d, kind="device", ring=r); G.add_edge(s, d)

pos_raw = nx.spring_layout(G, k=0.45, seed=7, iterations=80)
pos = {n: (float(xy[0]), float(xy[1])) for n, xy in pos_raw.items()}
KIND = {"victim": dict(color=C["blue"], size=9, name="Victim"),
        "scammer": dict(color=C["danger"], size=15, name="Scammer number"),
        "mule": dict(color=C["warn"], size=13, name="Mule account"),
        "device": dict(color=C["violet"], size=11, name="Device fingerprint")}

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
        marker=dict(color=s["color"], size=s["size"], line=dict(color=C["bg"], width=1.5), opacity=0.95),
        text=[f"{n}<br>Ring {G.nodes[n]['ring']} - degree {int(G.degree(n))}" for n in ns],
        hoverinfo="text"))
fig.update_layout(showlegend=True, xaxis=dict(visible=False), yaxis=dict(visible=False))
st.plotly_chart(style(fig, 520, axes=False))

st.write("If the graph above rendered clean with no 'undefined', the chart-construction code itself is fine in isolation.")
