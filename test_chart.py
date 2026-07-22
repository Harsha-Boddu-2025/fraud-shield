import streamlit as st
import plotly.graph_objects as go

st.title("Plotly Test")
st.write("If you see a red bar chart below, Plotly works fine on this environment.")

fig = go.Figure(go.Bar(x=["A", "B", "C"], y=[3, 7, 5]))
fig.update_layout(title="Simple Test Chart")
st.plotly_chart(fig)
