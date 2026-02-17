# data_loader.py
import pandas as pd
import os


def load_dataset(base_path):
    """
    Loads ECGs.csv and Rpeaks.csv from a given folder.

    :param: base_path (str): The base directory containing ECGs.csv and Rpeaks.csv.
    :return: tuple: A tuple containing two DataFrames (ecgs, rpeaks).
    """
    try:
        ecgs_path = os.path.join(base_path, "ECGs.csv")
        rpeaks_path = os.path.join(base_path, "Rpeaks.csv")

        if not os.path.exists(ecgs_path) or not os.path.exists(rpeaks_path):
            return None, None

        ecgs = pd.read_csv(ecgs_path)
        rpeaks = pd.read_csv(rpeaks_path)
        return ecgs, rpeaks
    except Exception as e:
        print(f"Error loading {base_path}: {e}")
        return None, None