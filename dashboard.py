import streamlit as st
import time
import random

# Page Configuration
st.set_page_config(page_title="Router DNS Defense", layout="wide")

st.title("🛡️ Secure Router Dashboard: DNS Defense Module")
st.markdown("Monitor network request filtering and cache resilience under DDoS attacks.")

# --- SIDEBAR (Controls & Triggers) ---
with st.sidebar:
    st.header("⚙️ Router Configuration")
    algo = st.radio("Active Eviction Policy:", ["Standard LRU", "Proposed AHPR"])
    cache_size = st.slider("DNS Cache Capacity", 50, 500, 100)
    
    st.divider()
    
    st.header("🚨 Threat Simulation")
    # THE ATTACK TRIGGER
    attack_btn = st.button("💥 TRIGGER DDoS ATTACK", type="primary")

# --- MAIN DASHBOARD AREA ---
col1, col2, col3 = st.columns(3)

# Placeholder metrics (These would update dynamically in your full loop)
with col1:
    st.metric(label="Current Cache Hit Rate", value="85%", delta="Normal")
with col2:
    st.metric(label="Network Status", value="UNDER ATTACK" if attack_btn else "SECURE")
with col3:
    st.metric(label="Filtered Attack Queries", value="1,402" if attack_btn else "0")

# --- RESILIENCE GRAPH ---
st.subheader("📊 Network Resilience (Hit Rate vs Time)")
# You would feed your simulator's pandas dataframe here instead of a line_chart
chart_data = [85, 86, 84, 85, 12, 5, 2] if (attack_btn and algo == "Standard LRU") else [85, 86, 84, 85, 78, 82, 85]
st.line_chart(chart_data)

# --- LIVE TRAFFIC LOG ---
st.subheader("📡 Live Network Request Filtering")
log_box = st.empty()
if attack_btn:
    log_box.code("""
[WARN] Traffic spike detected.
[EVICT] Dropping low-frequency record: xq291.botnet.info
[EVICT] Dropping low-frequency record: zza99.botnet.info
[CACHE HIT] Legitimate traffic preserved: netflix.com
    """, language="bash")
else:
    log_box.code("""
[CACHE HIT] youtube.com
[CACHE HIT] google.com
[RESOLVED] github.com
    """, language="bash")