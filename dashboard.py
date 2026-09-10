import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import time

# Production configuration
API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Industrial Energy AI | SCADA Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom SCADA-style CSS
st.markdown("""
    <style>
    .main { background-color: #0E1117; }
    .stMetric {
        background-color: #1E222D;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #2E3440;
    }
    .stButton>button {
        width: 100%;
        background-color: #00D4FF;
        color: #000;
        font-weight: bold;
        border-radius: 6px;
    }
    </style>
""", unsafe_allow_html=True)

# Session State Initialization
if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=["timestamp", "power_kw", "voltage", "current_amps", "temperature_c", "anomaly_detected"])

# Header Bar
st.title("⚡ Industrial Smart Energy Operations Platform")
st.caption("Real-Time Telemetry Data | Isolation Forest Anomaly Detection | SciPy Load Optimization")

st.divider()

# Sidebar Control Console
with st.sidebar:
    st.header("⚙️ Plant Control Panel")
    st.status("System Status: ONLINE", state="complete")
    
    st.subheader("1. Stream Controls")
    auto_refresh = st.toggle("Live Telemetry Stream", value=False)
    refresh_rate = st.slider("Refresh Interval (s)", 1, 5, 2)
    
    st.subheader("2. Peak Shaving Targets")
    target_power = st.number_input("Max Grid Allowance (kW)", min_value=50.0, max_value=300.0, value=120.0, step=10.0)
    
    if st.button("Trigger Optimization Run"):
        latest_kw = st.session_state.history["power_kw"].iloc[-1] if not st.session_state.history.empty else 100.0
        res = requests.post(f"{API_URL}/api/v1/optimize", json={"target_power_kw": target_power, "current_power_kw": latest_kw})
        if res.status_code == 200:
            st.session_state.opt_result = res.json().get("allocations", {})
            st.success("Load schedule updated!")

# Data Fetching Logic
def fetch_telemetry():
    try:
        res = requests.get(f"{API_URL}/api/v1/telemetry", timeout=3)
        if res.status_code == 200:
            data = res.json()
            new_row = pd.DataFrame([data])
            st.session_state.history = pd.concat([st.session_state.history, new_row]).tail(30).reset_index(drop=True)
            return data
    except Exception:
        st.error("Backend Connection Offline")
    return None

current_data = fetch_telemetry() if auto_refresh or st.button("Fetch Single Data Frame") else (st.session_state.history.iloc[-1].to_dict() if not st.session_state.history.empty else None)

# Main Dashboard View
if current_data:
    # 1. KPI Cards Row
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Active Load (kW)", f"{current_data.get('power_kw', 0)} kW", delta=f"{round(current_data.get('power_kw', 0) - target_power, 2)} kW vs Target")
    col2.metric("Bus Voltage", f"{current_data.get('voltage', 0)} V")
    col3.metric("Motor Temp", f"{current_data.get('temperature_c', 0)} °C")
    
    anomaly = current_data.get("anomaly_detected", False)
    col4.metric("Anomaly Status", "CRITICAL ALERT" if anomaly else "NORMAL", delta="Flagged" if anomaly else "Clear", delta_color="inverse" if anomaly else "normal")

    st.divider()

    # 2. Charts Row
    chart_col1, chart_col2 = st.columns([2, 1])

    with chart_col1:
        st.subheader("📈 Live Demand Curve vs. Target Threshold")
        if not st.session_state.history.empty:
            fig = px.line(st.session_state.history, x="timestamp", y="power_kw", title="Power Demand (kW)", markers=True, template="plotly_dark")
            fig.add_hline(y=target_power, line_dash="dash", line_color="red", annotation_text="Peak Threshold")
            fig.update_traces(line_color="#00D4FF", line_width=3)
            st.plotly_chart(fig, use_container_width=True)

    with chart_col2:
        st.subheader("📊 Optimised System Load Distribution")
        if "opt_result" in st.session_state:
            opt = st.session_state.opt_result
            alloc_df = pd.DataFrame({
                "System": ["HVAC", "Machinery", "Auxiliary"],
                "Allocation (kW)": [opt.get("hvac_kw", 0), opt.get("machinery_kw", 0), opt.get("auxiliary_kw", 0)]
            })
            fig_pie = px.pie(alloc_df, names="System", values="Allocation (kW)", hole=0.4, template="plotly_dark", color_discrete_sequence=px.colors.sequential.Cyan)
            st.plotly_chart(fig_pie, use_container_width=True)
            st.caption(f"Est. Cost: **${opt.get('estimated_cost_per_hr', 0)}/hr**")
        else:
            st.info("Run optimization from the sidebar to visualize SciPy load distribution.")

# Auto Loop for Live Stream
if auto_refresh:
    time.sleep(refresh_rate)
    st.rerun()
