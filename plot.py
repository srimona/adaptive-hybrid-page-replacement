
import matplotlib.pyplot as plt
import pandas as pd

# Load the dataset
df = pd.read_csv("memory_benchmark_results.csv")
workloads = ["Zipfian", "Mixed_Scan", "Uniform_Random"]

# Create a 1x3 grid of subplots (1 row, 3 columns)
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Define consistent styling for the algorithms
styles = {"FIFO": "o--", "LRU": "s--", "Proposed_AHPR": "^-"}
colors = {"FIFO": "#d95f02", "LRU": "#7570b3", "Proposed_AHPR": "#1b9e77"}

# Iterate through each workload and its corresponding subplot axis
for i, workload in enumerate(workloads):
    ax = axes[i]
    subset_df = df[df["Workload"] == workload]
    
    # Plot each algorithm on the current subplot
    for algo in df["Algorithm"].unique():
        algo_subset = subset_df[subset_df["Algorithm"] == algo]
        ax.plot(
            algo_subset["FrameCapacity"],
            algo_subset["PageFaultRate"],
            styles[algo],
            color=colors[algo],
            label=algo,
            linewidth=2,
            markersize=7,
        )
        
    # Formatting for the specific subplot
    # Replace underscores with spaces for cleaner titles (e.g., "Mixed Scan Workload")
    clean_title = workload.replace("_", " ")
    ax.set_title(f"{clean_title} Workload", fontsize=14)
    ax.set_xlabel("Physical Frame Capacity (N)", fontsize=12)
    
    # Only show the Y-axis label on the far left graph to reduce clutter
    if i == 0:
        ax.set_ylabel("Page Fault Rate (%)", fontsize=12)
        ax.legend(title="Algorithm", frameon=True)
    
    ax.set_xticks([4, 8, 16, 32, 64])
    ax.grid(True, linestyle=":", alpha=0.6)

# Add an overarching title for the entire figure
plt.suptitle("Page Fault Rate vs. Physical Frame Capacity Across Workloads", fontsize=16, y=1.05)

# Adjust layout to prevent overlapping text
plt.tight_layout()

# Save the figure in high resolution
plt.savefig("fig_page_fault_rate_all.png", dpi=300, bbox_inches="tight")
print("[+] Graph saved successfully as fig_page_fault_rate_all.png")

# Display the window
plt.show()