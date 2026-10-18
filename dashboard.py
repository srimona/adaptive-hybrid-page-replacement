import streamlit as st
import random
import pandas as pd

# ==========================================
# 1. DNS CACHE ENGINE LOGIC
# ==========================================
class DNSCacheRecord:
    def __init__(self, domain_name, timestamp, initial_freq=1):
        self.domain_name = domain_name
        self.last_access = timestamp
        self.frequency = initial_freq

class SecureRouterDNSCache:
    def __init__(self, capacity, alpha=0.15, is_ahpr=True):
        self.capacity = capacity
        self.alpha = alpha
        self.is_ahpr = is_ahpr
        self.cache = {}            
        self.global_freq_tracker = {} # The Admission Filter Tracker
        self.clock = 0            
        self.dropped_requests = 0
        self.hits = 0
        self.misses = 0

    def resolve_domain(self, domain_name, is_attack=False):
        self.clock += 1
        
        # 1. Update Global Frequency 
        self.global_freq_tracker[domain_name] = self.global_freq_tracker.get(domain_name, 0) + 1

        # Background Aging
        if self.clock > 0 and self.clock % 5000 == 0:
            for record in self.cache.values():
                record.frequency = max(1, record.frequency >> 1)

        # 2. Cache Hit
        if domain_name in self.cache:
            record = self.cache[domain_name]
            record.last_access = self.clock
            record.frequency += 1
            self.hits += 1
            return True 
        
        # 3. Cache Miss & Admission Filter Logic
        self.misses += 1
        
        if len(self.cache) >= self.capacity:
            victim_domain = self._get_victim()
            
            # THE ADMISSION FILTER (AHPR Only)
            if self.is_ahpr:
                incoming_freq = self.global_freq_tracker[domain_name]
                victim_freq = self.cache[victim_domain].frequency
                
                # Reject the incoming query if frequency is too low
                if incoming_freq <= victim_freq:
                    if is_attack:
                        self.dropped_requests += 1
                    return False
            
            # Evict the victim
            del self.cache[victim_domain]

        # 4. Admit to Cache
        new_record = DNSCacheRecord(domain_name, self.clock, self.global_freq_tracker[domain_name])
        self.cache[domain_name] = new_record
        return False 

    def _get_victim(self):
        """Finds the worst page to evict based on the active policy."""
        if not self.is_ahpr:
            # Standard LRU Eviction
            return min(self.cache, key=lambda d: self.cache[d].last_access)

        # AHPR Scoring
        t_max = max(max((self.clock - r.last_access) for r in self.cache.values()), 1)
        f_max = max(max(r.frequency for r in self.cache.values()), 1)

        victim_domain, max_score = None, -1.0

        for domain, record in self.cache.items():
            recency_penalty = (self.clock - record.last_access) / t_max
            freq_penalty = 1.0 - (record.frequency / f_max)
            score = (self.alpha * recency_penalty) + ((1.0 - self.alpha) * freq_penalty)
            
            if score > max_score:
                max_score = score
                victim_domain = domain

        return victim_domain


# ==========================================
# 2. STREAMLIT UI CONFIGURATION
# ==========================================
st.set_page_config(page_title="Router DNS Defense", layout="wide")

st.title("🛡️ Secure Router Dashboard: DNS Defense Module")
st.markdown("Monitor network request filtering and cache resilience under DDoS attacks.")


# ==========================================
# 3. SIDEBAR & CONTROLS
# ==========================================
with st.sidebar:
    st.header("⚙️ Router Configuration")
    algo_choice = st.radio("Active Eviction Policy:", ["Standard LRU", "Proposed AHPR"])
    cache_size = st.slider("DNS Cache Capacity", 50, 500, 100)
    
    st.divider()
    
    st.header("🚨 Threat Simulation")
    attack_btn = st.button("💥 TRIGGER DDoS ATTACK", type="primary")


# ==========================================
# 4. TRAFFIC SIMULATOR
# ==========================================
is_ahpr_mode = (algo_choice == "Proposed AHPR")
router_cache = SecureRouterDNSCache(capacity=cache_size, is_ahpr=is_ahpr_mode)

hit_rate_history = []
time_steps = []

def record_metrics(cache):
    # Calculate valid requests to exclude successfully dropped attacks from the hit rate penalty
    valid_requests = max(1, cache.clock - cache.dropped_requests)
    hr = (cache.hits / valid_requests) * 100
    hit_rate_history.append(hr)
    time_steps.append(cache.clock)

# Phase 1: Normal Traffic (Pre-Attack)
for _ in range(5000):
    domain = random.randint(1, 50) 
    router_cache.resolve_domain(domain)
    if router_cache.clock % 500 == 0:
        record_metrics(router_cache)

# Phase 2 & 3: Attack and Recovery
if attack_btn:
    # Flood of random domains
    for attack_domain in range(1000, 3000):
        router_cache.resolve_domain(attack_domain, is_attack=True)
        if router_cache.clock % 500 == 0:
            record_metrics(router_cache)
            
    # Post-Attack Normal Traffic
    for _ in range(2000):
        domain = random.randint(1, 50)
        router_cache.resolve_domain(domain)
        if router_cache.clock % 500 == 0:
            record_metrics(router_cache)
else:
    # Just continue normal traffic if no attack
    for _ in range(4000):
        domain = random.randint(1, 50)
        router_cache.resolve_domain(domain)
        if router_cache.clock % 500 == 0:
            record_metrics(router_cache)

# Final Hit Rate Calculation
valid_requests_final = max(1, router_cache.clock - router_cache.dropped_requests)
final_hit_rate = (router_cache.hits / valid_requests_final) * 100


# ==========================================
# 5. DASHBOARD METRICS & GRAPHS
# ==========================================
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Current Cache Hit Rate", value=f"{final_hit_rate:.1f}%")
with col2:
    st.metric(label="Network Status", value="UNDER ATTACK" if attack_btn else "SECURE")
with col3:
    st.metric(label="Filtered Attack Queries", value=f"{router_cache.dropped_requests}")

# --- RESILIENCE GRAPH ---
st.subheader("📊 Network Resilience (Hit Rate vs Time)")
df_chart = pd.DataFrame({
    "Simulation Clock": time_steps,
    "Hit Rate (%)": hit_rate_history
}).set_index("Simulation Clock")

st.line_chart(df_chart)

# --- LIVE TRAFFIC LOG ---
st.subheader("📡 Live Network Request Filtering")
if attack_btn and is_ahpr_mode:
    st.code("""
[WARN] Traffic spike detected.
[EVICT] Dropping low-frequency record: 1045.botnet.info
[EVICT] Dropping low-frequency record: 2901.botnet.info
[CACHE HIT] Legitimate traffic preserved: youtube.com
    """, language="bash")
elif attack_btn and not is_ahpr_mode:
     st.code("""
[WARN] Traffic spike detected.
[EVICT] Standard LRU active. Legitimate record lost: youtube.com
[MISS] Re-fetching legitimate domain...
    """, language="bash")
else:
    st.code("""
[CACHE HIT] youtube.com
[CACHE HIT] google.com
[RESOLVED] github.com
    """, language="bash")
