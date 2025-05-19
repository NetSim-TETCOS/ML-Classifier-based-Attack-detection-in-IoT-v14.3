import pandas as pd
import matplotlib.pyplot as plt
import os

# Define the base path where the folders are located
base_path = "C:\\Users\\mihit\\Documents\\NetSim\\Workspaces\\Attack_detection_in_IoT\\Test-Samples"
plots_folder = os.path.join(base_path, "DAO_sent_rec_plots")

# Create the plots folder if it doesn't exist
os.makedirs(plots_folder, exist_ok=True)

# Iterate over each immediate subfolder in the base path
for subfolder in os.listdir(base_path):
    subfolder_path = os.path.join(base_path, subfolder)

    # Check if it's a directory (immediate subfolder)
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

    # Load the packet trace file
    try:
        df = pd.read_csv(file_path, encoding='latin1')
        print(f"Data loaded successfully from {file_path}")
    except Exception as e:
        print(f"Error loading file {file_path}: {e}")
        continue

    # Verify required columns exist
    required_columns = {'PACKET_TYPE', 'CONTROL_PACKET_TYPE/APP_NAME', 'SOURCE_ID', 'RECEIVER_ID', 'PACKET_STATUS'}
    if not required_columns.issubset(df.columns):
        print(f"Required columns are missing in {file_path}. Skipping...")
        continue

    # Filter for 'Control_Packet' type and 'Successful' status
    control_packets = df[(df['PACKET_TYPE'] == 'Control_Packet') & (df['PACKET_STATUS'] == 'Successful')]

    # Filter DAO messages
    dao_packets = control_packets[control_packets['CONTROL_PACKET_TYPE/APP_NAME'] == 'DAO']

    if dao_packets.empty:
        print(f"No DAO messages found in {file_path}. Skipping...")
        continue

    # Count DAO messages sent by each sensor
    sent_dao = dao_packets[~dao_packets['SOURCE_ID'].str.contains('SINKNODE|ROUTER', case=False)]['SOURCE_ID'].value_counts()

    # Count DAO messages received by each sensor
    received_dao = dao_packets[~dao_packets['RECEIVER_ID'].str.contains('SINKNODE|ROUTER', case=False)]['RECEIVER_ID'].value_counts()

    # Abbreviate sensor names
    sent_dao.index = sent_dao.index.str.replace('SENSOR-', 'S-')
    received_dao.index = received_dao.index.str.replace('SENSOR-', 'S-')

    # Identify malicious nodes based on received DAO messages
    malicious_nodes = received_dao.index.tolist()
    print(f"Malicious nodes detected: {malicious_nodes}")

    # Combine data for plotting
    combined_counts = pd.DataFrame({
        'Sent': sent_dao,
        'Received': received_dao.reindex(sent_dao.index, fill_value=0)
    }).fillna(0)

    if combined_counts.empty:
        print(f"No data available for plotting in {subfolder_path}. Skipping plot...")
        continue

    print(f"Combined counts:\n{combined_counts}")

    # Plotting
    try:
        fig, ax = plt.subplots(figsize=(15, 8))
        bar_width = 0.3
        index = range(len(combined_counts))

        # Plot bars for sent and received messages
        bars_sent = ax.bar(index, combined_counts['Sent'], bar_width, label='DAO Sent', color='skyblue')
        bars_received = ax.bar([i + bar_width * 1.5 for i in index], combined_counts['Received'], bar_width, label='DAO Received', color='lightgreen')

        # Add count labels
        for bar in bars_sent + bars_received:
            height = bar.get_height()
            ax.annotate(f'{int(height)}',
                        (bar.get_x() + bar.get_width() / 2., height),
                        ha='center', va='bottom', fontsize=12, rotation=90, xytext=(0, 5), textcoords='offset points')

        # Customize the plot
        ax.set_title(f'DAO Messages Sent and Received', fontsize=20)
        ax.set_xlabel('Sensor ID', fontsize=16)
        ax.set_ylabel('DAO Messages', fontsize=16)
        ax.set_xticks([i + bar_width * 1.5 / 2 for i in index])
        ax.set_xticklabels(combined_counts.index, rotation=45, ha='center', fontsize=12)

        # Highlight malicious nodes in red
        for label in ax.get_xticklabels():
            if label.get_text() in malicious_nodes:
                label.set_color('red')

        ax.legend(title="Message Type", fontsize=10)

        plt.tight_layout()

        # Save the plot in the plots folder with subfolder name
        plot_output_path = os.path.join(plots_folder, f'{subfolder}.png')
        plt.savefig(plot_output_path)
        print(f"Plot saved to {plot_output_path}")
        plt.close()

    except Exception as e:
        print(f"Error during plotting: {e}")
