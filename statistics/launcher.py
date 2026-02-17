import os
import subprocess
import pandas as pd
import numpy as np
from tabulate import tabulate


def format_pvalue(val):
    """Format p-values for scientific presentation."""
    try:
        if val < 0.001:
            return "<.001 ***"
        elif val < 0.01:
            return f"{val:.3f} **"
        elif val < 0.05:
            return f"{val:.3f} *"
        else:
            return f"{val:.3f}"
    except:
        return str(val)


def print_statistical_summary(xlsx_path, mode="offline"):
    """
    Reads the R output Excel file and prints professional tables to console.
    """
    if not os.path.exists(xlsx_path):
        return

    print(f"\n{'=' * 80}")
    print(f"STATISTICAL ANALYSIS RESULTS ({mode.upper()})")
    print(f"{'=' * 80}")

    try:
        # Load Excel file
        xls = pd.ExcelFile(xlsx_path)

        # Define which sheets correspond to what type of data
        # Mapping: Sheet Name -> Display Title
        sheet_map = {
            "EMM_Jitter_F1": "ESTIMATED MARGINAL MEANS: Jitter F1 (Higher is Better)",
            "EMM_F1": "ESTIMATED MARGINAL MEANS: F1 Score",
            "EMM_Time": "ESTIMATED MARGINAL MEANS: Computational Time (s)",
            "PostHoc_Jitter_F1": "PAIRWISE COMPARISONS: Jitter F1",
            "PostHoc_F1": "PAIRWISE COMPARISONS: F1 Score",
            "PH_JF_Algo": "PAIRWISE: Jitter F1 (Between Algorithms)",
            "PH_Time_Algo": "PAIRWISE: Time (Between Algorithms)"
        }

        for sheet_name in xls.sheet_names:
            if sheet_name not in sheet_map:
                continue

            df = pd.read_excel(xls, sheet_name)
            title = sheet_map.get(sheet_name, sheet_name)

            print(f"\n{title}")

            # --- FORMATTING ---
            # 1. Round numeric columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                if "p.value" in col or "p-value" in col:
                    continue  # Handle separately
                df[col] = df[col].apply(lambda x: round(x, 3) if isinstance(x, (int, float)) else x)

            # 2. Format P-values nicely with stars
            p_cols = [c for c in df.columns if "p.value" in c or "p-value" in c]
            for p_col in p_cols:
                df[p_col] = df[p_col].apply(format_pvalue)

            # 3. Clean up column names for display
            df.columns = [c.replace(".", " ").title() for c in df.columns]

            # 4. Print Table
            print(tabulate(df, headers="keys", tablefmt="simple_grid", showindex=False))

    except Exception as e:
        print(f"Error formatting stats output: {e}")

    print(f"\nFull results saved in: {os.path.basename(xlsx_path)}\n")


def run_inferential_stats(mode="offline", input_csv=None, output_xlsx=None):
    """
    Handles the execution of R scripts for inferential statistics (GLMM).
    """
    # Define absolute paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    stats_dir = os.path.join(base_dir, "statistics")

    if mode.lower() == "offline":
        r_script = os.path.join(stats_dir, "stats_offline.R")
        default_in = os.path.join(base_dir, "results", "results_offline_benchmark.csv")
        default_out = os.path.join(base_dir, "results", "Offline_Results.xlsx")
    else:
        r_script = os.path.join(stats_dir, "stats_online.R")
        default_in = os.path.join(base_dir, "results", "results_online_benchmark.csv")
        default_out = os.path.join(base_dir, "results", "Online_Results.xlsx")

    # Override defaults
    input_csv = input_csv if input_csv else default_in
    output_xlsx = output_xlsx if output_xlsx else default_out

    if not os.path.exists(input_csv):
        print(f"[STATS] Input file not found: {input_csv}")
        return

    try:
        df = pd.read_csv(input_csv)
        n_algos = df["Algorithm"].nunique()
        if n_algos < 2:
            print(f"\n[STATS] Only {n_algos} algorithm detected. Inferential statistics (GLMM) skipped.")
            return
    except Exception as e:
        print(f"[STATS] Error reading CSV for pre-check: {e}")
        return

    # --- EXECUTION ---
    print(f"\n{'=' * 60}")
    print(f"STARTING R INFERENTIAL ANALYSIS ({mode.upper()})")
    print(f"Comparing {n_algos} algorithms via GLMM (Beta/Gamma families)")
    print(f"{'=' * 60}")

    try:
        # Run Rscript with arguments
        cmd = ["Rscript", r_script, input_csv, output_xlsx]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print_statistical_summary(output_xlsx, mode=mode)
        else:
            print(f"[STATS] R Execution Error:\n{result.stderr}")

    except FileNotFoundError:
        print("[STATS] 'Rscript' executable not found. Ensure R is installed and in your PATH.")
    except Exception as e:
        print(f"[STATS] Unexpected error: {e}")