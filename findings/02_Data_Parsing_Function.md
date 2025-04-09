# Data Parsing Function Development (Notebook 1 -> scripts/data_utils.py)

## 1. Goal

To create a reusable Python function (`parse_nasa_mat_file`) that takes the path to a NASA battery `.mat` file and converts its nested structured data into a flat Pandas DataFrame, suitable for analysis and modeling. Each row in the DataFrame should represent a single time-step measurement within a cycle.

## 2. Initial Implementation (`scripts/data_utils.py` v1)

*   A function was created to loop through cycles and then through measurements within each cycle.
*   It extracted cycle-level info (`cycle_type`, `ambient_temp`) and measurement-level info (`voltage_measured`, `current_measured`, `temperature_measured`, `voltage_charge`, `current_charge`, `time_relative`).
*   An initial attempt was made to extract `capacity`, assuming it was at the cycle level for discharge cycles.
*   Data was collected into a list of dictionaries and converted to a DataFrame.

## 3. Testing and Refinement (Notebook 1)

*   **Test Run (B0005):** The initial test revealed several issues:
    *   Many warnings about missing fields (`Current_charge`, `Voltage_charge`) for discharge cycles.
    *   Many warnings about missing `capacity` field at the cycle level.
    *   The resulting DataFrame only contained 'charge' cycle types, and the 'capacity' column was entirely NaN.
*   **Analysis:**
    *   Discharge cycles used different field names (`Current_load`, `Voltage_load`).
    *   The `capacity` value was located *within* the measurement structure (`measurement_struct`) for discharge cycles, not at the higher cycle level.
    *   Impedance cycles had entirely different fields and were causing errors or being skipped incorrectly.
*   **Code Modification (`scripts/data_utils.py` v2):**
    *   Added logic to check `cycle_type` first.
    *   Defined expected fields based on `cycle_type` (charge vs. discharge).
    *   Used generic column names (`voltage_load_or_charge`, `current_load_or_charge`) in the final DataFrame.
    *   Correctly extracted `capacity` from the `measurement_struct` for discharge cycles.
    *   Explicitly skipped 'impedance' cycles.
    *   Added checks for mismatched array lengths within a cycle.
    *   Improved error handling and warnings.
    *   Code Snippet (Key correction for capacity):
        ```python
        # Inside cycle loop...
        measurement_struct = cycle_struct['data'][0, 0]
        # ... check fields based on type ...
        cycle_capacity_value = np.nan # Default
        if cycle_type == 'discharge' and 'Capacity' in measurement_struct.dtype.names:
             has_capacity = True
             cap_val = measurement_struct['Capacity']
             # Handle potential nesting/scalar extraction
             cycle_capacity_value = cap_val.item() if isinstance(cap_val, np.ndarray) and cap_val.size == 1 else cap_val
             # ... further nesting checks ...
        # ... create measurement_dict with cycle_capacity_value ...
        ```
*   **Re-Testing (B0005):** Required restarting the notebook kernel to reload the modified `data_utils.py`. The second test run was successful:
    *   Both 'charge' and 'discharge' cycles were included.
    *   The 'capacity' column was correctly populated for discharge cycles, showing the expected degradation trend.
    *   Impedance cycles were correctly skipped.
    *   Resulting DataFrame structure was validated (`info()`, `head()`, `tail()`).

## 4. Final Parsing and Combination

*   The validated `parse_nasa_mat_file` function was used to process B0006.mat and B0018.mat.
*   The resulting DataFrames (`df_b0005`, `df_b0006`, `df_b0018`) were concatenated into a single DataFrame `df_all`.
*   This combined DataFrame was saved to `data/processed_data/nasa_battery_data_combined.csv` for use in the next phase.