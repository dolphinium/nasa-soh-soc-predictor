# Modeling Phase Findings: Battery State of Health (SoH) Prediction Summary

This document summarizes the results and findings from the model development phase for predicting State of Health (SoH) for NASA batteries B0005, B0006, and B0018, following the data preprocessing and exploratory data analysis stages. Battery-specific models were developed.

## Modeling Approaches Investigated

1.  **Cycle-Level Features (RF & XGBoost):** Aggregated features (mean voltage, discharge time, temp delta, etc.) per cycle. Models (Random Forest, XGBoost) severely overfit training data and failed to generalize (Negative R2 scores on validation/test). Feature importances were dominated by a few features like discharge time and cycle number. **Conclusion: Insufficient feature representation.**
2.  **LSTM on Full Discharge Sequences (Initial Train):** Used padded sequences of smoothed voltage, current, temperature, and time within each discharge cycle. Trained with early stopping based on validation data. **Results:** Showed significant improvement on the *validation* set (Positive R2 ~0.46, MAE/RMSE ~0.8-1.1% for B0005) but still performed poorly on the *test* set (Negative R2 ~ -2.2 for B0005), indicating difficulty extrapolating to late-life cycles.
3.  **LSTM on SoH Sequence (Simple Approach):** Predicted SoH based only on the previous cycle's SoH. **Results:** Performed very poorly (Negative R2 on validation and test), confirming this approach ignores critical information.
4.  **LSTM on Full Discharge Sequences (Re-trained on Train+Val):** Re-trained the architecture from Attempt 2 on combined training and validation data to provide the model with data continuity leading up to the test set. **Results:** Achieved the lowest **Test MAE/RMSE** (B0005: ~2.0%/2.3%, B0006: ~4.0%/4.3%, B0018: ~1.5%/1.7%), and trend plots showed better tracking of the general degradation slope compared to RF/XGBoost. However, the **Test R2 scores remained negative** for all batteries (B0005: -5.5, B0006: -4.0, B0018: -1.4), indicating the model still struggled to capture the variance and specific dynamics of late-life degradation.

## Overall Conclusion (SoH Prediction)

*   Using LSTMs directly on the time-series sequences within discharge cycles yielded significantly better results (lower MAE/RMSE, positive validation R2) than using tree-based models on simple cycle-level aggregated features.
*   The primary challenge identified across all models is **poor generalization and extrapolation to unseen, very late-life cycles** (Test sets), consistently resulting in **negative R2 scores on the test data**.
*   While the final LSTM achieved the lowest MAE/RMSE on the test sets, its inability to explain the variance (negative R2) indicates it's not reliably capturing the late-stage degradation dynamics based purely on earlier data and the current feature set.

## Future Work & Recommendations

1.  **Advanced Feature Engineering:** Implement features known to be sensitive to degradation mechanisms, primarily **Incremental Capacity Analysis (ICA / dQ/dV)** or Differential Voltage Analysis (DVA). Extract features like peak height, position, area, and width from these curves per cycle. These are likely necessary to improve late-life prediction accuracy.
2.  **LSTM Tuning/Architecture:** Experiment further with the LSTM model: different numbers of layers/units, different optimizers, learning rates, potentially adding attention mechanisms.
3.  **Combine Features:** Try feeding both the raw sequences *and* engineered features (like ICA peaks or cycle number) into the LSTM or other models.
4.  **SoC Prediction:** Address the State of Charge prediction task, which requires calculating ground truth SoC and likely using instantaneous measurements as features in a separate modeling process (deferred due to time constraints).