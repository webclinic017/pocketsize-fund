import os
import pickle
import shutil
import unittest
import warnings

import keras
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn import preprocessing

from pkg.model import model as model_package

test_data = pd.read_csv("pkg/features/test_data.csv")


class TestPreprocessTrainingFeatures(unittest.TestCase):
    def test_preprocess_training_features_without_mocks_success(self) -> None:
        model = model_package.Model(
            artifact_output_path="",
            weights_and_biases_api_key="",
        )

        result = model.preprocess_training_features(test_data)

        assert isinstance(result, dict)
        assert set(result.keys()) == {"data", "scalers"}

        data_keys = ["training", "validating", "testing"]
        assert set(result["data"].keys()) == set(data_keys)

        assert isinstance(result["scalers"], dict)
        assert len(result["scalers"]) == 2


class TestCreateDataset(unittest.TestCase):
    def test_create_dataset_success(self) -> None:
        model = model_package.Model(
            artifact_output_path="",
            weights_and_biases_api_key="",
        )

        data = np.array(
            object=[
                [1, 2, 3, 4, 5],
                [4, 5, 6, 7, 8],
                [7, 8, 9, 10, 11],
                [10, 11, 12, 13, 14],
                [13, 14, 15, 16, 17],
                [16, 17, 18, 19, 20],
            ],
            dtype=np.float32,
        )

        dataset = model._create_dataset(data)

        assert isinstance(
            dataset,
            tf.data.Dataset,
        )

        for inputs, labels in dataset:
            assert inputs.shape == (32, 5, 3)
            assert labels.shape == (32, 2, 3)

            expected_inputs = data[:, :5, :]
            expected_labels = data[:, 3:5, :]

            np.testing.assert_array_equal(inputs.np(), expected_inputs)
            np.testing.assert_array_equal(labels.np(), expected_labels)


class TestSplitWindow(unittest.TestCase):
    def test_split_window_data_success(self) -> None:
        model = model_package.Model(
            artifact_output_path="",
            weights_and_biases_api_key="",
        )

        model.window_input_length = 3
        model.window_output_length = 2

        data = np.array(
            object=[
                [
                    [1, 2, 3, 4, 5],
                    [3, 4, 5, 6, 7],
                    [5, 6, 7, 8, 9],
                    [7, 8, 9, 10, 11],
                    [9, 10, 11, 12, 13],
                ],
                [
                    [11, 12, 13, 14, 15],
                    [13, 14, 15, 16, 17],
                    [15, 16, 17, 18, 19],
                    [17, 18, 19, 20, 21],
                    [19, 20, 21, 22, 23],
                ],
                [
                    [21, 22, 23, 24, 25],
                    [23, 24, 25, 26, 27],
                    [25, 26, 27, 28, 29],
                    [27, 28, 29, 30, 31],
                    [29, 30, 31, 32, 33],
                ],
            ],
            dtype=np.float32,
        )

        result = model._split_window(data=tf.constant(data))

        inputs, labels = result

        day_count = 3
        feature_count = 5
        label_count = 1

        expected_input_shape = (
            day_count,
            model.window_input_length,
            feature_count,
        )
        expected_labels_shape = (
            day_count,
            model.window_output_length,
            label_count,
        )

        assert inputs.shape.as_list() == list(expected_input_shape)
        assert labels.shape.as_list() == list(expected_labels_shape)

        expected_inputs_values = np.array(
            object=[
                [
                    [1, 2, 3, 4, 5],
                    [3, 4, 5, 6, 7],
                    [5, 6, 7, 8, 9],
                ],
                [
                    [11, 12, 13, 14, 15],
                    [13, 14, 15, 16, 17],
                    [15, 16, 17, 18, 19],
                ],
                [
                    [21, 22, 23, 24, 25],
                    [23, 24, 25, 26, 27],
                    [25, 26, 27, 28, 29],
                ],
            ],
            dtype=np.float32,
        )

        expected_labels_values = np.array(
            object=[
                [
                    [10],
                    [12],
                ],
                [
                    [20],
                    [22],
                ],
                [
                    [30],
                    [32],
                ],
            ],
            dtype=np.float32,
        )

        np.testing.assert_array_equal(
            inputs.np(),
            expected_inputs_values,
        )
        np.testing.assert_array_equal(
            labels.np(),
            expected_labels_values,
        )


