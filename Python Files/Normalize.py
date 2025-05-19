import pandas as pd
import os

# Define the base path where the folders are located
base_path = "C:\\Users\\jace\\Documents\\Attack_detection_in_IoT\\Test-Samples"  # Use the current directory where the script is placed

# Define the paths for the output Excel files
file_with_index = os.path.join(base_path, 'normalized.xlsx')
file_no_index = os.path.join(base_path, 'training_data.xlsx')

# Initialize a list to store normalized and transposed DataFrames
all_transposed_dfs = []

# Iterate over each immediate subfolder in the base path
for subfolder in os.listdir(base_path):
    subfolder_path = os.path.join(base_path, subfolder)

    # Check if it's a directory (immediate subfolder)
    if os.path.isdir(subfolder_path):
        print(f"Processing subfolder: {subfolder}")

        # Define the file path for 'Sensor_Message_Counts.csv' in the subfolder
        file_path = os.path.join(subfolder_path, 'Sensor_Message_Counts.csv')

        # Check if the file exists in the subfolder
        if os.path.exists(file_path):
            try:
                # Load the CSV file into a DataFrame, using the first column as the index
                df = pd.read_csv(file_path, index_col=0)

                # Normalize the DataFrame by dividing each row by its maximum value
                numeric_df = df.apply(pd.to_numeric, errors='coerce')  # Convert to numeric
                max_values = numeric_df.max(axis=1)  # Get max value for each row
                normalized_df = numeric_df.div(max_values, axis=0)  # Normalize rows

                # Handle any rows where max value is 0 or all values are NaN
                normalized_df.fillna(0, inplace=True)

                # Round normalized values to two decimal places
                normalized_df = normalized_df.round(2)

                # Transpose the DataFrame
                transposed_df = normalized_df.T

                # Add a 'Sensor' column with the subfolder name (sensor name) repeated for all rows
                transposed_df.insert(0, 'Sensor', subfolder)

                # Append the transposed DataFrame to the list
                all_transposed_dfs.append(transposed_df)
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")
        else:
            print(f"File {file_path} does not exist. Skipping...")

# Concatenate all normalized and transposed DataFrames
if all_transposed_dfs:
    final_transposed_df = pd.concat(all_transposed_dfs, axis=0)

    # Save the first file with index (retaining row labels like S-1, S-10, etc.)
    with pd.ExcelWriter(file_with_index, engine='xlsxwriter') as writer:
        final_transposed_df.to_excel(writer, index=True, sheet_name='With_Index')

    # Reset the index to remove row labels
    final_transposed_df.reset_index(drop=True, inplace=True)

    # Remove an additional column (e.g., 'Sensor' or another column)
    column_to_remove = 'Sensor'  # Change this to the column you want to remove
    if column_to_remove in final_transposed_df.columns:
        final_transposed_df.drop(columns=[column_to_remove], inplace=True)

    # Save the second file without index and with one column removed
    with pd.ExcelWriter(file_no_index, engine='xlsxwriter') as writer:
        final_transposed_df.to_excel(writer, index=False, sheet_name='No_Index')

    print(f"File with index saved to: {file_with_index}")
    print(f"File without index and with one column removed saved to: {file_no_index}")
else:
    print("No data was processed. Please check the subfolders for valid CSV files.")
