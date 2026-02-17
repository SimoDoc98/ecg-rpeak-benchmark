"""
ONLINE ECG R-PEAK DETECTION BENCHMARK
======================================

Description:
    This script simulates a real-time environment to evaluate R-peak detection algorithms under streaming conditions.
    It processes ECG signals using a sliding window approach with buffering and overlap mechanisms, mimicking the
    constraints of wearable devices or bedside monitors. The benchmark assesses both accuracy (F1-Score) and temporal
    precision (Jitter F1) of the detectors across multiple datasets.

Usage:
    Ensure the 'data' directory is populated with the required datasets.
    Run from the project root: $ python main_offline.py

References:
    - P. H. Charlton et al., “Detecting beats in the photoplethysmogram: Benchmarking open-source algorithms,”
        Physiological Measurements, 43(8):085007, 2022. https://doi.org/10.1088/1361-6579/ac826d
    - Porr B, Macfarlane PW (2024) A new QRS detector stress test combining temporal jitter and F-score (JF) reveals
        significant performance differences amongst popular detectors. PLoS ONE 19(11): e0309739.
        https://doi.org/10.1371/journal.pone.0309739

To cite this work:
    Costantini, S., Storm, F. A., & Bianchi, A. M. (2026). "Benchmarking ECG R-peak Detectors in Offline and
    Real-time Settings across Heterogeneous Datasets". Proceedings of Workshop Biosignale 2026.
"""
import pandas as pd
import sys
import os
import datetime
import warnings

try:
    from ecg_benchmark.data_loader import load_dataset
    from ecg_benchmark.engines import run_benchmark_online
    from ecg_benchmark.detectors import *
except ImportError as e:
    print(f"[CRITICAL ERROR] Could not import project modules: {e}")
    print("Ensure you are running the script from the project root directory.")
    sys.exit(1)

warnings.filterwarnings("ignore", category=RuntimeWarning, module="numpy")

# --- CONFIGURATION ---
# Dictionary mapping dataset names to their relative directory paths
DATASET_PATHS = {
    "Fantasia": "data/Fantasia",
    "GUDB": "data/GUDB",
    "MIT-BIH Arrhythmia": "data/MIT-BIH Arrhythmia",
    "MIT-BIH Normal Sinus Rhythm": "data/MIT-BIH Normal Sinus Rhythm",
    "LUDB": "data/LUDB",
    "High Intensity Exercise": "data/High Intensity Exercise"
}

# List of detectors to be benchmarked
DETECTORS = [
    detector_neurokit,
    detector_pantompkins1985,
    detector_hamilton2002,
    detector_martinez2003,
    detector_christov2004,
    detector_gamboa2008,
    detector_elgendi2010,
    detector_engzeemod2012,
    detector_kalidas2017,
    detector_rodrigues2021
]

# Window lengths (in seconds) to simulate real-time streaming
WINDOWS_TO_TEST = [1, 2, 3, 4, 5]

OUTPUT_FILENAME = "results/online_benchmark.csv"


# --- UTILITIES ---
class Logger:
    """Simple logger for professional console output."""

    @staticmethod
    def info(msg):
        t = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{t}] [INFO]  {msg}")

    @staticmethod
    def warn(msg):
        t = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{t}] [WARN]  {msg}")

    @staticmethod
    def success(msg):
        t = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{t}] [OK]    {msg}")

    @staticmethod
    def section(msg):
        print(f"\n{'=' * 60}\n{msg}\n{'=' * 60}")


# --- MAIN EXECUTION ---
def main():
    Logger.section("STARTING ONLINE ECG BENCHMARK (STREAMING SIMULATION)")
    all_results = []

    # 1. Iterate over datasets
    for db_name, db_path in DATASET_PATHS.items():
        Logger.section(f"Processing Database: {db_name}")

        ecgs, rpeaks_all = load_dataset(db_path)

        if ecgs is None:
            Logger.warn(f"Skipping {db_name}: Files not found in '{db_path}'")
            continue

        participants = ecgs["Participant"].unique()
        Logger.info(f"Loaded {len(participants)} participants from {db_name}.")

        # 2. Iterate over unique recordings (Participant + Condition)
        grouped_data = ecgs.groupby(["Participant", "Database"])

        total_recordings = len(grouped_data)
        Logger.info(f"Found {len(participants)} participants and {total_recordings} unique recordings.")

        for i, ((participant, condition_raw), subset_ecg) in enumerate(grouped_data):
            # Extract corresponding R-peaks
            subset_rpeaks = rpeaks_all[(rpeaks_all["Participant"] == participant) &
                                       (rpeaks_all["Database"] == condition_raw)]

            if subset_ecg.empty or subset_rpeaks.empty:
                continue

            ecg_signal = subset_ecg["ECG"].values
            sampling_rate = subset_ecg["Sampling_Rate"].values[0]
            true_rpeaks = subset_rpeaks["Rpeaks"].values

            # Log participant processing
            Logger.info(f"Processing {i + 1}/{total_recordings}: {participant} | Cond: {condition_raw}")

            # 3. Iterate over Detectors
            for algo in DETECTORS:
                algo_name_clean = algo.__name__.replace("detector_", "")

                # 4. Iterate over Window Lengths
                for win_len in WINDOWS_TO_TEST:
                    # Execute Online Engine
                    res = run_benchmark_online(algo, ecg_signal, true_rpeaks, sampling_rate, win_len_sec=win_len)

                    # Append metadata
                    res["Database"] = db_name
                    res["Participant"] = participant
                    res["Condition"] = condition_raw

                    all_results.append(res)

    # 5. Finalizing and Saving
    Logger.section("BENCHMARK COMPLETE")

    if all_results:
        df = pd.DataFrame(all_results)

        try:
            # 1. Save Raw Results
            df.to_csv(OUTPUT_FILENAME, index=False)
            Logger.success(f"Results successfully saved to: {os.path.abspath(OUTPUT_FILENAME)}")

            # 2. Print Descriptive Statistics (Python)
            # Note: Descriptive stats aggregate over Window Lengths by default in the current function.
            # If you want specific window stats, you'd need to filter the dataframe before passing it.
            print_descriptive_stats(OUTPUT_FILENAME, metric="Jitter_F1")

            # 3. Run Inferential Statistics (R)
            run_inferential_stats(mode="online", input_csv=OUTPUT_FILENAME)

        except Exception as e:
            Logger.warn(f"Failed to process results: {e}")
    else:
        Logger.warn("No results generated.")


if __name__ == "__main__":
    main()