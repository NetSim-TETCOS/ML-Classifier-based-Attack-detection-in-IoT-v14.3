import pandas as pd
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Function to calculate confusion matrix and metrics for a model
def generate_metrics_and_plots(predicted_file, actual_file, classifier_name, cmap):
    # Verify file existence
    if not os.path.exists(predicted_file):
        print(f"Error: Predicted file {predicted_file} not found.")
        return
    if not os.path.exists(actual_file):
        print(f"Error: Actual file {actual_file} not found.")
        return

    # Load data from Excel files
    try:
        predicted_df = pd.read_excel(predicted_file)
        actual_df = pd.read_excel(actual_file)
    except Exception as e:
        print(f"Error loading files for {classifier_name}: {e}")
        return

    # Ensure 'Label' column exists
    if 'Label' not in predicted_df.columns or 'Label' not in actual_df.columns:
        print(f"Error: 'Label' column missing in predicted or actual file for {classifier_name}.")
        return

    # Extract labels
    predicted_labels = predicted_df['Label']
    actual_labels = actual_df['Label']

    # Ensure data alignment
    if len(predicted_labels) != len(actual_labels):
        print(f"Error: Row count mismatch between predicted and actual labels for {classifier_name}.")
        return

    # Calculate confusion matrix and metrics
    try:
        cm = confusion_matrix(actual_labels, predicted_labels)

        # Flatten and rearrange the confusion matrix for old layout format
        cm_flattened = cm.ravel()
        PP, PN, NP, NN = cm_flattened[3], cm_flattened[2], cm_flattened[1], cm_flattened[0]
        cm_rearranged = [[PP, PN],  # First row: Predicted Positive
                         [NP, NN]]  # Second row: Predicted Negative

        # Calculate additional metrics
        accuracy = accuracy_score(actual_labels, predicted_labels)
        precision = precision_score(actual_labels, predicted_labels)
        recall = recall_score(actual_labels, predicted_labels)
        f1 = f1_score(actual_labels, predicted_labels)
    except Exception as e:
        print(f"Error in calculating metrics for {classifier_name}: {e}")
        return

    # Part 1: Generate the Confusion Matrix Image
    try:
        fig_cm, ax_cm = plt.subplots(figsize=(6, 6), dpi=100)

        # Plot confusion matrix with the provided colormap
        sns.heatmap(cm_rearranged, annot=True, fmt='d', cbar=False, ax=ax_cm,
                    cmap=cmap, linewidths=0.5, linecolor='black',
                    annot_kws={"size": 16, "weight": "bold", "color": "black"})

        # Setting labels for axes and title
        ax_cm.set_xlabel('Actual Values', fontsize=16, weight='bold')
        ax_cm.set_ylabel('Predicted Values', fontsize=16, weight='bold')
        ax_cm.set_xticklabels(['Positive', 'Negative'], fontsize=12, weight='bold')
        ax_cm.set_yticklabels(['Positive', 'Negative'], fontsize=12, weight='bold')
        plt.title(f'Confusion Matrix : {classifier_name}', fontsize=18, weight='bold', pad=10)

        # Adjust layout and save figure
        plt.tight_layout()
        output_file_cm = os.path.join(os.getcwd(), f'Confusion_Matrix_{classifier_name}_CustomPalette.png')
        plt.savefig(output_file_cm, bbox_inches='tight', pad_inches=0.2, dpi=150)
        plt.show()
    except Exception as e:
        print(f"Error in generating confusion matrix for {classifier_name}: {e}")
        return

    # Part 2: Generate the Metrics Table Image
    try:
        fig_table, ax_table = plt.subplots(figsize=(6, 4), dpi=100)

        # Table data for metrics
        table_data = [
            ["True Positives (PP)", f"{PP}"],
            ["False Positives (PN)", f"{PN}"],
            ["False Negatives (NP)", f"{NP}"],
            ["True Negatives (NN)", f"{NN}"],
            ["Accuracy", f"{accuracy:.4f}"],
            ["Precision", f"{precision:.4f}"],
            ["Recall", f"{recall:.4f}"],
            ["F1 Score", f"{f1:.4f}"]
        ]

        # Create table
        table = plt.table(cellText=table_data,
                          colLabels=["Metric", "Value"],
                          cellLoc='center', loc='center', bbox=[0.1, 0.1, 0.8, 0.8])

        # Set font size and style
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1.0, 1.0)

        # Hide axes and save table
        ax_table.axis('off')
        output_file_table = os.path.join(os.getcwd(), f'Metrics_Table_{classifier_name}_CustomPalette.png')
        plt.savefig(output_file_table, bbox_inches='tight', pad_inches=0.2, dpi=150)
        plt.show()

        print(f"Confusion matrix plot saved as {output_file_cm}")
        print(f"Metrics table saved as {output_file_table}")
    except Exception as e:
        print(f"Error in generating metrics table for {classifier_name}: {e}")


# Main function to generate confusion matrix and metrics for all models
def main():
    # File paths for predicted labels for all models
    models = {
        "SVM": ("SupportVectorMachine.xlsx", sns.color_palette("Blues")),
        "Naive Bayes": ("NaiveBayes.xlsx", sns.color_palette("Greens")),
        "Logistic Regression": ("LogisticRegression.xlsx", sns.color_palette("Oranges")),
        "KNN": ("K-NearestNeighbour.xlsx", sns.color_palette("Purples"))
    }

    # Path to the actual labels
    actual_file = 'C:\\Users\\mihit\\Desktop\\Attack_detection_in_IoT\\Python Files\\test_data_manual.xlsx'

    # Loop through all models
    for model_name, (predicted_file, cmap) in models.items():
        print(f"Processing metrics for {model_name}...")
        generate_metrics_and_plots(predicted_file, actual_file, model_name, cmap)


# Run the main function
if __name__ == "__main__":
    main()
