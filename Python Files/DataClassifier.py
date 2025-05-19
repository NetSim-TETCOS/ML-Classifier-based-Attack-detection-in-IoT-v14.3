import pandas as pd
import os
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier

# Function to train and test the classifier
def run_classifier(classifier_name):
    # Paths to training and test data
    train_data_path = 'C:\\Users\\mihit\\Desktop\\Attack_detection_in_IoT\\Training-Samples\\training_data.xlsx'
    test_data_path = "C:\\Users\\mihit\\Desktop\\Attack_detection_in_IoT\\Test-Samples\\test_data.xlsx"

    # Load the training data
    train_df = pd.read_excel(train_data_path)
    X_train = train_df.drop('Label', axis=1)
    y_train = train_df['Label']

    # Load the test data
    test_df = pd.read_excel(test_data_path)

    # Initialize the classifier
    if classifier_name == "SVM":
        clf = SVC(kernel='linear', random_state=42)
        output_file = 'SupportVectorMachine.xlsx'
    elif classifier_name == "Naive Bayes":
        clf = GaussianNB()
        output_file = 'NaiveBayes.xlsx'
    elif classifier_name == "Logistic Regression":
        clf = LogisticRegression(random_state=42, max_iter=1000)
        output_file = 'LogisticRegression.xlsx'
    elif classifier_name == "KNN":
        clf = KNeighborsClassifier(n_neighbors=5)  # Adjust neighbors as needed
        output_file = 'K-NearestNeighbour.xlsx'
    else:
        print("Invalid classifier selected!")
        return

    # Train the classifier
    print(f"Training {classifier_name} classifier...")
    clf.fit(X_train, y_train)

    # Predict the labels for the test data
    print(f"Predicting with {classifier_name} classifier...")
    predictions = clf.predict(test_df)

    # Add the predictions as a new column in the test data DataFrame
    test_df['Label'] = predictions

    # Save the updated DataFrame to a new Excel file
    current_directory = os.getcwd()
    output_file_path = os.path.join(current_directory, output_file)
    test_df.to_excel(output_file_path, index=False)

    print(f"Predictions for {classifier_name} have been saved to {output_file_path}")


# Main function to run all classifiers
def main():
    classifiers = ["SVM", "Naive Bayes", "Logistic Regression", "KNN"]
    
    for classifier_name in classifiers:
        run_classifier(classifier_name)


# Run the main function
if __name__ == "__main__":
    main()
