# Step 10: Modeling Attempt 4 - Final LSTM (Full Sequence, Re-trained on Train+Val) (`4_model_development.ipynb`)

This document details the final SoH modeling step, where the more successful LSTM architecture (using full discharge sequences) was re-trained on combined training and validation data before final evaluation on the test set. This aimed to address the potential issue of the validation data "gap" hindering test set performance.

## 1. Rationale

*   The previous LSTM (Attempt 2) showed good validation performance but poor test performance, potentially due to not learning from the cycles immediately preceding the test set (the validation cycles).
*   Re-training on Train+Val allows the model to learn from a continuous sequence up to the start of the test period, potentially improving extrapolation. This is a standard practice for reporting final test performance after validation/tuning.

## 2. Data Preparation and Model Re-Training

*   **Data:** Combined the padded/scaled training and validation sequences (`X_train_pad`, `y_train_seq` and `X_val_pad`, `y_val_seq`) into `X_train_val_pad`, `y_train_val_seq`.
*   **Model:** Re-initialized the *same* LSTM architecture used in Attempt 2 (Masking -> LSTM(50) -> Dropout(0.2) -> Dense(1)).
*   **Training:** Trained the *new* model instance on the *combined* `X_train_val_pad`, `y_train_val_seq` for a *fixed* number of epochs (`final_epochs = 20`), chosen based on observing where the initial model's validation loss plateaued. Early stopping was not used here as there was no separate validation set.

## 3. Final Evaluation (Test Set Only)

*   The re-trained model (`model_final`) was evaluated *only* on the held-out test set (`X_test_pad`, `y_test_seq`).
*   **Final Test Results (All Batteries):**
    | Battery | Test MAE | Test RMSE | Test R2   |
    | :------ | :------- | :-------- | :-------- |
    | B0005   | 0.0205   | 0.0227    | -5.5426   |
    | B0006   | 0.0405   | 0.0432    | -3.9514   |
    | B0018   | 0.0154   | 0.0174    | -1.3794   |
    *(Note: These final metrics supersede previous test results)*
*   **Final Trend Plots:** Generated plots comparing the full Train+Val actual SoH (red line), Test actual SoH (blue line), and the final model's Test predictions (green dashed line) versus cycle number for each battery.

## 4. Analysis of Final Results

*   **MAE/RMSE:** Achieved the lowest test errors so far (RMSE ~1.0% for B0018, ~2.3% for B0005, ~4.3% for B0006). Re-training helped reduce average error compared to the initially trained LSTM evaluated on the test set.
*   **R2 Score:** Remained **negative** for all batteries on the test set. While the trend tracking improved visually compared to RF/XGBoost, the model still failed to explain the variance in the test data better than a mean prediction.
*   **Trend Plots:** Showed the model capturing the general downward slope but missing fluctuations and exhibiting some offsets. B0006 showed the poorest trend capture in late life.
*   **Overall:** Confirmed that while using full sequences and re-training helps, the fundamental challenge of accurately extrapolating SoH into very late life using only the provided measurements (even smoothed) persists.

## Conclusion

Re-training the sequence-based LSTM on combined training and validation data yielded the lowest test MAE/RMSE but did not resolve the negative R2 score, confirming limitations in generalizing to the final test cycles. This reinforces the recommendation that more advanced feature engineering (like ICA/DVA) is likely required for substantial improvement in late-life SoH prediction accuracy. This LSTM model represents the best performing model developed within the project constraints.