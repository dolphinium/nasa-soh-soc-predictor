# Modeling Phase Findings: Battery State of Health (SoH) Prediction

This document summarizes the results and findings from the model development phase for predicting State of Health (SoH) for NASA batteries B0005, B0006, and B0018, following the data preprocessing and exploratory data analysis stages. Battery-specific models were developed.

## Starting Point

*   **Data:** Preprocessed CSV files for each battery (`nasa_battery_data_[ID]_preprocessed.csv`) containing time-series measurements, calculated SoH (from discharge capacity), and smoothed measurement signals.
*   **Goal:** Predict SoH for later cycles based on data from earlier cycles.
*   **Split:** Data for each battery was split chronologically into Training (70%), Validation (15%), and Test (15%) sets based on cycle number.

## Approach 1: Random Forest (Cycle-Level Features)

*   **Data Prep:** Discharge data was aggregated to one row per cycle. Features included cycle number, average/min/max smoothed voltage, average current, average/max/delta temperature, and discharge time. Features were scaled using `StandardScaler` (fit on training data).
*   **Target:** SoH value for the cycle.
*   **Results (B0005):**
    *   **Validation:** MAE ~0.021, RMSE ~0.025, **R2 Score ~ -1.83**
    *   **OOB Score:** ~0.995 (Indicating excellent fit on training data samples)
    *   **Feature Importance:** Dominated by `discharge_time_s` (~37%), `cycle_number` (~34%), and `delta_temp_measured` (~17%). Other features had minimal importance.
    *   **Actual vs. Predicted Plot:** Showed poor correlation; predictions were clustered horizontally, failing to track actual SoH variations in the validation set.
*   **Interpretation:** Severe overfitting on the training data dynamics. The model failed to generalize to the unseen validation cycles, indicated by the strongly negative R2 score. The cycle-level aggregated features were likely insufficient.

## Approach 2: XGBoost (Cycle-Level Features)

*   **Data Prep:** Same as Random Forest.
*   **Target:** SoH value for the cycle.
*   **Results (B0005):**
    *   **Validation:** MAE ~0.106, RMSE ~0.107, **R2 Score ~ -52.16**
    *   **Test:** MAE ~0.141, RMSE ~0.142, **R2 Score ~ -253.89**
    *   **Feature Importance:** Dominated by `discharge_time_s` (~45%), `cycle_number` (~33%), and `avg_voltage_measured` (~23%). Other features had zero importance.
    *   **Actual vs. Predicted Plot:** Showed complete failure; predictions were flat and significantly offset from actual values.
*   **Interpretation:** Performed even worse than Random Forest, further confirming that the cycle-level aggregated features were inadequate for generalization with tree-based ensemble models.

## Approach 3: LSTM (Full Discharge Sequence Features) - Initial Training

*   **Data Prep:** Used sequences of smoothed measurements (`voltage_measured_smooth`, `current_measured_smooth`, `temperature_measured_smooth`, `measurement_time_relative`) from *within* each discharge cycle. Sequences were scaled (StandardScaler fit on training sequences) and padded to uniform length.
*   **Target:** Single SoH value for the entire sequence (cycle).
*   **Model:** Simple LSTM (Masking -> LSTM(50) -> Dropout(0.2) -> Dense(1)). Trained with early stopping based on validation loss.
*   **Results (B0005 - Best Checkpoint Model):**
    *   **Validation:** MAE ~0.0085, RMSE ~0.0108, **R2 Score ~ 0.4604**
    *   **Test:** MAE ~0.0142, RMSE ~0.0159, **R2 Score ~ -2.1966**
    *   **Training History Plot:** Showed effective learning with validation loss decreasing significantly.
    *   **Actual vs. Predicted Plot (Validation):** Showed much better correlation than RF/XGBoost, points closer to the ideal line.
    *   **Actual vs. Predicted Plot (Test):** Showed poorer correlation, predictions generally higher than actual values.
*   **Interpretation:** Using the full sequence data significantly improved performance on the *validation* set (positive R2). However, the model *still struggled to generalize and extrapolate* accurately to the later-life cycles in the *test* set (negative R2).

## Approach 4: LSTM (Full Discharge Sequence Features) - Re-trained on Train+Val

*   **Rationale:** To address the potential issue of the "gap" caused by not training on validation data, potentially hindering prediction on the subsequent test data.
*   **Data Prep:** Combined training and validation sequence data. Same sequence features and scaling approach.
*   **Model:** Same LSTM architecture, re-initialized and trained for a fixed number of epochs (20) on the combined data.
*   **Target:** Single SoH value per cycle.
*   **Final Results (Test Set):**
    | Battery | Test MAE | Test RMSE | Test R2   |
    | :------ | :------- | :-------- | :-------- |
    | B0005   | 0.0205   | 0.0227    | -5.5426   |
    | B0006   | 0.0405   | 0.0432    | -3.9514   |
    | B0018   | 0.0154   | 0.0174    | -1.3794   |
    *Note: Slight variations from previous B0005 run due to re-training.*
*   **Final Trend Plot:** Showed the LSTM predictions tracking the general downward trend of the test data better than RF/XGBoost, but failing to capture short-term fluctuations and exhibiting offsets, leading to the negative R2 scores.

## Overall Conclusion (SoH Prediction)

*   Using LSTMs directly on the time-series sequences within discharge cycles yielded significantly better results (lower MAE/RMSE, positive validation R2) than using tree-based models on simple cycle-level aggregated features.
*   The primary challenge identified across all models is **poor generalization and extrapolation to unseen, very late-life cycles** (Test sets), consistently resulting in **negative R2 scores on the test data**.
*   While the final LSTM achieved the lowest MAE/RMSE on the test sets (ranging from ~1.0% to ~4.3% SoH error depending on the battery), its inability to explain the variance (negative R2) indicates it's not reliably capturing the late-stage degradation dynamics based purely on earlier data and the current feature set.

## Future Work & Recommendations

1.  **Advanced Feature Engineering:** Implement features known to be sensitive to degradation mechanisms, primarily **Incremental Capacity Analysis (ICA / dQ/dV)** or Differential Voltage Analysis (DVA). Extract features like peak height, position, area, and width from these curves per cycle. These are likely necessary to improve late-life prediction accuracy.
2.  **LSTM Tuning/Architecture:** Experiment further with the LSTM model: different numbers of layers/units, different optimizers, learning rates, potentially adding attention mechanisms.
3.  **Combine Features:** Try feeding both the raw sequences *and* engineered features (like ICA peaks or cycle number) into the LSTM or other models.
4.  **SoC Prediction:** Address the State of Charge prediction task, which requires calculating ground truth SoC and likely using instantaneous measurements as features in a separate modeling process.

This summary captures the iterative modeling process and the final state of the SoH prediction task based on today's experiments.