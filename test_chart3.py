import streamlit as st

st.set_page_config(page_title="Test 3", layout="wide")

C = {"cyan": "#C42B1C", "text": "#211A12", "muted": "#7A6A58", "border": "#E8D5BF"}

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;800&family=Inter:wght@400;500;600&display=swap');
html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
.stApp {{ background: #FBF0E4; }}
h1,h2,h3 {{ font-family:'Playfair Display',serif !important; color:{C['text']}; }}
.sec {{
    font-family:'Inter',sans-serif; font-size:12px; font-weight:700;
    letter-spacing:0.15em; text-transform:uppercase; color:{C['cyan']};
    border-bottom:1px solid {C['border']}; padding-bottom:5px;
    margin:26px 0 10px 0;
}}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="sec">Fraud network graph test</div>', unsafe_allow_html=True)
cA, cB, _ = st.columns([1, 1, 2])
n_rings = cA.slider("Simulated campaigns", 2, 8, 4)
seed = cB.number_input("Random seed", 1, 999, 42)

st.write("END OF TEST — no chart below this line. If you see 'undefined' above this text, the widgets/CSS combo is the cause, not Plotly.")
