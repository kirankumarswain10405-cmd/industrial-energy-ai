import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
import hashlib

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="AI Industrial Energy Optimization Platform",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Blue Vector SVGs
SVG_BOLT = """<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#00A3FF" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>"""
SVG_GEAR = """<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#00A3FF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>"""
SVG_LOCK = """<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#00A3FF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>"""
SVG_PULSE = """<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#00A3FF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>"""

# Precise Black, Electric Blue & Crisp White CSS Palette
st.markdown("""
    <style>
    /* Dark Background Override */
    .stApp, [data-testid="stSidebar"], body {
        background-color: #06090E !important;
    }
    
    /* Global Pure White Base Text */
    p, label, span, h1, h2, h3, h4, h5, h6, div {
        color: #FFFFFF !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Subtext Neutral High-Contrast Styling */
    .subtext-gray {
        color: #A0AEC0 !important;
    }

    /* Primary Accent Blue Class */
    .text-blue-accent {
        color: #00A3FF !important;
        font-weight: 700;
    }

    /* Form & Input Field Visibility */
    input, stTextInput>div>div>input {
        color: #FFFFFF !important;
        background-color: #0F172A !important;
        border: 1px solid #1E293B !important;
        border-radius: 6px !important;
    }
    input:focus {
        border-color: #00A3FF !important;
        box-shadow: 0 0 8px rgba(0, 163, 255, 0.4) !important;
    }

    /* Native Metric Cards Override */
    [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-weight: 800 !important;
        font-family: 'Courier New', monospace !important;
    }
    [data-testid="stMetricLabel"] {
        color: #00A3FF !important;
        font-size: 0.85rem !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* SCADA Custom Cards */
    .scada-card {
        background: linear-gradient(180deg, #0F172A 0%, #0B1120 100%);
        border: 1px solid #1E293B;
        border-left: 4px solid #00A3FF;
        border-radius: 8px;
        padding: 18px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
    }
    .metric-title {
        color: #A0AEC0 !important;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .metric-value {
        color: #FFFFFF !important;
        font-size: 2rem;
        font-weight: 800;
        font-family: 'JetBrains Mono', 'Courier New', monospace;
        margin-top: 4px;
    }

    /* Status Indicators */
    .status-pill-normal {
        background-color: rgba(0, 163, 255, 0.12);
        color: #00A3FF !important;
        border: 1px solid #00A3FF;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    .status-pill-critical {
        background-color: rgba(255, 68, 68, 0.15);
        color: #FF4444 !important;
        border: 1px solid #FF4444;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.5px;
    }

    /* Blue Accent Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #0052D4 0%, #00A3FF 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        font-weight: 700 !important;
        border-radius: 6px !important;
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        box-shadow: 0 0 12px rgba(0, 163, 255, 0.6) !important;
        transform: translateY(-1px);
    }
    </style>
""", unsafe_allow_html=True)

def make_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

USER_DATABASE = {
    "admin": make_hash("admin123"),
    "operator": make_hash("scada2026")
}

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=["timestamp", "power_kw", "voltage", "current_amps", "temperature_c", "anomaly_detected"])

