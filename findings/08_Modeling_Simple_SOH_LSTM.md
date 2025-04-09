# Modeling Attempt 3: Simple LSTM on SOH Sequence (Notebook 4)

## 1. Rationale

Based on a reference notebook found online, this approach attempted a simpler time-series forecast: predicting the next cycle's SoH based *only* on the current cycle's SoH value.

## 2. Data Preparation (SOH Sequence)

*   Used the cycle-level aggregated dataframes (`df_train_cycle`, etc.) created previously for RF/XGBoost.
*   Extracted the `soh` column values for train, val, and test sets.
*   Scaled these 1D SoH arrays using `MinMaxScaler` (fit on training SoH values).
*   **Sequence Creation:** Created input/output pairs where Input = `[Scaled_SOH_n]` and Output = `Scaled_SOH_n+1`, using a `look_back=1`.
*   Reshaped input sequences to `(samples, 1, 1)` for LSTM.

## 3. LSTM Model Architecture

*   Very simple: `LSTM(64)` -> `Dense(1)`.
*   Compiled with `optimizer='adam'` and `loss='mean_squared_error'`.

## 4. Training and Evaluation

*   Trained using `model.fit` on the `SOH_n` -> `SOH_n+1` pairs, validating on the corresponding validation pairs. Used `EarlyStopping`.
*   Predicted on validation and test sequences, then inverse-scaled the predictions and actuals back to the original SoH range using the fitted `MinMaxScaler`.
*   **Results (B0005):**
    *   **Training:** Stopped very early (Epoch 11).
    *   **Validation:** MAE ~0.024, RMSE ~0.027, **R2 Score ~ -2.46**
    *   **Test:** MAE ~0.058, RMSE ~0.058, **R2 Score ~ -42.77**
    *   **Actual vs. Predicted Plot (Test):** Showed predicted SoH as almost flat, completely failing to follow the actual degradation trend.

## 5. Interpretation

*   This extremely simplified approach performed **very poorly**, comparable to the failed RF/XGBoost cycle-level models and much worse than the LSTM using full discharge sequences.
*   Using only the previous SoH value provides insufficient information to predict the next SoH accurately, especially ignoring intra-cycle dynamics and other influential factors like temperature.
*   This attempt confirmed the value of using the richer information present in the full measurement sequences.