"""
Script for formatting the High-Intensity Exercise (HIE) Database

Steps:
    1. Download the ZIP database from https://zenodo.org/records/5727800
    2. Open it with a zip-opener (WinZip, 7zip).
    3. Extract the folder of the same name (named 'ECG_high_intensity_exercise') to the same folder as this script.
    4. Run this script.

Reference:
- De Giovanni, E., Teijeiro, T., David Meier, Millet, G., & Atienza, D. (2021). ECG in High Intensity Exercise Dataset
    [Data set]. Zenodo. https://doi.org/10.5281/zenodo.5727800
"""
import os
import pandas as pd
from glob import glob

ECG_PATH = "ECG_high_intensity_exercise/ecg_segments/"
ANN_PATH = "ECG_high_intensity_exercise/manual_annotations/"
SAMPLING_RATE = 250  # Hz
DATABASE_NAME = "High_Intensity_Exercise"

ecg_data = []
rpeaks_data = []

# Find all ECG files with the correct extension
files = sorted(glob(os.path.join(ECG_PATH, "*.csv")))

for file_path in files:
    filename = os.path.basename(file_path).replace(".csv", "")
    parts = filename.split("_")
    subject = parts[2].replace("sub", "")  # X
    segment = parts[3].replace("seg", "")  # Y

    participant_id = f"HIE_{subject}"
    database_id = f"HIE_seg{segment}"

    signal = pd.read_csv(file_path, header=None, usecols=[0])
    signal.columns = ["ECG"]
    signal["Participant"] = participant_id
    signal["Sample"] = range(len(signal))
    signal["Sampling_Rate"] = SAMPLING_RATE
    signal["Database"] = database_id
    ecg_data.append(signal)

    # Find corresponding annotation file
    ann_file = os.path.join(ANN_PATH, f"ecg_sub{subject}_seg{segment}_labels.csv")
    if os.path.exists(ann_file):
        rpeaks = pd.read_csv(ann_file, header=None, usecols=[0])
        rpeaks.columns = ["Rpeaks"]
        rpeaks["Participant"] = participant_id
        rpeaks["Sampling_Rate"] = SAMPLING_RATE
        rpeaks["Database"] = database_id
        rpeaks_data.append(rpeaks)

# Save the data to CSV files
pd.concat(ecg_data).to_csv("ECGs.csv", index=False)
pd.concat(rpeaks_data).to_csv("Rpeaks.csv", index=False)
