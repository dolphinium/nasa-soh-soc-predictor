# Project Setup and Initial Data Inspection (Notebook 1)

## 1. Overview

This phase involved setting up the project environment based on the provided roadmap and performing an initial inspection of the raw NASA battery data files (`.mat` format). This corresponds to Phase 1 of the implementation roadmap.

## 2. Environment and Directory Structure

*   Confirmed conda environment and necessary libraries (`numpy`, `pandas`, `scipy`, `matplotlib`, `seaborn`, `tensorflow`, `xgboost`, etc.) were installed.
*   Confirmed Jupyter Notebook environment setup within VS Code.
*   Initialized a Git repository for version control.
*   Created the project directory structure as recommended:
    ```
    your-project-root/
    ├── data/
    │   ├── raw_data/      # .mat files reside here
    │   └── processed_data/
    ├── notebooks/
    │   ├── 1_initial_data_inspection.ipynb # This stage
    │   ├── ... (other notebooks planned)
    ├── scripts/           # For helper functions
    ├── models/            # For saved models
    ├── visualizations/    # For saved plots
    ├── api/               # For deployment code
    ├── .gitignore
    ├── README.md
    └── requirements.txt
    ```

## 3. Initial Data Loading and Inspection (`1_initial_data_inspection.ipynb`)

*   **Goal:** Load one of the `.mat` files (B0005.mat) and understand its internal structure.
*   **Tool:** Used `scipy.io.loadmat`.
*   **Code Snippet (Initial Load):**
    ```python
    import scipy.io
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import os

    RAW_DATA_DIR = '../data/raw_data/'
    file_path_b0005 = os.path.join(RAW_DATA_DIR, 'B0005.mat')
    mat_b0005 = scipy.io.loadmat(file_path_b0005)

    print(f"Type: {type(mat_b0005)}")
    print(f"Keys: {mat_b0005.keys()}")

    main_key = 'B0005'
    if main_key in mat_b0005:
        data_b0005 = mat_b0005[main_key]
        print(f"Main data dtype: {data_b0005.dtype}")
        if 'cycle' in data_b0005.dtype.names:
             cycles_b0005 = data_b0005['cycle'][0, 0]
             print(f"Cycle array shape: {cycles_b0005.shape}")
             if cycles_b0005.shape[1] > 0:
                 first_cycle = cycles_b0005[0, 0]
                 print(f"First cycle dtype fields: {first_cycle.dtype.names}")
                 if 'data' in first_cycle.dtype.names:
                     first_cycle_data_struct = first_cycle['data'][0,0]
                     print(f"Measurement struct fields: {first_cycle_data_struct.dtype.names}")
                     # Further refined
    ```
*   **Findings:**
    *   `.mat` files load as Python dictionaries.
    *   The main data is nested within a key matching the battery ID (e.g., `'B0005'`).
    *   Data is stored in structured NumPy arrays.
    *   The structure follows: `dict -> structured_array[battery_id] -> structured_array['cycle'][0, 0] -> array_of_cycles`.
    *   Each cycle element is a structured array containing `'type'`, `'ambient_temperature'`, `'time'`, and `'data'`.
    *   The `'data'` element within a cycle is another structured array containing the actual time-series measurements (e.g., `'Voltage_measured'`, `'Current_measured'`, `'Temperature_measured'`, `'Time'`, plus charger/load specific fields).
*   **Refined Inspection:** Confirmed that measurement arrays (e.g., `Voltage_measured`) are typically `(1, n_readings)` NumPy arrays and need to be accessed correctly (e.g., `measurement_struct['Voltage_measured']`).
*   **Confirmation:** Briefly loaded B0006.mat and B0018.mat to confirm they followed the same structure.

## 4. Next Step Planning

*   Identified the need for a parsing function to extract data from the complex nested structure into a more usable format (Pandas DataFrame).
*   Outlined the desired DataFrame structure and the logic for the parsing function.