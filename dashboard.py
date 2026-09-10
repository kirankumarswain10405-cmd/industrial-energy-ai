import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import time

st.set_page_config(page_title="Industrial Energy AI", layout="wide")
st.title(" AI-Powered Industrial Energy Optimization")

API_URL = "http://127.0.0.1:8000"

st.sidebar.header("Control Panel")
auto_refresh = st.sidebar.checkbox("Start Live Telemetry", value=False)
target_kw = st.sidebar.slider("Target Plant Load (kW)", 50, 250, 120)

if "history" not in st.session_state:
    st.session_state.history = []

col1, col2, col3 = st.columns(3)
metric_ph1 = col1.empty()
metric_ph2 = col2.empty()
metric_ph3 = col3.empty()

chart_ph = st.empty()

def fetch_and_render():
    try:
        response = requests.get(f"{API_URL}/api/v1/telemetry")
        
        # Check if HTTP request returned success code 200
        if response.status_code != 200:
            st.error(f"Backend returned HTTP Status {response.status_code}")
            return

        res = response.json()
        st.session_state.history.append(res)
        if len(st.session_state.history) > 30:
            st.session_state.history.pop(0)

        df = pd.DataFrame(st.session_state.history)

        metric_ph1.metric("Current Power", f"{res['power_kw']} kW")
        metric_ph2.metric("Motor Temp", f"{res['temperature_c']} °C")
        metric_ph3.metric("Anomaly Flag", "ALERT " if res['anomaly_detected'] else "NORMAL", delta_color="inverse")

        fig = px.line(df, x="timestamp", y="power_kw", title="Live Plant Load (kW)", markers=True)
        chart_ph.plotly_chart(fig, use_container_width=True)

    except requests.exceptions.JSONDecodeError:
        st.error("API active, but response payload was not valid JSON.")
    except Exception as e:
        st.error(f"Cannot connect to backend server: {e}")

fetch_and_render()

if auto_refresh:
    time.sleep(2)
    st.rerun()

st.subheader(" AI Load Distribution Optimizer")
if st.button("Run Optimizer"):
    try:
        opt_res = requests.post(f"{API_URL}/api/v1/optimize", json={"target_power_kw": target_kw}).json()
        st.json(opt_res["allocations"])
    except Exception as e:
        st.error(f"Could not connect to optimization service: {e}")
