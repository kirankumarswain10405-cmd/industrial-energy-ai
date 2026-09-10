import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="AI Industrial Energy Optimization Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Vector SVGs for UI Rendering
SVG_BOLT = """<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#00E5FF" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>"""
SVG_GEAR = """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#8B949E" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>"""
SVG_PULSE = """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#00E5FF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>"""

# Custom CSS Styling
st.markdown("""
    <style>
    .stApp { background-color: #0B0E14; }
    
    .header-container {
        display: flex;
        align-items: center;
        gap: 12px;
        padding-bottom: 8px;
    }
    
    .scada-metric-box {
        background-color: #12161F;
        border: 1px solid #1F2837;
        border-radius: 6px;
        padding: 16px;
    }
    .metric-title {
        color: #8B949E;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .metric-value-text {
        color: #F0F6FC;
        font-size: 1.8rem;
        font-weight: 700;
        font-family: 'JetBrains Mono', 'Courier New', monospace;
        margin-top: 4px;
    }
    
    .status-pill-normal {
        display: inline-block;
        background-color: rgba(0, 229, 255, 0.1);
        color: #00E5FF;
        border: 1px solid rgba(0, 229, 255, 0.3);
        padding: 4px 12px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    .status-pill-critical {
        display: inline-block;
        background-color: rgba(255, 46, 147, 0.15);
        color: #FF2E93;
        border: 1px solid rgba(255, 46, 147, 0.4);
        padding: 4px 12px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    </style>
""", unsafe_allow_html=True)

# Session State Initialization
if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=["timestamp", "power_kw", "voltage", "current_amps", "temperature_c", "anomaly_detected"])

# Web Application Header
head_col1, head_col2 = st.columns([3, 1])
with head_col1:
    st.markdown(f'<div class="header-container">{SVG_BOLT} <h1 style="margin:0; font-size:1.8rem; color:#F0F6FC;">AI Industrial Energy Optimization Platform</h1></div>', unsafe_allow_html=True)
    st.caption("Telemetry Node: **SUBSTATION-01** | Analytics Engine: **FastAPI + SciPy LP + IsolationForest**")

with head_col2:
    st.markdown('<div style="text-align: right; margin-top:15px;"><span class="status-pill-normal">STREAM ACTIVE</span></div>', unsafe_allow_html=True)

st.divider()

# Sidebar Setup
with st.sidebar:
    st.markdown(f'<div style="display:flex; align-items:center; gap:8px;">{SVG_GEAR} <h3 style="margin:0; font-size:1.1rem; color:#F0F6FC;">Control Console</h3></div>', unsafe_allow_html=True)
    st.markdown(" ")
    auto_refresh = st.toggle("Live Telemetry Ingestion", value=True)
    refresh_rate = st.slider("Stream Interval (seconds)", 1, 5, 2)
    
    st.divider()
    st.markdown("### Grid Threshold Settings")
    target_power = st.number_input("Max Grid Capacity (kW)", min_value=50.0, max_value=300.0, value=120.0, step=10.0)
    
    if st.button("Execute SciPy Load Optimization", use_container_width=True):
        try:
            latest_kw = float(st.session_state.history["power_kw"].iloc[-1]) if not st.session_state.history.empty else 100.0
            res = requests.post(f"{API_URL}/api/v1/optimize", json={"target_power_kw": target_power, "current_power_kw": latest_kw}, timeout=3)
            if res.status_code == 200:
                st.session_state.opt_result = res.json().get("allocations", {})
                st.toast("SciPy Linear Optimization updated system schedule", icon="⚡")
        except Exception as e:
            st.error(f"Optimization link failed: {e}")

# Data Handling
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

current_data = fetch_telemetry() if auto_refresh or st.button("Manual Data Fetch") else (
    st.session_state.history.iloc[-1].to_dict() if not st.session_state.history.empty else None
)

