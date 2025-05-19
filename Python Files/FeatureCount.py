import pandas as pd
import os

# Define the base path as the current working directory (where the script is located)
base_path = "C:\\Users\\jace\\Documents\\Attack_detection_in_IoT\\Training-Samples"

# Function to count sent and received messages for a given packet type
def count_messages(df, packet_type, control_packet_name):
    # Filter the packets by type and status
    control_packets = df[(df['PACKET_TYPE'] == packet_type) & (df['PACKET_STATUS'] == 'Successful')]

    # Filter for the specific control packet (DAO or DIO)
    specific_packets = control_packets[control_packets['CONTROL_PACKET_TYPE/APP_NAME'] == control_packet_name]

    # Count messages sent by each sensor
    sent_count = specific_packets[~specific_packets['SOURCE_ID'].str.contains('SINKNODE|ROUTER', case=False)]['SOURCE_ID'].str.replace('SENSOR-', 'S-').value_counts()

    # Count messages received by each sensor
    received_count = specific_packets[~specific_packets['RECEIVER_ID'].str.contains('SINKNODE|ROUTER', case=False)]['RECEIVER_ID'].str.replace('SENSOR-', 'S-').value_counts()

    # Combine the counts into a DataFrame
    combined_counts = pd.DataFrame({
        f'{control_packet_name}_Sent': sent_count,
        f'{control_packet_name}_Received': received_count
    }).fillna(0).astype(int)  # Fill NaNs with 0 and convert counts to integers

    return combined_counts

# Function to process first-level subdirectories and handle the 'Packet Trace.csv' files
def process_directories(base_path):
    # Loop through each item in the base directory
    for folder_name in os.listdir(base_path):
        folder_path = os.path.join(base_path, folder_name)

        # Check if it's a directory
        if os.path.isdir(folder_path):
            # Construct the file path for 'Packet Trace.csv'
            file_path = os.path.join(folder_path, 'Packet Trace.csv')

            # Proceed if 'Packet Trace.csv' exists in the folder
            if os.path.exists(file_path):
                # Load the packet trace CSV file
                df = pd.read_csv(file_path, encoding='latin1')

                # Count DAO and DIO messages
                dao_counts = count_messages(df, 'Control_Packet', 'DAO')
                dio_counts = count_messages(df, 'Control_Packet', 'DIO')

                # Combine the counts for DAO and DIO messages
                all_counts = pd.concat([dao_counts, dio_counts], axis=1).fillna(0).astype(int)

                # Filter for Sensing packets
                sensing_packets = df[(df['PACKET_TYPE'] == 'Sensing') & (df['PACKET_STATUS'] == 'Successful')]

                # Abbreviate sensor names for easier handling
                sensing_packets['SOURCE_ID'] = sensing_packets['SOURCE_ID'].str.replace('SENSOR-', 'S-')
                sensing_packets['RECEIVER_ID'] = sensing_packets['RECEIVER_ID'].str.replace('SENSOR-', 'S-')

                # Count how many packets were received by each sensor
                sensor_receive_counts = sensing_packets[sensing_packets['RECEIVER_ID'].str.contains('S-', na=False)]['RECEIVER_ID'].value_counts()

                # Add received packet counts to the result
                all_counts['Packet_Received'] = sensor_receive_counts.reindex(all_counts.index, fill_value=0).astype(int)

                # Sort the DataFrame by sensor IDs
                all_counts = all_counts.sort_index(axis=1)

                # Transpose the DataFrame to match the desired format
                all_counts = all_counts.T

                # Output file path to save the results
                output_file_path = os.path.join(folder_path, 'Sensor_Message_Counts.csv')

                # Save the resulting DataFrame to a CSV file
                all_counts.to_csv(output_file_path)

# Call the function to process the directories
process_directories(base_path)
