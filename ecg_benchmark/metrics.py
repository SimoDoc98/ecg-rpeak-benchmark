# ecg_benchmark/metrics.py
"""
Module to compute the evaluation metrics for ECG R-peak detection.

The metrics implemented include:
- F1 Score: Evaluates the precision and recall of detected R-peaks against true R-peaks,
    considering a specified tolerance in samples. Based on the standard definition by Charlton et al. (2022),
    where the threshold for a true positive was defined as 150 ms, in this implementation, a tolerance of 50 ms is used.
- Jitter F1: Combines the F1 score with a jitter score that quantifies the temporal accuracy of detected R-peaks.
    It is based on the work by Porr et al. (2024), where the jitter coefficient is computed as 1/(1+(mean jitter/12ms)).
    In this implementation, the Mean Absolute Difference (MAD) is used to compute the mean jitter,
    and the normalization factor is set to 10 ms.

References:
- P. H. Charlton et al., “Detecting beats in the photoplethysmogram: Benchmarking open-source algorithms,”
    Physiological Measurements, 43(8):085007, 2022. https://doi.org/10.1088/1361-6579/ac826d
- Porr B, Macfarlane PW (2024) A new QRS detector stress test combining temporal jitter and F-score (JF) reveals
    significant performance differences amongst popular detectors. PLoS ONE 19(11): e0309739.
    https://doi.org/10.1371/journal.pone.0309739
"""
import numpy as np
from scipy.stats import stats


def calculate_f1_precision_recall(true_rpeaks, found_rpeaks, sampling_rate=250, tolerance_ms=50):
    if len(found_rpeaks) == 0 or len(true_rpeaks) == 0:
        return 0.0, 0.0, 0.0

    true_rpeaks = np.array(true_rpeaks)
    found_rpeaks = np.array(found_rpeaks)

    tolerance_samples = int(tolerance_ms * sampling_rate / 1000)

    tp = 0
    matched = np.zeros(len(found_rpeaks), dtype=bool)

    for true_peak in true_rpeaks:
        diffs = np.abs(found_rpeaks - true_peak)
        within_tol = np.where(diffs <= tolerance_samples)[0]
        if within_tol.size > 0:
            # Find closest match
            best_match = within_tol[np.argmin(diffs[within_tol])]
            if not matched[best_match]:
                matched[best_match] = True
                tp += 1

    fp = len(found_rpeaks) - tp
    fn = len(true_rpeaks) - tp

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    return precision, recall, f1


def calculate_jitter_coefficient(true_rpeaks, found_rpeaks, sampling_rate=250, max_shift_samples=200, norm_jitter=0.01):
    true_rpeaks = np.array(true_rpeaks)
    found_rpeaks = np.array(found_rpeaks)

    diffs = []
    matched = np.zeros(len(found_rpeaks), dtype=bool)

    for true_peak in true_rpeaks:
        diffs_all = np.abs(found_rpeaks - true_peak)
        within_tol = np.where(diffs_all <= max_shift_samples)[0]
        if within_tol.size > 0:
            best_idx = within_tol[np.argmin(diffs_all[within_tol])]
            if not matched[best_idx]:
                matched[best_idx] = True
                diffs.append(np.abs(found_rpeaks[best_idx] - true_peak) / sampling_rate)

    if len(diffs) == 0:
        return np.nan

    jitter = stats.median_abs_deviation(diffs)

    if jitter == 0:
        return 1.0

    jitter_coefficient = 1 / (1 + (jitter / norm_jitter))

    return jitter_coefficient


def calculate_jitter_f1(f1, jitter_coefficient):
    jf = f1 * jitter_coefficient if not np.isnan(jitter_coefficient) else np.nan
    return jf