# -----------------------------------------------------------------------------
# 1. LOGIN INTERFACE (Isolated Screen)
# -----------------------------------------------------------------------------
if not st.session_state.authenticated:
    _, center_col, _ = st.columns([1, 1.2, 1])
    with center_col:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown(f'<div style="text-align:center;">{SVG_LOCK}</div>', unsafe_allow_html=True)
        st.markdown('<h2 style="text-align:center; color:#FFFFFF !important; margin-bottom:2px; font-weight:800;">SYSTEM AUTHORIZATION</h2>', unsafe_allow_html=True)
        st.markdown('<p style="text-align:center; color:#A0AEC0 !important; font-size:0.9rem;">AI Industrial Energy Optimization Platform</p>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Operator ID")
            password = st.text_input("Access Key", type="password")
            submit = st.form_submit_button("AUTHENTICATE ACCESS", use_container_width=True)
            
            if submit:
                hashed_pw = make_hash(password)
                if username in USER_DATABASE and USER_DATABASE[username] == hashed_pw:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Invalid Operator ID or Access Key.")
                    
        st.markdown('<p style="text-align:center; color:#A0AEC0 !important; font-size:0.85rem;">Default Login: <span class="text-blue-accent">admin</span> / <span class="text-blue-accent">admin123</span></p>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. MAIN DASHBOARD (Authenticated View)
# -----------------------------------------------------------------------------
else:
    head_col1, head_col2 = st.columns([3, 1])
    with head_col1:
        st.markdown(f'<div style="display:flex; align-items:center; gap:12px;">{SVG_BOLT} <h1 style="margin:0; font-size:1.8rem; font-weight:800; color:#FFFFFF !important;">AI INDUSTRIAL ENERGY OPTIMIZATION</h1></div>', unsafe_allow_html=True)
        st.markdown(f'<p style="color:#A0AEC0 !important; margin-top:4px;">Authenticated Operator: <span class="text-blue-accent">{st.session_state.username.upper()}</span> | Substation: <b style="color:#FFFFFF !important;">01-ALPHA</b></p>', unsafe_allow_html=True)

    with head_col2:
        st.markdown('<div style="text-align: right; margin-top:10px;"><span class="status-pill-normal">SYSTEM ONLINE</span></div>', unsafe_allow_html=True)

    st.divider()

    # Sidebar Controls
    with st.sidebar:
        st.markdown(f'<div style="display:flex; align-items:center; gap:8px;">{SVG_GEAR} <h3 style="margin:0; font-size:1.1rem; color:#FFFFFF !important; font-weight:700;">CONTROL CONSOLE</h3></div>', unsafe_allow_html=True)
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
                
        st.divider()
        if st.button("Sign Out Session", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()

    # Telemetry Fetch Function
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

    if current_data:
        p_kw = current_data.get('power_kw', 0.0)
        anomaly = current_data.get("anomaly_detected", False)

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f'<div class="scada-card"><div class="metric-title">Active Power Load</div><div class="metric-value">{p_kw:.1f} <span style="font-size:1rem; color:#00A3FF !important;">kW</span></div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="scada-card"><div class="metric-title">Grid Bus Voltage</div><div class="metric-value">{current_data.get("voltage", 0.0):.1f} <span style="font-size:1rem; color:#00A3FF !important;">V</span></div></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="scada-card"><div class="metric-title">Motor Temperature</div><div class="metric-value">{current_data.get("temperature_c", 0.0):.1f} <span style="font-size:1rem; color:#00A3FF !important;">°C</span></div></div>', unsafe_allow_html=True)
        with m4:
            status_html = '<span class="status-pill-critical">CRITICAL ANOMALY</span>' if anomaly else '<span class="status-pill-normal">NOMINAL OPERATION</span>'
            st.markdown(f'<div class="scada-card"><div class="metric-title">ML Anomaly Status</div><div style="margin-top:10px;">{status_html}</div></div>', unsafe_allow_html=True)

        st.divider()

        col_chart, col_gauge = st.columns([2, 1])

        # High-Contrast Blue & White Line Graph
        with col_chart:
            st.markdown(f'<div style="display:flex; align-items:center; gap:8px;">{SVG_PULSE} <h4 style="margin:0; font-weight:700;">Power Telemetry Stream vs Capacity Threshold</h4></div>', unsafe_allow_html=True)
            if not st.session_state.history.empty:
                fig = px.line(st.session_state.history, x="timestamp", y="power_kw", markers=True)
                fig.add_hline(y=target_power, line_dash="dash", line_color="#FF4444", annotation_text="Max Capacity", annotation_font_color="#FF4444")
                fig.update_traces(line_color="#00A3FF", line_width=3, marker=dict(size=6, color="#00E5FF"))
                fig.update_layout(
                    height=340, 
                    margin=dict(l=10, r=10, t=20, b=10),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#FFFFFF"),
                    xaxis=dict(showgrid=True, gridcolor="#1E293B", tickfont=dict(color="#A0AEC0")),
                    yaxis=dict(showgrid=True, gridcolor="#1E293B", tickfont=dict(color="#A0AEC0"))
                )
                st.plotly_chart(fig, use_container_width=True)

        # High-Contrast Blue & White Gauge Chart
        with col_gauge:
            st.markdown('<h4 style="margin:0; font-weight:700;">Active Peak Capacity</h4>', unsafe_allow_html=True)
            gauge_fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=p_kw,
                gauge={
                    'axis': {'range': [0, 300], 'tickcolor': "#FFFFFF", 'tickfont': {'color': "#A0AEC0"}},
                    'bar': {'color': "#FF4444" if p_kw > target_power else "#00A3FF"},
                    'bgcolor': "#0F172A",
                    'bordercolor': "#1E293B",
                    'steps': [
                        {'range': [0, target_power], 'color': "#0F172A"},
                        {'range': [target_power, 300], 'color': "#2B1118"}
                    ],
                    'threshold': {'line': {'color': "#FF4444", 'width': 3}, 'thickness': 0.8, 'value': target_power}
                }
            ))
            gauge_fig.update_layout(
                height=310, 
                margin=dict(l=20, r=20, t=20, b=10), 
                paper_bgcolor="rgba(0,0,0,0)", 
                font=dict(color="#FFFFFF")
            )
            st.plotly_chart(gauge_fig, use_container_width=True)

        st.divider()
        st.markdown('<h4 style="margin:0; font-weight:700;">SciPy LP System Load Distribution</h4>', unsafe_allow_html=True)
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
