# Modeling Attempt 2: LSTM on Full Discharge Sequences (Notebook 4)

## 1. Rationale

Based on the failure of models using cycle-level aggregated features, this approach aimed to leverage the detailed time-series information *within* each discharge cycle using a Long Short-Term Memory (LSTM) network.

## 2. Data Preparation (Sequence Format)

*   Loaded the battery-specific preprocessed CSV (e.g., B0005).
*   Split data chronologically (train/val/test) based on cycle number.
*   **Sequence Creation:**
    *   Filtered for discharge cycles with non-NaN `soh`.
    *   Grouped data by cycle.
    *   For each cycle, extracted the sequence of selected features: `voltage_measured_smooth`, `current_measured_smooth`, `temperature_measured_smooth`, `measurement_time_relative`. Stored these sequences in lists (`X_train_list`, etc.).
    *   Extracted the single `soh` value corresponding to each sequence (`y_train_seq`, etc.).
*   **Scaling:**
    *   Stacked all training sequences vertically.
    *   Fit `StandardScaler` on this stacked data.
    *   Applied the fitted scaler to transform each sequence in the train, val, and test lists individually.
*   **Padding:**
    *   Determined the maximum sequence length across all splits.
    *   Used `keras.preprocessing.sequence.pad_sequences` (with `padding='post'`, `value=0.0`) to make all sequences in `X_train_pad`, `X_val_pad`, `X_test_pad` the same length.

## 3. LSTM Model Architecture

*   Used `keras.models.Sequential`.
*   `Masking(mask_value=0.0)`: To ignore the padded zeros during LSTM computation.
*   `LSTM(units=50, activation='tanh')`: Main recurrent layer.
*   `Dropout(0.2)`: For regularization.
*   `Dense(units=1, activation='linear')`: Output layer for SoH regression.
*   Compiled with `optimizer='adam'` and `loss='mean_squared_error'`.

## 4. Initial Training and Evaluation

*   **Training:** Trained using `model.fit` on `X_train_pad`, `y_train_seq`, validating on `X_val_pad`, `y_val_seq`.
*   **Callbacks:** Used `EarlyStopping` (monitoring `val_loss`, `patience=10`) and `ModelCheckpoint` (saving the best model based on `val_loss`).
*   **Results (B0005 - Best Checkpoint Model):**
    *   **Validation:** MAE ~0.0085, RMSE ~0.0108, **R2 Score ~ 0.4604**
    *   **Test:** MAE ~0.0142, RMSE ~0.0159, **R2 Score ~ -2.1966**
    *   **Training History Plot:** Showed decreasing train/validation loss, indicating learning.
    *   **Actual vs. Predicted Plot (Validation):** Showed good correlation, points reasonably close to the ideal line. Much better than RF/XGBoost.
    *   **Actual vs. Predicted Plot (Test):** Showed significant deviation from the ideal line, poor correlation.

## 5. Interpretation

*   The LSTM utilizing full sequences performed **significantly better on the validation set** than models using aggregated features, achieving a positive R2 score and low MAE/RMSE.
*   However, it **still failed to generalize effectively to the test set**, indicated by the negative R2 score. The model struggled to extrapolate accurately into the later stages of degradation not fully represented in the training data range.
*   The gap between the training and test data, bridged only by the validation data (which wasn't used for direct weight updates), was identified as a likely contributor to the poor test performance.