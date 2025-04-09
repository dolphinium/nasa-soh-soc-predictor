import scipy.io
import numpy as np
import pandas as pd
import os
from tqdm import tqdm # Optional: for progress bar

def parse_nasa_mat_file(file_path):
    """
    Parses a NASA battery dataset .mat file into a Pandas DataFrame.
    Handles variations in field names between charge and discharge cycles.

    Args:
        file_path (str): The full path to the .mat file.

    Returns:
        pandas.DataFrame: A DataFrame containing the structured time-series data
                          from all cycles in the file, or None if parsing fails.
    """
    try:
        mat_data = scipy.io.loadmat(file_path)
        print(f"Processing file: {os.path.basename(file_path)}")

        battery_id = os.path.basename(file_path).split('.')[0]
        if battery_id not in mat_data:
            print(f"Error: Main key '{battery_id}' not found. Available: {mat_data.keys()}")
            potential_keys = [k for k in mat_data if k.upper() == battery_id.upper() and not k.startswith('__')]
            if not potential_keys: return None
            battery_id = potential_keys[0]
            print(f"Using data key: '{battery_id}'")

        if 'cycle' not in mat_data[battery_id].dtype.names:
            print(f"Error: 'cycle' field not found in '{battery_id}'.")
            return None

        cycle_array = mat_data[battery_id]['cycle'][0, 0]
        num_cycles = cycle_array.shape[1]
        print(f"Found {num_cycles} cycles.")

        all_measurements = []

        for i in tqdm(range(num_cycles), desc=f"Parsing {battery_id}"):
            cycle_struct = cycle_array[0, i]

            cycle_type = cycle_struct['type'][0]
            ambient_temp = cycle_struct['ambient_temperature'][0][0].item() if isinstance(cycle_struct['ambient_temperature'][0], np.ndarray) else cycle_struct['ambient_temperature'][0]
            # cycle_time_epoch = cycle_struct['time'][0][0].item() if isinstance(cycle_struct['time'][0], np.ndarray) else cycle_struct['time'][0] # Less critical for now

            # Check if 'data' field exists for this cycle type
            if 'data' not in cycle_struct.dtype.names:
                 print(f"Warning: 'data' field not found in cycle {i+1} ({cycle_type}) of {battery_id}. Skipping cycle.")
                 continue
            measurement_struct = cycle_struct['data'][0, 0]

            # --- Define expected fields based on cycle type ---
            base_fields = ['Voltage_measured', 'Current_measured', 'Temperature_measured', 'Time']
            charge_specific_fields = ['Current_charge', 'Voltage_charge']
            discharge_specific_fields = ['Current_load', 'Voltage_load', 'Capacity'] # Capacity is often here for discharge

            required_fields = []
            current_input_col, voltage_input_col = None, None # Temp vars for field names
            has_capacity = False

            if cycle_type == 'charge':
                required_fields = base_fields + charge_specific_fields
                current_input_col = 'Current_charge'
                voltage_input_col = 'Voltage_charge'
            elif cycle_type == 'discharge':
                required_fields = base_fields + discharge_specific_fields
                current_input_col = 'Current_load'
                voltage_input_col = 'Voltage_load'
                has_capacity = 'Capacity' in measurement_struct.dtype.names # Check if capacity field exists
            elif cycle_type == 'impedance':
                # Skip impedance measurements for now, or handle separately if needed
                # print(f"Info: Skipping impedance cycle {i+1} of {battery_id}.")
                continue
            else:
                print(f"Warning: Unknown cycle type '{cycle_type}' in cycle {i+1} of {battery_id}. Skipping cycle.")
                continue

            # --- Check if all required fields are present ---
            missing_fields = [f for f in required_fields if f not in measurement_struct.dtype.names]
            # Relax check slightly for Capacity if it's missing but type is discharge
            if cycle_type == 'discharge' and 'Capacity' in missing_fields and len(missing_fields) == 1:
                print(f"Warning: 'Capacity' field missing in discharge cycle {i+1} of {battery_id}. Proceeding without capacity for this cycle.")
                has_capacity = False # Ensure flag is false
                required_fields.remove('Capacity') # Remove from required list for this cycle
                missing_fields = [] # Clear missing fields if only capacity was missing

            if missing_fields:
                print(f"Warning: Missing required fields {missing_fields} for {cycle_type} cycle {i+1} of {battery_id}. Available: {measurement_struct.dtype.names}. Skipping cycle data.")
                continue

            # --- Extract data ---
            voltage_m = measurement_struct['Voltage_measured'].flatten()
            current_m = measurement_struct['Current_measured'].flatten()
            temp_m = measurement_struct['Temperature_measured'].flatten()
            time_rel = measurement_struct['Time'].flatten()
            # Use the correct field names based on cycle type
            current_input = measurement_struct[current_input_col].flatten()
            voltage_input = measurement_struct[voltage_input_col].flatten()

            cycle_capacity_value = np.nan # Default
            if has_capacity:
                # Capacity seems to be scalar within the measurement struct for discharge
                cap_val = measurement_struct['Capacity']
                # Handle potential nesting/scalar extraction
                cycle_capacity_value = cap_val.item() if isinstance(cap_val, np.ndarray) and cap_val.size == 1 else cap_val
                # Sometimes it might be nested further
                if isinstance(cycle_capacity_value, np.ndarray) and cycle_capacity_value.shape == (1,1):
                    cycle_capacity_value = cycle_capacity_value[0,0].item()
                elif isinstance(cycle_capacity_value, np.ndarray) and cycle_capacity_value.size > 1:
                    print(f"Warning: Capacity in cycle {i+1} has unexpected shape {cycle_capacity_value.shape}. Using NaN.")
                    cycle_capacity_value = np.nan


            # --- Length Check ---
            n_measurements = len(time_rel)
            if not all(len(arr) == n_measurements for arr in [voltage_m, current_m, temp_m, current_input, voltage_input]):
                print(f"Warning: Mismatched measurement lengths in cycle {i+1} ({cycle_type}) of {battery_id}. Skipping cycle data.")
                continue

            # --- Create dictionary per measurement ---
            for j in range(n_measurements):
                measurement_dict = {
                    'battery_id': battery_id,
                    'cycle_number': i + 1,
                    'cycle_type': cycle_type,
                    'ambient_temperature': ambient_temp,
                    'measurement_time_relative': time_rel[j],
                    'voltage_measured': voltage_m[j],
                    'current_measured': current_m[j],
                    'temperature_measured': temp_m[j],
                    'voltage_load_or_charge': voltage_input[j], # Renamed generic column
                    'current_load_or_charge': current_input[j], # Renamed generic column
                    'capacity': cycle_capacity_value # Capacity for the whole discharge cycle
                }
                all_measurements.append(measurement_dict)

        if not all_measurements:
            print(f"Warning: No measurements could be extracted from {file_path}.")
            return pd.DataFrame()

        df = pd.DataFrame(all_measurements)
        print(f"Finished processing {battery_id}. DataFrame shape: {df.shape}")
        return df

    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except Exception as e:
        print(f"An error occurred while parsing {file_path}: {e}")
        import traceback
        traceback.print_exc()
        return None