class TestCleanAndGroupData(unittest.TestCase):
    def test_clean_and_group_data_success(self) -> None:
        model = model_package.Model(
            artifact_output_path="",
            weights_and_biases_api_key="",
        )

        input = pd.DataFrame(
            {
                "ticker": [
                    "AAPL",
                    "AAPL",
                    "AAPL",
                    "AAPL",
                    "AAPL",
                    "AAPL",
                ],
                "timestamp": [
                    "2024-01-01 16:00:00",
                    "2024-01-02 16:00:00",
                    "2024-01-03 16:00:00",
                    "2024-01-04 16:00:00",
                    "2024-01-05 16:00:00",
                    "2024-01-05 16:00:00",
                ],
                "open_price": [180.0, 182.0, 181.5, 183.0, 182.5, 182.5],
                "high_price": [182.5, 183.5, 183.0, 184.0, 183.5, 183.5],
                "low_price": [179.5, 181.0, 181.0, 182.0, 182.0, 182.0],
                "close_price": [182.0, 182.5, 182.5, 183.5, 183.0, 183.0],
                "volume": [1000, 1500, 1200, 2000, 1800, 1800],
                "source": [
                    "ALPACA",
                    "ALPACA",
                    "ALPACA",
                    "ALPACA",
                    "ALPACA",
                    "ALPACA",
                ],
            },
        )

        output = model._clean_and_group_data(input)

        assert "AAPL" in output
        assert "ticker" not in output["AAPL"].columns
        assert "source" not in output["AAPL"].columns
        assert output["AAPL"].index.isin(["2024-01-05 16:00:00"]).sum() == 1


class TestSaveModel(unittest.TestCase):
    def test_save_model_success(self) -> None:
        model = model_package.Model(
            artifact_output_path=".",
            weights_and_biases_api_key="",
        )

        lstm_model = keras.models.Sequential()

        warnings.filterwarnings("ignore")
        model.save_model(model=lstm_model)
        warnings.resetwarnings()

        file_path = "./lstm.keras"

        assert os.path.exists(file_path)

        os.remove(file_path)


class TestSaveScalers(unittest.TestCase):
    def test_save_scalers_success(self) -> None:
        model = model_package.Model(
            artifact_output_path=".",
            weights_and_biases_api_key="",
        )

        scalers = {
            "AAPL": preprocessing.MinMaxScaler(),
        }

        model.save_scalers(scalers=scalers)

        file_path = "./scalers.pkl"

        assert os.path.exists(file_path)

        os.remove(file_path)


class TestSaveData(unittest.TestCase):
    def test_save_data_success(self) -> None:
        model = model_package.Model(
            artifact_output_path=".",
            weights_and_biases_api_key="",
        )

        model.save_data(
            name="testing_data",
            data=tf.data.Dataset.from_tensor_slices([1, 2, 3]),
        )

        file_path = "./testing_data"

        assert os.path.exists(file_path)

        shutil.rmtree(file_path)


class TestLoadModel(unittest.TestCase):
    def test_load_model_success(self) -> None:
        model = model_package.Model(
            artifact_output_path=".",
            weights_and_biases_api_key="",
        )

        file_path = "./lstm.keras"

        lstm_model = keras.models.Sequential()

        warnings.filterwarnings("ignore")
        lstm_model.save(
            filepath=file_path,
        )
        warnings.resetwarnings()

        model.load_model()

        assert isinstance(model.model, keras.models.Sequential)

        os.remove(file_path)


class TestLoadScalers(unittest.TestCase):
    def test_load_scalers_success(self) -> None:
        model = model_package.Model(
            artifact_output_path=".",
            weights_and_biases_api_key="",
        )

        file_path = "./scalers.pkl"

        scalers = {
            "AAPL": preprocessing.MinMaxScaler(
                feature_range=(0, 1),
            ),
        }

        with open(file_path, "wb") as scalers_file:
            pickle.dump(
                obj=scalers,
                file=scalers_file,
            )

        model.load_scalers()

        assert sorted(list(model.scalers.keys())) == sorted(list(scalers.keys()))

        os.remove(file_path)


class MockPredictor:
    def __init__(self) -> None:
        pass

    def predict(
        self,
        data: any,
    ) -> any:
        return {
            "65": [
                [
                    10.0,
                ],
            ],
        }


class TestGeneratePredictions(unittest.TestCase):
    def test_generate_predictions_success(self) -> None:
        client = model_package.Client(
            model_endpoint_name="model_endpoint_name",
        )

        client.predictor = MockPredictor()

        predictions = client.generate_predictions(
            data=pd.DataFrame(
                data={
                    "timestamp": pd.Timestamp("2021-01-01"),
                },
                index=[0],
            ),
        )

        assert predictions["65"][0][0] == 10.0
