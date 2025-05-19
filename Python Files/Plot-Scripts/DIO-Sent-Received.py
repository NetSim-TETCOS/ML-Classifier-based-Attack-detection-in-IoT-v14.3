import pandas as pd
import matplotlib.pyplot as plt
import os

# Define the base path where the folders are located
base_folder = "C:\\Users\\mihit\\Documents\\NetSim\\Workspaces\\Attack_detection_in_IoT\\Test-Samples"

# Create the plots folder if it doesn't exist
plots_folder = os.path.join(base_folder, "DIO_sent_rec_plots")
os.makedirs(plots_folder, exist_ok=True)

# Iterate over each subfolder in the base path
for subfolder in os.listdir(base_folder):
    subfolder_path = os.path.join(base_folder, subfolder)

    # Ensure it's a directory and contains 'Packet Trace.csv'
    if os.path.isdir(subfolder_path):
        file_path = os.path.join(subfolder_path, 'Packet Trace.csv')

        # Check if 'Packet Trace.csv' exists
        if os.path.exists(file_path):
            print(f"Found 'Packet Trace.csv' in {subfolder_path}. Processing...")

            # Load the packet trace file
            try:
                df = pd.read_csv(file_path, encoding='latin1')

                # Verify required columns exist
                required_columns = {'PACKET_TYPE', 'CONTROL_PACKET_TYPE/APP_NAME', 'SOURCE_ID', 'RECEIVER_ID', 'PACKET_STATUS'}
                if not required_columns.issubset(df.columns):
                    print(f"Required columns are missing in {file_path}. Skipping...")
                    continue

                # Filter for 'Control_Packet' type and 'Successful' status
                control_packets = df[(df['PACKET_TYPE'] == 'Control_Packet') & (df['PACKET_STATUS'] == 'Successful')]

                # Filter DIO messages
                dio_packets = control_packets[control_packets['CONTROL_PACKET_TYPE/APP_NAME'] == 'DIO']

                if dio_packets.empty:
                    print(f"No DIO messages found in {file_path}. Skipping...")
                    continue

                # Count DIO messages sent by each sensor
                sent_dio = dio_packets[~dio_packets['SOURCE_ID'].str.contains('SINKNODE|ROUTER', case=False)]['SOURCE_ID'].value_counts()

                # Count DIO messages received by each sensor
                received_dio = dio_packets[~dio_packets['RECEIVER_ID'].str.contains('SINKNODE|ROUTER', case=False)]['RECEIVER_ID'].value_counts()

                # Abbreviate sensor names
                sent_dio.index = sent_dio.index.str.replace('SENSOR-', 'S-')
                received_dio.index = received_dio.index.str.replace('SENSOR-', 'S-')

                # Identify malicious nodes based on received DIO messages
                malicious_nodes = received_dio.index.tolist()
                print(f"Malicious nodes detected: {malicious_nodes}")

                # Combine the data for plotting
                combined_counts = pd.DataFrame({
                    'Sent': sent_dio,
                    'Received': received_dio.reindex(sent_dio.index, fill_value=0)
                }).fillna(0)

                # Plotting
                fig, ax = plt.subplots(figsize=(15, 8))
                bar_width = 0.3
                index = range(len(combined_counts))

                # Increase spacing between bars to avoid overlap
                bar_spacing = bar_width * 1.5
                
                # Plot bars for sent (Sent) and received (Received) messages
                bars_sent = ax.bar(index, combined_counts['Sent'], bar_width, label='DIO Sent', color='skyblue', edgecolor='none')
                bars_received = ax.bar([i + bar_spacing for i in index], combined_counts['Received'], bar_width, label='DIO Received', color='lightgreen', edgecolor='none')

                # Add count labels on top of the bars with vertical orientation and slight offset
                for bar in bars_sent + bars_received:
                    height = bar.get_height()
                    ax.annotate(f'{int(height)}', 
                                (bar.get_x() + bar.get_width() / 2., height),
                                ha='center', va='bottom', fontsize=12, rotation=90, xytext=(0, 5), textcoords='offset points')

                # Customize the plot
                ax.set_title('Number of DIO Messages Sent and Received', fontsize=32)
                ax.set_xlabel('Sensor ID', fontsize=32)
                ax.set_ylabel('DIO Messages', fontsize=32)
                ax.set_xticks([i + bar_spacing / 2 for i in index])
                ax.set_xticklabels(combined_counts.index, rotation=45, ha='center', va='top', fontsize=14)

                # Highlight specific sensor IDs in red based on malicious nodes
                for label in ax.get_xticklabels():
                    if label.get_text() in malicious_nodes:
                        label.set_color('red')
                
                ax.legend(title="Message Type", fontsize=16)

                plt.tight_layout()

                # Save the plot as an image file in the plots folder
                plot_output_path = os.path.join(plots_folder, f'{subfolder}.png')
                plt.savefig(plot_output_path)
                print(f"Plot saved to {plot_output_path}")
                plt.close()

            except Exception as e:
                print(f"Error processing file {file_path}: {e}")

        else:
            print(f"Skipping {subfolder_path}, 'Packet Trace.csv' not found.")
