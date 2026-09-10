import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="AI Industrial Energy Optimization Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enterprise Dark SCADA Theme
st.markdown("""
    <style>
    .main { background-color: #0E1117; }
    div[data-testid="stMetricValue"] { font-family: 'Courier New', monospace; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# Session State Initializer
if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=["timestamp", "power_kw", "voltage", "current_amps", "temperature_c", "anomaly_detected"])

# Header Console
st.markdown("## ⚡ AI Industrial Energy Optimization Platform")
st.caption("Real-Time Telemetry Streaming | Isolation Forest Anomaly Detection | SciPy Load Optimization")
st.divider()

# Sidebar - Operational Control Unit
with st.sidebar:
    st.markdown("### 🎛️ Control Console")
    auto_refresh = st.toggle("Enable Live Telemetry Stream", value=True)
    refresh_rate = st.slider("Polling Frequency (sec)", 1, 5, 2)
    
    st.divider()
    st.markdown("### 🎯 Peak-Shaving Parameters")
    target_power = st.number_input("Peak Threshold Limit (kW)", min_value=50.0, max_value=300.0, value=120.0, step=10.0)
    
    if st.button("Run Load Optimization"):
        try:
            latest_kw = float(st.session_state.history["power_kw"].iloc[-1]) if not st.session_state.history.empty else 100.0
            res = requests.post(f"{API_URL}/api/v1/optimize", json={"target_power_kw": target_power, "current_power_kw": latest_kw}, timeout=3)
            if res.status_code == 200:
                st.session_state.opt_result = res.json().get("allocations", {})
                st.toast("SciPy Linear Optimizer Execution Complete", icon="✅")
        except Exception as e:
            st.error(f"Optimization link failed: {e}")

# Data Fetcher
def fetch_telemetry():
    try:
        res = requests.get(f"{API_URL}/api/v1/telemetry", timeout=3)
        if res.status_code == 200:
            data = res.json()
            new_row = pd.DataFrame([data])
            st.session_state.history = pd.concat([st.session_state.history, new_row]).tail(30).reset_index(drop=True)
            return data
    except Exception:
        pass
    return None

current_data = fetch_telemetry() if auto_refresh or st.button("Single Refresh") else (
    st.session_state.history.iloc[-1].to_dict() if not st.session_state.history.empty else None
)

if current_data:
    p_kw = current_data.get('power_kw', 0.0)
    anomaly = current_data.get("anomaly_detected", False)

    # Top KPI Banner
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Current Active Demand", f"{p_kw:.1f} kW", delta=f"{p_kw - target_power:.1f} kW Delta")
    kpi2.metric("Grid Voltage", f"{current_data.get('voltage', 0.0):.1f} V")
    kpi3.metric("Motor Temp", f"{current_data.get('temperature_c', 0.0):.1f} °C")
    
    status_label = "CRITICAL ANOMALY" if anomaly else "NOMINAL OPERATION"
    kpi4.metric("System Health", status_label, delta="Action Req" if anomaly else "Clear", delta_color="inverse" if anomaly else "normal")

    st.divider()

    # Visual Analytics Row
    col_chart, col_gauge = st.columns([2, 1])

    with col_chart:
        st.markdown("#### 📉 Real-Time Power Telemetry vs Operational Threshold")
        if not st.session_state.history.empty:
            fig = px.line(st.session_state.history, x="timestamp", y="power_kw", markers=True, template="plotly_dark")
            fig.add_hline(y=target_power, line_dash="dash", line_color="#FF4B4B", annotation_text="Max Allowed Grid Peak")
            fig.update_traces(line_color="#00D4FF", line_width=2.5)
            fig.update_layout(height=350, margin=dict(l=10, r=10, t=20, b=10), paper_bgcolor="#0E1117", plot_bgcolor="#0E1117")
            st.plotly_chart(fig, use_container_width=True)

    with col_gauge:
        st.markdown("#### ⚡ Peak Load Capacity Gauge")
        gauge_fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=p_kw,
            gauge={
                'axis': {'range': [0, 300]},
                'bar': {'color': "#FF4B4B" if p_kw > target_power else "#00D4FF"},
                'steps': [
                    {'range': [0, target_power], 'color': "#1E2230"},
                    {'range': [target_power, 300], 'color': "#3A1E2B"}
                ],
                'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': target_power}
            }
        ))
        gauge_fig.update_layout(height=320, margin=dict(l=20, r=20, t=30, b=10), paper_bgcolor="#0E1117", font={"color": "white"})
        st.plotly_chart(gauge_fig, use_container_width=True)

    # Optimization Output Section
    st.divider()
    st.markdown("#### ⚙️ SciPy Optimal Load Allocation")
    
    if "opt_result" in st.session_state:
        opt = st.session_state.opt_result
        o1, o2, o3, o4 = st.columns(4)
        o1.metric("HVAC Allocated", f"{opt.get('hvac_kw', 0)} kW")
        o2.metric("Machinery Allocated", f"{opt.get('machinery_kw', 0)} kW")
        o3.metric("Auxiliary Allocated", f"{opt.get('auxiliary_kw', 0)} kW")
        o4.metric("Estimated Cost", f"${opt.get('estimated_cost_per_hr', 0)} / hr")
    else:
        st.info("Click 'Run Load Optimization' in the sidebar to compute linear load distributions.")
else:
    st.warning("Awaiting telemetry frames from FastAPI service...")

if auto_refresh:
    time.sleep(refresh_rate)
    st.rerun()
