# Data Restructuring for Battery-Specific Models (End of Notebook 3)

## 1. Rationale Change

*   Initial modeling plan involved training a single model on data combined from all batteries.
*   Decision was made to pivot to **battery-specific models** for potentially better accuracy, as degradation patterns differed between batteries (observed during EDA).
*   Decision was also made to perform final splitting, scaling, and feature/target preparation within the modeling notebook (`4_model_development.ipynb`) rather than saving complex dictionary structures containing processed splits.

## 2. Skipping Combined Splits/Scaling

*   The code cells previously added in Notebook 3 for creating combined `df_train`/`df_val`/`df_test` dictionaries and battery-specific scaler/imputer dictionaries were removed or commented out.

## 3. Saving Battery-Specific Preprocessed CSVs

*   **Goal:** Save the fully preprocessed DataFrame (`df_eda`, containing cleaned data, smoothed signals, calculated SoH, and merged cycle-level features) into separate CSV files for each battery.
*   **Implementation:**
    *   Added a new cell at the end of Notebook 3.
    *   Looped through unique `battery_id` values in `df_eda`.
    *   For each battery, filtered the DataFrame.
    *   Selected relevant columns (excluding temporary ones).
    *   Saved the battery-specific DataFrame to `data/processed_data/nasa_battery_data_[ID]_preprocessed.csv`.
    ```python
    # Key code snippet for saving
    output_dir = PROCESSED_DATA_DIR
    os.makedirs(output_dir, exist_ok=True)
    batteries = df_eda['battery_id'].unique()
    cols_to_save = [...] # List of final columns

    for battery in batteries:
        df_battery = df_eda[df_eda['battery_id'] == battery][cols_to_save].copy()
        filepath = os.path.join(output_dir, f'nasa_battery_data_{battery}_preprocessed.csv')
        df_battery.to_csv(filepath, index=False)
    ```

## 4. Revised Workflow for Modeling (Notebook 4)

*   The modeling notebook (`4_model_development.ipynb`) would now start by loading *one* of these battery-specific CSV files.
*   All subsequent steps (train/val/test splitting, feature/target selection, NaN imputation, scaling, model training, evaluation) would be performed *within* Notebook 4, specific to the loaded battery.
*   This process would be repeated (potentially by looping or using functions) for each battery (B0005, B0006, B0018).