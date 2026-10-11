import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("memory_benchmark_results.csv")
zipf_df = df[df["Workload"] == "Zipfian"]

plt.figure(figsize=(8, 5))
styles = {"FIFO": "o--", "LRU": "s--", "Proposed_AHPR": "^-"}
colors = {"FIFO": "#d95f02", "LRU": "#7570b3", "Proposed_AHPR": "#1b9e77"}

for algo in zipf_df["Algorithm"].unique():
  subset = zipf_df[zipf_df["Algorithm"] == algo]
  plt.plot(
      subset["FrameCapacity"],
      subset["PageFaultRate"],
      styles[algo],
      color=colors[algo],
      label=algo,
      linewidth=2,
      markersize=7,
  )

plt.title(
    "Page Fault Rate vs. Physical Frame Capacity (Zipfian Workload)",
    fontsize=12,
)
plt.xlabel("Physical Frame Capacity (N)", fontsize=11)
plt.ylabel("Page Fault Rate (%)", fontsize=11)
plt.xticks([4, 8, 16, 32, 64])
plt.grid(True, linestyle=":", alpha=0.6)
plt.legend(title="Algorithm", frameon=True)
plt.tight_layout()
plt.savefig("fig_page_fault_rate.png", dpi=300)
print("[+] Graph saved successfully as fig_page_fault_rate.png")
plt.show()