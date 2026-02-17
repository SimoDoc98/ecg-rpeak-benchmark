# -*- coding: utf-8 -*-
"""
Script for formatting the Lobachevsky University Electrocardiography Database

Steps:
    1. Download zipped data base from https://physionet.org/content/ludb/1.0.1/ 
    2. Unzip the folder so that you have a `lobachevsky-university-electrocardiography-database-1.0.1/` folder'
    3. Run this script.

Reference:
- Kalyakulina, A., Yusipov, I., Moskalenko, V., Nikolskiy, A., Kosonogov, K., Zolotykh, N., & Ivanchenko, M. (2021).
    Lobachevsky University Electrocardiography Database (version 1.0.1). PhysioNet.
    RRID:SCR_007345. https://doi.org/10.13026/eegm-h675
"""
import pandas as pd
import numpy as np
import wfdb
import os

dfs_ecg = []
dfs_rpeaks = []

for participant in range(200):
    filename = str(participant + 1)

    data, info = wfdb.rdsamp(
        "./lobachevsky-university-electrocardiography-database-1.0.1/data/" + filename
    )

    # Get signal
    data = pd.DataFrame(data, columns=info["sig_name"])
    data = data[["i"]].rename(columns={"i": "ECG"})
    data["Participant"] = "LUDB_%.2i" % (participant + 1)
    data["Sample"] = range(len(data))
    data["Sampling_Rate"] = info["fs"]
    data["Database"] = "LUDB"

    # Get annotations
    anno = wfdb.rdann(
        "./lobachevsky-university-electrocardiography-database-1.0.1/data/" + filename, "i"
    )
    anno = anno.sample[np.where(np.array(anno.symbol) == "N")[0]]
    anno = pd.DataFrame({"Rpeaks": anno})
    anno["Participant"] = "LUDB_%.2i" % (participant + 1)
    anno["Sampling_Rate"] = info["fs"]
    anno["Database"] = "LUDB"

    # Store with the rest
    dfs_ecg.append(data)
    dfs_rpeaks.append(anno)

# Save
df_ecg = pd.concat(dfs_ecg).to_csv("ECGs.csv", index=False)
dfs_rpeaks = pd.concat(dfs_rpeaks).to_csv("Rpeaks.csv", index=False)
