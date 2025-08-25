import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import GRU, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from app.models import JsonDataset, TestingJsonDataset
import json
from app.constants import app_constants as CONSTANTS
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
from tensorflow.keras.models import load_model
from sklearn.metrics import precision_score, recall_score, f1_score
from app.models import ModelInfo
from datetime import datetime

class GatedRecurrentUnit:

    def __init__(self):
        """ A constructor for GRU. """

        self.normal_datasets = self.get_datasets('Normal')
        self.arrhythmia_datasets = self.get_datasets('Arrhythmia')

    def predict_input_data(self, sequential_data):
        """ A method to feed a sequential data and predict using """

        ensured_int = []
        for rate in sequential_data:
            if isinstance(rate, int):
                print('True')
                ensured_int.append(
                    int(rate)
                )

        sequential_data = ensured_int
        
        model = load_model('gru_model.h5')
        ecg_data = np.array(sequential_data) / CONSTANTS.MAXIMUM_VALUE
        ecg_data = np.expand_dims(ecg_data, axis=-1)  # Reshape for GRU
        ecg_data = np.reshape(ecg_data, (1, 3000,1))
        prediction = model.predict(ecg_data)
        label = "Arrhythmia" if prediction[0][0] > 0.5 else "Normal"

        return label

    def test_predict(self):
        """ Predict validation dataset. """

        result = TestingJsonDataset.objects.all()
        model = load_model('gru_model.h5')

        if len(result) > 0:

            for data in result:
                sequential_data = json.loads(data.sequential_ecg)['rates']
                test_data = np.array(sequential_data) / CONSTANTS.MAXIMUM_VALUE
                test_data = np.expand_dims(test_data, axis=-1)  # Reshape for GRU
                test_data = np.reshape(test_data, (1, 3000,1))
                prediction = model.predict(test_data)
                label = "Arrhythmia" if prediction[0][0] > 0.5 else "Normal"
                TestingJsonDataset.objects.all().filter(id = data.pk).update(answered_remarks = label)


    def save_test_data_to_orm(self, x_test, y_test):
        """ A function to save test data into the ORM. """

        TestingJsonDataset.objects.all().delete()

        for i in range(len(x_test)):
            # Unscale the test data (reverse the scaling)
            unscaled_data = x_test[i] * CONSTANTS.MAXIMUM_VALUE  # Multiply by 650 to restore the original scale

            rates = []

            for each_row in unscaled_data:
                rates.append(int(each_row.tolist()[0]))
                
            data = {
                'sequential_ecg': json.dumps({
                    "rates": rates
                }),  # Convert to JSON format
                'correct_remarks': 'Normal' if y_test[i] == 0 else 'Arrhythmia'  # Optionally, you can add remarks like "Test" to distinguish
            }

            TestingJsonDataset.objects.create(**data)

    def algorithm(self):
        """ Algorithm for training the dataset itself. """
        
        x_data = self.normal_datasets + self.arrhythmia_datasets
        
        # Create corresponding y_data labels (0 for normal, 1 for arrhythmia)
        y_data = [0] * len(self.normal_datasets) + [1] * len(self.arrhythmia_datasets)
        y_data = np.array(y_data)

        # Normalize data (GRU works better with scaled values)
        x_data = np.array(x_data)  # Convert to a numpy array for easy processing
        x_data = x_data / CONSTANTS.MAXIMUM_VALUE  # Scale values between 0 and 1

        # Reshape data for GRU input (samples, timesteps, features)
        x_data = np.expand_dims(x_data, axis=-1)  # Adding feature dimension

        # Split into train and test sets (80% train, 20% test)
        x_train, x_test, y_train, y_test = train_test_split(x_data, y_data, test_size=0.2, random_state=42)
        self.save_test_data_to_orm(x_test, y_test)

        # Build the GRU model
        model = Sequential([
            GRU(128, return_sequences=True, input_shape=(x_train.shape[1], 1)),
            Dropout(0.2),
            GRU(64),
            Dropout(0.2),
            Dense(32, activation='relu'),
            Dropout(0.2),
            Dense(1, activation='sigmoid')  # Single output with sigmoid for binary classification
        ])

        # Compile model
        model.compile(loss='binary_crossentropy', optimizer=Adam(learning_rate=0.001), metrics=['accuracy'])

        # Train the model
        model.fit(x_train, y_train, epochs=10, batch_size=16, validation_data=(x_test, y_test))

        # Evaluate model
        eval_loss, eval_acc = model.evaluate(x_test, y_test)

        # Predict the test set labels
        y_pred = model.predict(x_test)
        y_pred = (y_pred > 0.5).astype(int)  # Convert probabilities to binary labels

        cm = confusion_matrix(y_test, y_pred)

        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)

        print(f"Manual Accuracy: {accuracy:.4f}")
        print(f"Precision: {precision:.4f}")
        print(f"Recall: {recall:.4f}")
        print(f"F1 Score: {f1:.4f}")
        
        model_report = ModelInfo.objects.all()

        if len(model_report) > 0:

            ModelInfo.objects.all().update(last_trained_state = datetime.now(),
                                     accuracy = round(accuracy, 2), 
                                     precision = round(precision, 2), 
                                     recall = round(recall, 2), 
                                     f1_score = round(f1, 2), json_info = json.dumps({}))
        else:

            ModelInfo.objects.create(last_trained_state = datetime.now(),
                                     accuracy = round(accuracy, 2), 
                                     precision = round(precision, 2), 
                                     recall = round(recall, 2), 
                                     f1_score = round(f1, 2), json_info = json.dumps({}))


        # Save the model in .h5 format
        model.save('gru_model.h5')
      
        sample_input = np.random.randint(1, 651, (1, 3000)) / CONSTANTS.MAXIMUM_VALUE  # Normalize
        sample_input = np.expand_dims(sample_input, axis=-1)  # Reshape for GRU
        prediction = model.predict(sample_input)
        label = "Arrhythmia" if prediction[0][0] > 0.5 else "Normal"


    def get_datasets(self, remarks=None,):
        """ An ORM Method to get datasets along with labels. """

        if remarks is None:
            return []

        datasets = []
        result = JsonDataset.objects.all().filter(remarks=remarks)

        for element in result:
            numpy_array = np.array(json.loads(element.sequential_ecg)['rates'])
            datasets.append(numpy_array)

        return datasets  # Repeat the label for each sequence in the dataset
