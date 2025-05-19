import pandas as pd
import matplotlib.pyplot as plt
import os

# Define the base path where the folders are located
base_path = "C:\\Users\\mihit\\Documents\\NetSim\\Workspaces\\Attack_detection_in_IoT\\Test-Samples"
plots_folder = os.path.join(base_path, "data_sent_plots")

# Create the plots folder if it doesn't exist
os.makedirs(plots_folder, exist_ok=True)

# Iterate over each immediate subfolder in the base path
for subfolder in os.listdir(base_path):
    subfolder_path = os.path.join(base_path, subfolder)

    # Ensure that the item is a valid directory (not a file)
    if not os.path.isdir(subfolder_path):
        print(f"Skipping {subfolder_path}, not a directory.")
        continue

    print(f"Processing subfolder: {subfolder}")

    # Check if 'Packet Trace.csv' exists in the subfolder
    file_path = os.path.join(subfolder_path, 'Packet Trace.csv')
    if not os.path.exists(file_path):
        print(f"'Packet Trace.csv' not found in {subfolder_path}. Skipping...")
        continue

    print(f"'Packet Trace.csv' found in {subfolder_path}. Processing...")

# Load the CSV file
    df = pd.read_csv(file_path, encoding='latin1')

    # Filter PACKET_TYPE to 'Sensing' and STATUS to 'Successful'
    sensing_packets = df[(df['PACKET_TYPE'] == 'Sensing') & (df['PACKET_STATUS'] == 'Successful')]

    # Abbreviate the sensor names
    sensing_packets['SOURCE_ID'] = sensing_packets['SOURCE_ID'].str.replace('SENSOR-', 'S-')
    sensing_packets['RECEIVER_ID'] = sensing_packets['RECEIVER_ID'].str.replace('SENSOR-', 'S-')

    # Exclude non-sensor nodes like SinkNode, Router, and Node
    excluded_nodes = ['SinkNode', 'Router', 'Node']
    sensing_packets = sensing_packets[~sensing_packets['RECEIVER_ID'].isin(excluded_nodes)]

    # Get the list of all sensors present in the data (excluding non-sensor nodes)
    all_sensors_in_data = pd.concat([sensing_packets['SOURCE_ID'], sensing_packets['RECEIVER_ID']]).unique()
    all_sensors_in_data = [sensor for sensor in all_sensors_in_data if sensor.startswith('S-')]

    # Count the packets received by each sensor
    sensor_receive_counts = sensing_packets[sensing_packets['RECEIVER_ID'].str.contains('S-', na=False)]['RECEIVER_ID'].value_counts()

    # Reindex the DataFrame to include all sensors present in the data, filling missing ones with 0
    sensor_receive_counts = sensor_receive_counts.reindex(all_sensors_in_data, fill_value=0)

    # Create a DataFrame for plotting
    combined_counts = pd.DataFrame({
        'Data Packets Received': sensor_receive_counts
    })

    # Plotting
    try:
        fig, ax = plt.subplots(figsize=(15, 8))

        # Create bar plot
        bars = ax.bar(sensor_receive_counts.index, sensor_receive_counts, color='lightgreen')

        # Add count labels on top of the bars
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{int(height)}',
                        (bar.get_x() + bar.get_width() / 2., height),
                        ha='center', va='bottom', fontsize=12, rotation=90, xytext=(0, 5), textcoords='offset points')

        # Customize the plot
        ax.set_title(f'Number of Data Packets Received', fontsize=20)
        ax.set_xlabel('Sensor ID', fontsize=16)
        ax.set_ylabel('Data Packets Received', fontsize=16)
        ax.set_xticks(range(len(sensor_receive_counts.index)))
        ax.set_xticklabels(sensor_receive_counts.index, rotation=45, ha='center', fontsize=12)

        plt.tight_layout()

        # Save the plot in the plots folder with subfolder name
        plot_output_path = os.path.join(plots_folder, f'{subfolder}_data_packets.png')
        plt.savefig(plot_output_path)
        print(f"Plot saved to {plot_output_path}")
        plt.close()

    except Exception as e:
        print(f"Error during plotting: {e}")
