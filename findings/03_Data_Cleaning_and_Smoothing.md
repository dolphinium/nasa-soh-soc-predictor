# Data Cleaning and Smoothing (Notebook 2)

## 1. Overview

This phase focused on cleaning the combined, parsed data and applying initial transformations, primarily addressing missing values, outliers, and signal noise. This corresponds mainly to Phase 2.1 and parts of Phase 2.3 of the roadmap.

## 2. Loading Data (`2_data_preparation.ipynb`)

*   Loaded the combined data from `data/processed_data/nasa_battery_data_combined.csv` into a DataFrame `df`.

## 3. Initial Checks

*   **Missing Values:**
    *   Checked using `df.isnull().sum()`.
    *   Found a large number of NaNs in `capacity` (expected, as it's only for discharge cycles).
    *   Found 2 NaNs each in `voltage_measured`, `current_measured`, `temperature_measured`.
    *   **Action:** Dropped the 2 rows containing NaNs in the measurement columns using `df.dropna(subset=...)`.
*   **Data Types:** Checked using `df.dtypes`. Types were deemed appropriate (float/int for numerical, object for categorical).
*   **Duplicates:** Checked using `df.duplicated().sum()`. Found 0 duplicate rows.

## 4. Outlier Analysis and Handling

*   **Visualization:** Generated histograms and box plots for key numerical measurement columns (`voltage_measured`, `current_measured`, `temperature_measured`, etc.) using `seaborn`.
*   **Statistical Summary:** Used `df[cols].describe()` to check min/max/mean etc.
*   **Findings:**
    *   **Voltage:** Clear outliers detected, especially values significantly above 4.2V (up to ~8.4V) and slightly below 0V. These were deemed physically implausible for normal operation.
    *   **Current:** Outliers detected, particularly below -2A (down to -4.5A). Decided these *might* be valid depending on test conditions and deferred handling.
    *   **Temperature:** Many points above the main distribution (up to ~42°C) were flagged by box plot, but considered potentially valid operating points rather than errors. Deferred handling.
*   **Handling Voltage Outliers:**
    *   Defined physical bounds (0.0V to 4.5V).
    *   Identified outliers using a boolean mask. Found only 7 outliers.
    *   Replaced outliers with `np.nan`.
    *   Used `groupby(['battery_id', 'cycle_number']).transform()` with `.interpolate(method='linear', limit_direction='both')` to fill NaNs within each cycle, preserving the time-series nature. Included a fallback `ffill().bfill()`.
    *   Re-visualized and checked `describe()` to confirm outliers were removed and the range was corrected.
    ```python
    # Key code snippet for interpolation
    voltage_outliers_mask = (df['voltage_measured'] < VOLTAGE_MIN) | (df['voltage_measured'] > VOLTAGE_MAX)
    df.loc[voltage_outliers_mask, 'voltage_measured'] = np.nan
    df['voltage_measured'] = df.groupby(['battery_id', 'cycle_number'])['voltage_measured'].transform(
        lambda x: x.interpolate(method='linear', limit_direction='both', limit_area=None)
    )
    # Fallback ffill/bfill added for robustness
    ```

## 5. Signal Smoothing (Transformation)

*   **Rationale:** To reduce high-frequency noise in time-series measurements before feature engineering or modeling.
*   **Method:** Applied the Savitzky-Golay filter (`scipy.signal.savgol_filter`) chosen for its ability to preserve signal shape.
*   **Implementation:**
    *   Chose `window_length=11` and `polyorder=2`.
    *   Applied filter to `voltage_measured`, `current_measured`, `temperature_measured`.
    *   Used `groupby(['battery_id', 'cycle_number']).transform()` to apply the filter independently to each cycle's measurements.
    *   Handled potential errors for cycles shorter than the window length.
    *   Stored smoothed data in new columns (e.g., `voltage_measured_smooth`).
    ```python
    from scipy.signal import savgol_filter
    # ... inside loop for cols_to_smooth ...
    def apply_savgol(series):
        if len(series) < window_length: return series
        try: return savgol_filter(series, window_length, polyorder, mode='interp')
        except ValueError: return series # Fallback
    df[smoothed_col_name] = df.groupby(['battery_id', 'cycle_number'])[col].transform(apply_savgol)
    ```
*   **Verification:** Plotted original vs. smoothed signals for an example discharge cycle (B0005, Cycle 2). Confirmed noise reduction looked reasonable without significant distortion.

## 6. Saving Preprocessed Data

*   Saved the resulting DataFrame `df` (containing cleaned, smoothed data and initial features like SoH - calculated in next step but saved here) to `data/processed_data/nasa_battery_data_preprocessed.csv`.