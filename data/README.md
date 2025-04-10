# Data Directory

This directory contains the NASA battery dataset used for SOH and SOC prediction.

## Directory Structure

- `raw_data/`: Contains the original NASA battery dataset files
- `processed_data/`: Contains preprocessed CSV files used for training and analysis

## Large Data Files

Due to GitHub's file size limitations, the following large data files are not included in the repository:

- nasa_battery_data_preprocessed.csv (252.41 MB)
- nasa_battery_data_combined.csv (142.90 MB)
- nasa_battery_data_B0005_preprocessed.csv (101.62 MB)
- nasa_battery_data_B0006_preprocessed.csv (101.26 MB)
- nasa_battery_data_B0018_preprocessed.csv (54.62 MB)

## Getting the Data

To obtain these files:

1. Download the original NASA battery dataset from [NASA's Prognostics Data Repository](https://ti.arc.nasa.gov/tech/dash/groups/pcoe/prognostic-data-repository/#battery)
2. Run the preprocessing scripts in the `scripts/` directory to generate the processed data files
3. Place the generated files in the `data/processed_data/` directory

Alternatively, you can download the preprocessed files from our project's data storage location: [Add your preferred data storage link here]

## Data Storage Recommendations

For large data files, we recommend using one of these solutions:
1. Cloud storage services (Google Drive, Dropbox, etc.)
2. Scientific data repositories (Zenodo, Figshare)
3. Self-hosted storage server
4. AWS S3 or similar cloud storage 