# Benchmarking ECG R-Peak Detectors: Offline & Online Evaluation across Heterogeneous Datasets

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

> This is the official repository for the conference paper: *Benchmarking ECG R-peak Detectors in Offline and Real-time Settings across Heterogeneous Datasets*.

---

## Abstract
Reliable R-peak detection is crucial for ECG analysis, especially in wearable applications. While many algorithms exist, they are often validated on clean, clinical datasets (like MIT-BIH) in offline mode.

This repository provides a comprehensive benchmarking framework to evaluate ECG R-peak detection algorithms over 5 heterogeneous datasets using both offline and real-time scenarios.

The evaluation is done using advanced metrics such as the **F1-Score** by (Charlton et al., 2022) and **Jitter F1** by (Porr et al., 2024), as well as the computational efficiency (**CPUTime**) of the algorithms.

---

## Description

Standard benchmarking procedures often rely on noise-free datasets, potentially overestimating algorithmic performance in real-world scenarios. This project addresses this limitation by evaluating 10 open-source R-peak detection algorithms across five heterogeneous datasets comprising daily-living conditions, various levels of physical activity, and both normal and arrhythmic rhythms. 

The datasets included in this framework are:
- **Fantasia Database**: https://doi.org/10.13026/C2RG61
- **LUDB** (Lobachevsky University Database): https://doi.org/10.13026/eegm-h675
- **MIT-BIH Database**: https://doi.org/10.13026/C2F305
- **GUDB** (Glasgow University Database): https://doi.org/10.5525/gla.researchdata.716
- **High Intensity Exercise Database**: https://doi.org/10.5281/zenodo.5727800

The framework evaluates detectors in two distinct scenarios. 
- The **Offline Benchmark** processes the whole ECG signal recording, thus simulating a batch processing scenario where the entire ECG signal is available at once. 
- The **Online Benchmark** simulates a real-time data streaming scenario. The ECG signal is sequentially processed using a sliding window of varying lengths (1s, 2s, 3s, 4s, 5s).

### Relation to NeuroKit2

This work builds upon the original benchmarking tools for ECG R-peak detection algorithms provided by **Dominique Makowski** and the [NeuroKit2](https://github.com/neuropsychology/NeuroKit) team. This repository significantly extends their original contribution as follows:
- Implementation of the F1-Score and Jitter F1 performance metrics
- Extension to 5 heterogeneous datasets
- Implementation of the online benchmark scenario
- Code refactoring and optimization to support both offline and online benchmarks
- Implementation of statistical analysis tools to compare the performance of the algorithms across datasets and window lengths.

---

## Installation & Setup

To set up the benchmarking environment, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/SimoDoc98/ecg-rpeak-benchmark.git](https://github.com/SimoDoc98/ecg-rpeak-benchmark.git)
    cd ecg-rpeak-benchmark
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Data Setup:**
    Due to licensing and size constraints, the raw datasets are not included in this repository. However, automated setup scripts to format the data correctly are provided. The `data/` folder already contains sub-directories for each dataset (e.g., `data/Fantasia`).

    For each dataset you wish to use:
    * Download the original database ZIP file from the official source.
    * Extract the downloaded folder **inside** the corresponding directory in `data/`.
    * Run the setup script found in that folder.

    *Example for Fantasia:*
    ```bash
    # After downloading and extracting 'fantasia-database-1.0.0' into data/Fantasia/
    cd data/Fantasia
    python setup_fantasia.py
    ```
    This script will automatically process the raw files and generate the `ECGs.csv` and `Rpeaks.csv` required for the benchmark.

---

## Usage

### Running the Benchmarks
Once the datasets are set up, you can run either the offline or online benchmark using the following commands:
- **Offline Benchmark:**
    ```bash
    python main_offline.py
    ```
- **Online Benchmark:**
    ```bash
    python main_online.py
    ```
The results of the benchmarking analysis will be saved as _.csv_ files in the `results/` directory.

### Adding a Custom ECG R-Peak Detection Algorithm

To add a custom ECG R-peak detection algorithm, follow these steps:
1. Open `ecg_benchmark/detectors.py`.
2. Add your algorithm as a new function following the existing signature `detector_yourname(ecg, sampling_rate)`. The function should take the ECG signal and its sampling rate as inputs and return an array of R-peaks indices.
3. Import your function in `main_offline.py` (or online) and add it to the `DETECTORS` list.

To test your detector against a strong benchmark, it is suggested keeping `Neurokit` as a baseline in the `DETECTORS` list, as it has proven to be the most robust algorithm in the benchmark tests.

### Adding a Custom Dataset

To add a custom dataset, follow these steps:
1. Create a new folder for your dataset inside the `data/` directory (e.g., `data/MyDataset`).
2. Generate the `ECGs.csv` and `Rpeaks.csv` files for your dataset. The `ECGs.csv` should contain the columns `ECG`, `Participant`, `Sample`, `Sampling_Rate`, `Database`; the `Rpeaks.csv` should contain the columns `Rpeaks`, `Participant`, `Sample`, `Sampling_Rate`, `Database`.
3. Add the custom dataset path to the `DATASET_PATHS` list in `main_offline.py` (or online) to include it in the benchmarking process.

If the dataset has more than one experimental condition (e.g., different levels of physical activity), it is recommended to specify it in the `Database` column of the `ECGs.csv` and `Rpeaks.csv` files by using a format like `MyDataset_Condition1`, `MyDataset_Condition2`, etc. This will allow for more granular analysis of the results across different conditions.

---

## References

1. P. H. Charlton et al., “Detecting beats in the photoplethysmogram: Benchmarking open-source algorithms,” Physiol. Meas., 43(8):085007, 2022.
2. Porr B, Macfarlane PW (2024) A new QRS detector stress test combining temporal jitter and F-score (JF) reveals significant performance differences amongst popular detectors. PLOS ONE 19(11): e0309739.
3. D. Makowski et al., “NeuroKit2: A Python toolbox for neurophysiological signal processing,” Behav. Res. Methods, 53(4):1689–1696, 2021.

---

## How to Cite

If you use this code or findings in your research, please cite our paper:

```bash
@inproceedings{costantini2026benchmarking,
  title={Benchmarking ECG R-peak Detectors in Offline and Real-time Settings across Heterogeneous Datasets},
  author={Costantini, Simone and Storm, F. A. and Bianchi, A. M.},
  year={2026},
}
```