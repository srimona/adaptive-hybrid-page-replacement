# Adaptive Hybrid Page Replacement (AHPR) Simulator

A high-performance discrete-event virtual memory simulator evaluating dynamic page replacement policies under skewed locality, sequential scan, and uniform random workloads. Designed and benchmarked for an undergraduate Computer Science & Engineering research study.

---

## Abstract & Overview

Modern operating systems rely heavily on efficient physical memory management to prevent costly disk and SSD I/O page fault overhead. Traditional single-metric heuristics suffer from structural weaknesses:
* **Least Recently Used (LRU)** experiences severe cache pollution during one-off sequential memory scans.
* **Least Frequently Used (LFU)** retains historic page references that no longer reflect the active working set.
* **First-In, First-Out (FIFO)** completely ignores memory access patterns and is susceptible to Belady's Anomaly.

The **Adaptive Hybrid Page Replacement (AHPR)** framework resolves these trade-offs by evaluating frames through a unified eviction scoring metric that balances normalized temporal recency decay and reference frequency history. This repository contains the complete simulation engine, synthetic trace generators, automated parameter sweeping tools, and visualization pipelines.

---

## Mathematical Formulation

Upon a page fault when all physical frames are occupied, AHPR evaluates an eviction penalty score $S_i$ for every active frame $i$:

$$S_i = \alpha \cdot \left(\frac{t_{current} - t_{last\_access,i}}{T_{max}}\right) + (1 - \alpha) \cdot \left(1 - \frac{f_i}{F_{max}}\right)$$

Where:
* $t_{current} - t_{last\_access,i}$ represents the temporal recency elapsed time since frame $i$ was last referenced.
* $T_{max}$ represents the maximum elapsed time observed within the active working window ($t_{current} + 1$).
* $f_i$ denotes the frequency access count of frame $i$.
* $F_{max}$ is the peak reference count among all resident memory frames.
* $\alpha \in [0.0, 1.0]$ is an adaptive tuning factor governing the trade-off between recency and frequency.
* **Eviction Policy:** The page with the maximum score $S_i$ is chosen as the eviction candidate.

### Scan Resistance & Dynamic Adaptation
* **Sequential Scan Filtering:** When an unrepeated sequential scan passes through memory, each scanned page enters with frequency $f_i = 1$. The frequency penalty term $(1 - f_i / F_{max})$ immediately approaches $1.0$, giving transient scan pages an elevated eviction score and protecting high-frequency working pages from eviction.
* **Dynamic $\alpha$ Tuning:** A sliding observation window monitors moving hit rates; when hit rates drop during scan phases, $\alpha$ shifts dynamically to prioritize frequency resistance.

---

## Features & Supported Algorithms

* **FIFO (First-In, First-Out):** Evicts the oldest loaded physical frame regardless of reference history.
* **LRU (Least Recently Used):** Evicts the page with the oldest access timestamp.
* **Optimal (Belady's Algorithm):** An offline theoretical lower-bound baseline that evicts the page unreferenced for the longest time in the future[cite: 1].
* **AHPR (Static & Dynamic):** Evaluates runtime hybrid penalty metrics with dynamic $\alpha$ adaptation[cite: 1].

### Synthetic Workload Generators
* **Zipfian Distribution ($s = 1.2$):** Simulates power-law memory access skew typical of database management systems and web caches[cite: 1].
* **Mixed Sequential Scan:** Intersperses 70% concentrated working-set locality with 30% sequential scans to assess scan resilience[cite: 1].
* **Uniform Random:** Uncorrelated stochastic access patterns modeling unpredictable memory pressure[cite: 1].

