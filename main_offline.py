"""
OFFLINE ECG R-PEAK DETECTION BENCHMARK
======================================

Description:
    This script extends an offline benchmark of several R-peak detection algorithms originally proposed by Dominik
    Makowski with Neurokit2. It processes entire ECG recordings at once, evaluating the algorithms' performance
    in terms of accuracy (F1-Score by Charlton et al. (2022)) and temporal precision (Jitter F1 by Porr et al., (2024)).

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

try:
    from ecg_benchmark.data_loader import load_dataset
    from ecg_benchmark.engines import run_benchmark_offline
    from ecg_benchmark.detectors import *
    from statistics.descriptive import print_descriptive_stats
    from statistics.launcher import run_inferential_stats
except ImportError as e:
    print(f"[CRITICAL ERROR] Could not import project modules: {e}")
    print("Ensure you are running the script from the project root directory.")
    sys.exit(1)

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

OUTPUT_FILENAME = "results/offline_benchmark.csv"


# --- UTILITIES ---
class Logger:
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
    Logger.section("STARTING OFFLINE ECG BENCHMARK")
    all_results = []

    # 1. Iterate over datasets
    for db_name, db_path in DATASET_PATHS.items():
        Logger.section(f"Processing Database: {db_name}")

        # Load data using the data_loader module
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

            # Validation check for empty data
            if subset_ecg.empty or subset_rpeaks.empty:
                Logger.warn(f"Empty data for {participant}. Skipping.")
                continue

            # Extract signal arrays and metadata
            ecg_signal = subset_ecg["ECG"].values
            sampling_rate = subset_ecg["Sampling_Rate"].values[0]
            true_rpeaks = subset_rpeaks["Rpeaks"].values

            # Log participant processing
            Logger.info(f"Processing {i + 1}/{total_recordings}: {participant} | Cond: {condition_raw}")

            # 3. Benchmark Detectors
            for algo in DETECTORS:
                # Execute engine
                res = run_benchmark_offline(algo, ecg_signal, true_rpeaks, sampling_rate)

                # Append metadata
                res["Database"] = db_name
                res["Participant"] = participant
                res["Condition"] = condition_raw

                all_results.append(res)

    # 4. Finalizing and Saving
    Logger.section("BENCHMARK COMPLETE")

    if all_results:
        df = pd.DataFrame(all_results)

        try:
            # A. Save Raw Results
            df.to_csv(OUTPUT_FILENAME, index=False)
            Logger.success(f"Results successfully saved to: {os.path.abspath(OUTPUT_FILENAME)}")
            Logger.info(f"Total entries: {len(df)}")

            # B. Print Descriptive Statistics (Python)
            print_descriptive_stats(OUTPUT_FILENAME, metric="Jitter_F1")

            # C. Run Inferential Statistics (R)
            run_inferential_stats(mode="offline", input_csv=OUTPUT_FILENAME)

        except Exception as e:
            Logger.warn(f"Failed to process results: {e}")
    else:
        Logger.warn("No results generated. Check dataset paths.")


if __name__ == "__main__":
    main()