# ecg_benchmark/engines.py
"""
Benchmarking Engine Module.

This module contains the core logic to execute R-peak detection algorithms
in two modalities:
1. Offline: Processing the entire signal at once.
2. Online: Simulating a real-time stream with buffering and overlap.

Original Author: Dominik Makowski
Modified and Extended by: Simone Costantini for Costantini et al. (2026)
"""

import time
import numpy as np
import pandas as pd
from ecg_benchmark.metrics import calculate_f1_precision_recall, calculate_jitter_coefficient, calculate_jitter_f1


def run_benchmark_offline(detection_function, ecg_signal, true_rpeaks, sampling_rate):
    """
    Executes an R-peak detection algorithm on the full signal (Offline mode).

    :param: detection_function (callable): The detection function to test.
    :param: ecg_signal (array): The raw ECG signal.
    :param: true_rpeaks (array): Ground truth R-peak indices.
    :param: sampling_rate (int): Sampling frequency in Hz.
    :param: tolerance_ms (int, optional): Tolerance window for matching peaks. Defaults to 50ms.
    :return: dict: A dictionary containing performance metrics (Precision, Recall, F1, Jitter F1, Time).
    """

    # 1. Execution
    try:
        start_time = time.time()
        detected_peaks = detection_function(ecg_signal, sampling_rate)
        duration = time.time() - start_time
    except Exception as e:
        return {"Error": str(e), "Algorithm": detection_function.__name__.replace("detector_", ""),}

    # 2. Metrics Calculation
    precision, recall, f1 = calculate_f1_precision_recall(true_rpeaks, detected_peaks, sampling_rate)

    jitter_coeff = calculate_jitter_coefficient(true_rpeaks, detected_peaks, sampling_rate)
    jitter_f1 = calculate_jitter_f1(f1, jitter_coeff)

    return {
        "Algorithm": detection_function.__name__.replace("detector_", ""),
        "Precision": precision,
        "Recall": recall,
        "F1": f1,
        "Jitter_F1": jitter_f1,
        "Time_Total_s": duration,
        "Mode": "Offline"
    }


def run_benchmark_online(detection_function, ecg_signal, true_rpeaks, sampling_rate, win_len_sec=5):
    """
    Simulates real-time R-peak detection using a sliding window approach (Online mode).

    Logic:
    - The signal is processed in chunks of `win_len_sec`.
    - To simulate processing latency and avoid edge artifacts, only the first 90% of the window is used for detection.
    - An overlap strategy is used to avoid misdetections at window boundaries, with a duplicate removal step
        based on a refractory period assumption.

    :param: detection_function (callable): The detection function to test.
    :param: ecg_signal (array): The raw ECG signal.
    :param: true_rpeaks (array): Ground truth R-peak indices.
    :param: sampling_rate (int): Sampling frequency in Hz.
    :param: win_len_sec (int): Length of the sliding window in seconds.
    :return: dict: Performance metrics including average processing time per window.
    """

    window_len = int(win_len_sec * sampling_rate)
    step = int(window_len * 0.8)

    final_peaks = []
    previous_peaks = []
    computation_times = []

    current_idx = 0

    # Loop to simulate streaming
    while current_idx + window_len <= len(ecg_signal):

        # A. Extract Window
        window = ecg_signal[current_idx: current_idx + window_len]

        # B. Simulation Constraints (Processing 90% of window to reduce edge effects)
        proc_limit = int(window_len * 0.9)
        window_to_process = window[:proc_limit]

        # C. Algorithm Execution
        t0 = time.time()
        try:
            local_peaks = detection_function(window_to_process, sampling_rate)
        except Exception:
            local_peaks = []
        t1 = time.time()
        computation_times.append(t1 - t0)

        # D. Coordinate Mapping (Local -> Global)
        global_peaks = [p + current_idx for p in local_peaks]

        # E. Duplicate Removal (Merging logic)
        # Check against peaks found in the previous window overlap
        new_unique_peaks = []
        duplicate_tolerance = int(0.25 * sampling_rate)  # 250ms refractory period assumption

        for peak in global_peaks:
            is_duplicate = False
            for prev in previous_peaks:
                if abs(peak - prev) <= duplicate_tolerance:
                    is_duplicate = True
                    break
            if not is_duplicate:
                new_unique_peaks.append(peak)

        final_peaks.extend(new_unique_peaks)

        # F. Update buffer for next iteration
        # Keep only peaks from the end of the current window to check against next window
        overlap_start = current_idx + window_len - int(0.2 * window_len)
        previous_peaks = [p for p in global_peaks if p >= overlap_start]

        current_idx += step

    # 3. Metrics Calculation on the aggregated result
    precision, recall, f1 = calculate_f1_precision_recall(true_rpeaks, final_peaks, sampling_rate)

    jitter_coeff = calculate_jitter_coefficient(true_rpeaks, final_peaks, sampling_rate)
    jitter_f1 = calculate_jitter_f1(f1, jitter_coeff)

    avg_latency = np.mean(computation_times) if computation_times else 0

    return {
        "Algorithm": detection_function.__name__.replace("detector_", ""),
        "Precision": precision,
        "Recall": recall,
        "F1": f1,
        "Jitter_F1": jitter_f1,
        "Time_Avg_s": avg_latency,
        "Window_Sec": win_len_sec,
        "Mode": "Online"
    }