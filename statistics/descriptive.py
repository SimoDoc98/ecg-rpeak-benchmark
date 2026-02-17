import pandas as pd
import numpy as np
from tabulate import tabulate


def get_median_iqr(x):
    """Calculates Median and IQR and returns a formatted string 'Med (IQR)'."""
    if len(x) == 0:
        return "-"
    med = np.nanmedian(x)
    q1 = np.nanpercentile(x, 25)
    q3 = np.nanpercentile(x, 75)
    iqr = q3 - q1
    return f"{med:.3f} ({iqr:.3f})"


def print_descriptive_stats(csv_path, metric="Jitter_F1"):
    """
    Loads benchmark results and prints descriptive statistics tables (Median + IQR).

    Structure:
    1. Global Summary: Algorithm vs Database
    2. Detailed Summary: Algorithm vs Condition (per Database)
    """
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"[STATS] File not found: {csv_path}")
        return

    # Check if metric exists
    if metric not in df.columns:
        metric = "F1" if "F1" in df.columns else df.columns[-1]

    print(f"\n{'=' * 80}")
    print(f"DESCRIPTIVE STATISTICS (Metric: {metric})")
    print(f"{'=' * 80}")

    # --- ALGORITHM vs DATABASE ---
    print("\n[TABLE] Aggregated Performance by Dataset")
    pivot_db = df.pivot_table(
        index="Algorithm",
        columns="Database",
        values=metric,
        aggfunc=get_median_iqr
    )
    # Print using tabulate
    print(tabulate(pivot_db, headers="keys", tablefmt="simple_grid"))

    # --- ALGORITHM vs CONDITION (Per Database) ---
    databases = df["Database"].unique()

    # Check if 'Condition' column has varying values
    print("\n\n[TABLE] Detailed Performance by Condition")

    for db in databases:
        subset = df[df["Database"] == db]
        # Skip if only one condition exists to avoid redundancy
        if subset["Condition"].nunique() <= 1:
            continue

        print(f"\nDatabase: {db}")
        pivot_cond = subset.pivot_table(
            index="Algorithm",
            columns="Condition",
            values=metric,
            aggfunc=get_median_iqr
        )
        print(tabulate(pivot_cond, headers="keys", tablefmt="simple_grid"))

    print(f"{'-' * 80}\n")