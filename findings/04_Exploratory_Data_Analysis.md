# Exploratory Data Analysis (EDA) (Notebook 3)

## 1. Overview

This phase focused on understanding the preprocessed data, exploring relationships between variables, and identifying patterns related to battery degradation (SoH). This corresponds to Phase 3 of the roadmap.

## 2. Loading Preprocessed Data (`3_exploratory_data_analysis.ipynb`)

*   Loaded the cleaned and smoothed data from `data/processed_data/nasa_battery_data_preprocessed.csv` into `df_eda`.

## 3. Feature Calculation: State of Health (SoH)

*   **Method:** Calculated SoH as the ratio of current discharge capacity to initial capacity for each battery.
*   **Implementation:**
    *   Found initial capacity (`capacity` from the first discharge cycle) for each `battery_id`.
    *   Calculated `soh = capacity / initial_capacity` for rows corresponding to discharge cycles.
    *   Propagated the cycle-level `soh` value to all measurement rows within that same cycle using `groupby().transform(lambda x: x.ffill().bfill())`.
*   **Verification:** Checked `describe()` for SoH and printed head/tail SoH values per cycle for B0005, confirming the expected decreasing trend (from ~1.0 down to ~0.7).

## 4. Univariate/Bivariate Analysis (Cycle Level)

*   **SoH Degradation Plot:**
    *   Plotted `soh` vs. `cycle_number` for each `battery_id`.
    *   **Findings:** Confirmed clear degradation trend for all batteries; observed different degradation rates (B0005 slowest, B0006/B0018 faster); noted non-linearity ("knee" points) and temporary capacity recovery jumps.
    *   *[Insert Plot: soh_vs_cycle.png]*
*   **Cycle-Level Aggregation:** Created `cycle_agg` DataFrame by grouping `df_eda` by `battery_id` and `cycle_number` (for discharge cycles only) and calculating aggregate statistics (mean voltage, mean/max/delta temp, discharge time).
*   **Correlation Analysis:**
    *   Calculated the correlation matrix for cycle-level aggregated features.
    *   Visualized using a `seaborn` heatmap.
    *   **Findings:**
        *   Strong negative correlation: `soh` vs `cycle_number` (-0.90), `soh` vs `delta_temp_measured` (-0.85), `soh` vs `avg_current_measured` (-0.92).
        *   Strong positive correlation: `soh` vs `avg_voltage_measured` (+0.95), `soh` vs `discharge_time_s` (+0.89).
        *   Identified multicollinearity between temperature features and between discharge time/voltage.
    *   *[Insert Plot: cycle_level_correlation_heatmap.png]*
*   **Implications:** Identified `avg_voltage_measured`, `discharge_time_s`, `avg_current_measured`, `delta_temp_measured` as strong potential predictors. Highlighted the need for features capturing curve shape.

## 5. Time Series Analysis (Intra-Cycle)

*   **Discharge Curve Evolution Plot:**
    *   Plotted smoothed discharge voltage (`voltage_measured_smooth`) vs. relative time for selected cycles representing early, mid, and late life for B0005 (Cycles 10, 316, 568).
    *   **Findings:** Visually confirmed significant changes: shorter discharge time, lower overall voltage profile, steeper plateau slope, and earlier/sharper end-of-discharge voltage drop for lower SoH cycles.
    *   *[Insert Plot: discharge_voltage_curves_comparison.png]*
*   **Implications:** Reinforced the importance of discharge time and voltage levels. Strongly motivated using features that capture curve *shape* (derivatives, ICA/DVA peaks) for better prediction.

## 6. Merging Features

*   Merged the key cycle-level aggregated features (`discharge_time_s`, `delta_temp_measured`) back into the main `df_eda` DataFrame using a left merge on `battery_id` and `cycle_number`. These columns contained values for discharge cycle rows and NaNs otherwise.

## 7. Conclusion of EDA

EDA provided valuable insights into degradation patterns and identified key correlated features. It highlighted the limitations of simple averages and motivated the need for more sophisticated feature engineering or sequence-based modeling approaches to capture the changing dynamics, especially the curve shapes.