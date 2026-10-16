import csv
import math
import random

NUM_REQUESTS = 50000
ADDRESS_SPACE = 250
FRAME_CAPACITIES = [4, 8, 16, 32, 64]
ALPHA = 0.65

def generate_trace(workload_type):
    random.seed(1337)
    trace = []
    if workload_type == "Uniform_Random":
        trace = [random.randint(0, ADDRESS_SPACE - 1) for _ in range(NUM_REQUESTS)]
    elif workload_type == "Zipfian":
        s = 1.2
        weights = [1.0 / math.pow(i, s) for i in range(1, ADDRESS_SPACE + 1)]
        trace = random.choices(range(ADDRESS_SPACE), weights=weights, k=NUM_REQUESTS)
    elif workload_type == "Mixed_Scan":
        scan_addr = 0
        for _ in range(NUM_REQUESTS):
            if random.random() < 0.30:
                trace.append(scan_addr)
                scan_addr = (scan_addr + 1) % ADDRESS_SPACE
            else:
                trace.append(random.randint(0, 15))
    return trace

def run_fifo(capacity, trace):
    frames, in_memory, head, faults = [], set(), 0, 0
    for page in trace:
        if page in in_memory:
            continue
        faults += 1
        if len(frames) < capacity:
            frames.append(page)
        else:
            in_memory.remove(frames[head])
            frames[head] = page
            head = (head + 1) % capacity
        in_memory.add(page)
    return faults

def run_lru(capacity, trace):
    last_access, faults = {}, 0
    for t, page in enumerate(trace):
        if page not in last_access:
            faults += 1
            if len(last_access) >= capacity:
                lru_page = min(last_access, key=last_access.get)
                del last_access[lru_page]
        last_access[page] = t
    return faults

# --- UPDATED AHPR FUNCTION ---
def run_ahpr(capacity, trace):
    active_frames, faults = {}, 0
    
    for t, page in enumerate(trace):
        # Aging mechanism: decay historical frequency to prevent lock-in
        if t > 0 and t % 10000 == 0:
            for p in active_frames:
                active_frames[p][1] >>= 1  # Integer division by 2

        if page in active_frames:
            active_frames[page][0] = t
            active_frames[page][1] += 1
        else:
            faults += 1
            if len(active_frames) >= capacity:
                # Dynamic T_max and F_max based ONLY on currently loaded frames
                current_t_diffs = [(t - info[0]) for info in active_frames.values()]
                current_freqs = [info[1] for info in active_frames.values()]
                
                t_max = max(current_t_diffs) if current_t_diffs else 1
                f_max = max(current_freqs) if current_freqs else 1
                
                victim, max_score = None, -1.0
                for p, (last_t, freq) in active_frames.items():
                    recency_penalty = (t - last_t) / t_max
                    freq_penalty = 1.0 - (freq / f_max)
                    
                    score = (ALPHA * recency_penalty) + ((1.0 - ALPHA) * freq_penalty)
                    if score > max_score:
                        max_score = score
                        victim = p
                        
                del active_frames[victim]
            active_frames[page] = [t, 1]
    return faults

workloads = ["Zipfian", "Mixed_Scan", "Uniform_Random"]
rows = [["Workload", "FrameCapacity", "Algorithm", "TotalAccesses", "PageFaults", "PageFaultRate", "HitRatio"]]

print("[+] Running simulation benchmark...")
for w in workloads:
    trace = generate_trace(w)
    for c in FRAME_CAPACITIES:
        for name, fn in [("FIFO", run_fifo), ("LRU", run_lru), ("Proposed_AHPR", run_ahpr)]:
            faults = fn(c, trace)
            pfr = (faults / NUM_REQUESTS) * 100.0
            hit_ratio = 100.0 - pfr
            rows.append([w, c, name, NUM_REQUESTS, faults, f"{pfr:.4f}", f"{hit_ratio:.4f}"])

with open("memory_benchmark_results.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(rows)

print("[+] Dataset exported successfully to: memory_benchmark_results.csv")