# Dashboard Display
if current_data:
    p_kw = current_data.get('power_kw', 0.0)
    anomaly = current_data.get("anomaly_detected", False)

    # Metric Banner
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f'<div class="scada-metric-box"><div class="metric-title">Active Power Load</div><div class="metric-value-text">{p_kw:.1f} <span style="font-size:1rem; color:#8B949E;">kW</span></div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="scada-metric-box"><div class="metric-title">Grid Bus Voltage</div><div class="metric-value-text">{current_data.get("voltage", 0.0):.1f} <span style="font-size:1rem; color:#8B949E;">V</span></div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="scada-metric-box"><div class="metric-title">Motor Temperature</div><div class="metric-value-text">{current_data.get("temperature_c", 0.0):.1f} <span style="font-size:1rem; color:#8B949E;">°C</span></div></div>', unsafe_allow_html=True)
    with m4:
        status_html = '<span class="status-pill-critical">CRITICAL ANOMALY</span>' if anomaly else '<span class="status-pill-normal">NOMINAL OPERATION</span>'
        st.markdown(f'<div class="scada-metric-box"><div class="metric-title">ML Anomaly Status</div><div style="margin-top:10px;">{status_html}</div></div>', unsafe_allow_html=True)

    st.divider()

    # Visual Layout
    col_chart, col_gauge = st.columns([2, 1])

    with col_chart:
        st.markdown(f'<div style="display:flex; align-items:center; gap:8px;">{SVG_PULSE} <h4 style="margin:0; color:#F0F6FC;">Power Telemetry Stream vs Threshold</h4></div>', unsafe_allow_html=True)
        if not st.session_state.history.empty:
            fig = px.line(st.session_state.history, x="timestamp", y="power_kw", markers=True)
            fig.add_hline(y=target_power, line_dash="dash", line_color="#FF2E93", annotation_text="Max Allowed Capacity")
            fig.update_traces(line_color="#00E5FF", line_width=2.5)
            fig.update_layout(
                height=340, 
                margin=dict(l=10, r=10, t=20, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#8B949E"),
                xaxis=dict(showgrid=True, gridcolor="#1F2837"),
                yaxis=dict(showgrid=True, gridcolor="#1F2837")
            )
            st.plotly_chart(fig, use_container_width=True)

    with col_gauge:
        st.markdown('<h4 style="margin:0; color:#F0F6FC;">Active Peak Capacity</h4>', unsafe_allow_html=True)
        gauge_fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=p_kw,
            gauge={
                'axis': {'range': [0, 300], 'tickcolor': "#8B949E"},
                'bar': {'color': "#FF2E93" if p_kw > target_power else "#00E5FF"},
                'bgcolor': "#12161F",
                'bordercolor': "#1F2837",
                'steps': [
                    {'range': [0, target_power], 'color': "#12161F"},
                    {'range': [target_power, 300], 'color': "#2E1524"}
                ],
                'threshold': {'line': {'color': "#FF2E93", 'width': 3}, 'thickness': 0.8, 'value': target_power}
            }
        ))
        gauge_fig.update_layout(
            height=310, 
            margin=dict(l=20, r=20, t=20, b=10), 
            paper_bgcolor="rgba(0,0,0,0)", 
            font=dict(color="#F0F6FC")
        )
        st.plotly_chart(gauge_fig, use_container_width=True)

    # SciPy Linear Optimization Allocations
    st.divider()
    st.markdown('<h4 style="margin:0; color:#F0F6FC;">SciPy LP System Load Distribution</h4>', unsafe_allow_html=True)
    st.markdown(" ")
    if "opt_result" in st.session_state:
        opt = st.session_state.opt_result
        o1, o2, o3, o4 = st.columns(4)
        o1.metric("HVAC System Load", f"{opt.get('hvac_kw', 0)} kW")
        o2.metric("Machinery Load", f"{opt.get('machinery_kw', 0)} kW")
        o3.metric("Auxiliary Load", f"{opt.get('auxiliary_kw', 0)} kW")
        o4.metric("Est. Cost Rate", f"${opt.get('estimated_cost_per_hr', 0)} / hr")
    else:
        st.info("Execute SciPy Load Optimization from the control sidebar to render active load allocation.")
else:
    st.warning("Awaiting initial telemetry stream frame from FastAPI service...")

if auto_refresh:
    time.sleep(refresh_rate)
    st.rerun()
