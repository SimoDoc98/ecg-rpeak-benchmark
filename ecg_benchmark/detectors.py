# ecg_benchmark/detectors.py
"""
Wrapper functions for various ECG R-peak detection algorithms.
Original Author: Dominik Makowski (NeuroKit2)
Extended by: Costantini et al. (2026) for uniform benchmarking interface.

Instructions to add new algorithms:
You can add a new function to test by copy-pasting your own R-peak detection algorithm here below.
Please, ensure consistency in input parameters and output format (returning R-peak indices).
The function name should follow the pattern `detector_algorithmname` for clarity in benchmarking results.
"""
import neurokit2 as nk


def detector_neurokit(ecg, sampling_rate):
    signal, info = nk.ecg_peaks(ecg, sampling_rate=sampling_rate, method="neurokit")
    return info["ECG_R_Peaks"]

def detector_pantompkins1985(ecg, sampling_rate):
    signal, info = nk.ecg_peaks(ecg, sampling_rate=sampling_rate, method="pantompkins1985")
    return info["ECG_R_Peaks"]

def detector_hamilton2002(ecg, sampling_rate):
    signal, info = nk.ecg_peaks(ecg, sampling_rate=sampling_rate, method="hamilton2002")
    return info["ECG_R_Peaks"]

def detector_martinez2003(ecg, sampling_rate):
    signal, info = nk.ecg_peaks(ecg, sampling_rate=sampling_rate, method="martinez2004")
    return info["ECG_R_Peaks"]

def detector_christov2004(ecg, sampling_rate):
    signal, info = nk.ecg_peaks(ecg, sampling_rate=sampling_rate, method="christov2004")
    return info["ECG_R_Peaks"]

def detector_gamboa2008(ecg, sampling_rate):
    signal, info = nk.ecg_peaks(ecg, sampling_rate=sampling_rate, method="gamboa2008")
    return info["ECG_R_Peaks"]

def detector_elgendi2010(ecg, sampling_rate):
    signal, info = nk.ecg_peaks(ecg, sampling_rate=sampling_rate, method="elgendi2010")
    return info["ECG_R_Peaks"]

def detector_engzeemod2012(ecg, sampling_rate):
    signal, info = nk.ecg_peaks(ecg, sampling_rate=sampling_rate, method="engzeemod2012")
    return info["ECG_R_Peaks"]

def detector_kalidas2017(ecg, sampling_rate):
    signal, info = nk.ecg_peaks(ecg, sampling_rate=sampling_rate, method="kalidas2017")
    return info["ECG_R_Peaks"]

def detector_rodrigues2021(ecg, sampling_rate):
    signal, info = nk.ecg_peaks(ecg, sampling_rate=sampling_rate, method="rodrigues2021")
    return info["ECG_R_Peaks"]