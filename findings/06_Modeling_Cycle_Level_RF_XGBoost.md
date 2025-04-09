# Modeling Attempt 1: Cycle-Level RF & XGBoost (Notebook 4)

## 1. Goal

To establish baseline SoH prediction performance using standard tree-based ensemble models (Random Forest and XGBoost) trained on aggregated features at the cycle level. This follows the battery-specific data restructuring.

## 2. Data Preparation (Cycle-Level Aggregation)

*   Loaded the battery-specific preprocessed CSV (e.g., for B0005).
*   Split data chronologically into train/val/test sets based on cycle number for the specific battery.
*   Created cycle-level aggregated DataFrames (`df_train_cycle`, etc.) by grouping the *discharge* cycle data and calculating statistics (mean/min voltage, mean/max/delta temp, discharge time, cycle number).
*   Selected features (`X`) from these aggregated columns and the target (`y`) as the cycle's `soh`.
*   Applied `SimpleImputer` (mean strategy) and `StandardScaler` (fit only on training data) to the features.

## 3. Random Forest Regressor

*   **Model:** `RandomForestRegressor(n_estimators=100, min_samples_split=2, min_samples_leaf=1, oob_score=True, random_state=42)`.
*   **Results (B0005):**
    *   **Validation:** MAE ~0.021, RMSE ~0.025, **R2 Score ~ -1.83**
    *   **Test:** MAE ~0.055, RMSE ~0.056, **R2 Score ~ -39.02**
    *   **OOB Score:** ~0.995
    *   **Feature Importance:** Dominated by `discharge_time_s`, `cycle_number`, `delta_temp_measured`.
    *   **Actual vs. Predicted Plots:** Showed poor correlation on both validation and test; predictions were horizontally clustered, failing to track actual SoH.
*   **Interpretation:** Severe overfitting (high OOB, very poor val/test R2). Model learned training dynamics but failed completely to generalize/extrapolate.

## 4. XGBoost Regressor

*   **Model:** `XGBRegressor(objective='reg:squarederror', n_estimators=100, learning_rate=0.1, max_depth=5, ..., early_stopping_rounds=10)`. Trained with early stopping based on validation set.
*   **Results (B0005):**
    *   **Validation:** MAE ~0.106, RMSE ~0.107, **R2 Score ~ -52.16**
    *   **Test:** MAE ~0.141, RMSE ~0.142, **R2 Score ~ -253.89**
    *   **Feature Importance:** Dominated by `discharge_time_s`, `cycle_number`, `avg_voltage_measured`.
    *   **Actual vs. Predicted Plots:** Showed complete failure; predictions flat and offset.
*   **Interpretation:** Performed even worse than Random Forest. Early stopping triggered very quickly.

## 5. Conclusion for Cycle-Level Approach

*   Using simple aggregated features (mean, max, time duration) per cycle is **insufficient** for accurately predicting SoH, especially for generalization to later cycles.
*   Both RF and XGBoost models **severely overfit** the training data and performed worse than a baseline mean prediction on unseen validation and test data (negative R2 scores).
*   This strongly indicated the need for features that better capture the intra-cycle dynamics or the use of models that can process sequences directly.