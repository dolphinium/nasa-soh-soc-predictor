import pandas as pd
import os
import numpy as np

def optimize_battery_csv(input_file, output_file):
    """
    Optimize battery CSV file by keeping only necessary columns and removing redundant data.
    """
    print(f"Processing {input_file}...")
    
    # Read the CSV file
    df = pd.read_csv(input_file)
    
    # Filter only discharge cycles
    df = df[df['cycle_type'] == 'discharge'].copy()
    
    # Essential columns to keep (based on actual usage in frontend and backend)
    essential_columns = [
        'cycle_number',
        'measurement_time_relative',  # Used in SEQUENCE_FEATURES
        'voltage_measured_smooth',    # Used in SEQUENCE_FEATURES
        'current_measured_smooth',    # Used in SEQUENCE_FEATURES
        'temperature_measured_smooth', # Used in SEQUENCE_FEATURES
        'soh'                        # Used for visualization/comparison
    ]
    
    # Filter columns that exist in the DataFrame
    columns_to_keep = [col for col in essential_columns if col in df.columns]
    
    # Create optimized DataFrame
    df_optimized = df[columns_to_keep]
    
    # Save optimized DataFrame
    print(f"Saving optimized file to {output_file}")
    print(f"Original size: {len(df)} rows")
    print(f"Original columns: {len(df.columns)}")
    print(f"Optimized columns: {len(df_optimized.columns)}")
    
    df_optimized.to_csv(output_file, index=False)
    
    # Calculate and print size reduction
    original_size = os.path.getsize(input_file) / (1024 * 1024)  # Size in MB
    optimized_size = os.path.getsize(output_file) / (1024 * 1024)  # Size in MB
    reduction = ((original_size - optimized_size) / original_size) * 100
    
    print(f"Original file size: {original_size:.2f} MB")
    print(f"Optimized file size: {optimized_size:.2f} MB")
    print(f"Size reduction: {reduction:.2f}%")
    print("---")

def main():
    data_dir = "app/data/processed_data"
    
    # Files to optimize
    files = [
        "nasa_battery_data_B0005_preprocessed.csv",
        "nasa_battery_data_B0006_preprocessed.csv",
        "nasa_battery_data_B0018_preprocessed.csv"
    ]
    
    # Process each file
    for file in files:
        input_file = os.path.join(data_dir, file)
        output_file = os.path.join(data_dir, f"optimized_{file}")
        
        if os.path.exists(input_file):
            optimize_battery_csv(input_file, output_file)
        else:
            print(f"File not found: {input_file}")

if __name__ == "__main__":
    main() 