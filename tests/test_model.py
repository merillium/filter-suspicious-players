import copy
import unittest
import pandas as pd
import pytest
from unittest import mock
from model import PlayerAnomalyDetectionModel
from player_account_handler import PlayerAccountHandler


# fixture for sample training data
@pytest.fixture(scope="class")
def get_sample_train_data():
    sample_train_data = pd.DataFrame(
        {
            "player": [f"test_player{i}" for i in range(1, 6 + 1)] * 2,
            "time_control": ["blitz"] * 6 + ["bullet"] * 6,
            "number_of_games": [100] * 12,
            "mean_perf_diff": [0.155, 0.16, 0.17, 0.18, 0.19, 0.25]
            + [0.16, 0.17, 0.18, 0.19, 0.20, 0.26],
            "std_perf_diff": [0.005] * 12,
            "mean_rating": [1510, 1520, 1530, 1540, 1550, 1560]
            + [1510, 1520, 1530, 1540, 1550, 1560],
            "median_rating": [1510, 1520, 1530, 1540, 1550, 1560]
            + [1510, 1520, 1530, 1540, 1550, 1560],
            "std_rating": [10] * 12,
            "mean_opponent_rating": [1510, 1520, 1530, 1540, 1550, 1560]
            + [1510, 1520, 1530, 1540, 1550, 1560],
            "std_opponent_rating": [10] * 12,
            "mean_rating_gain": [1.00, -1.00, 1.00, -1.00, 1.00, -1.00]
            + [1.00, -1.00, 1.00, -1.00, 1.00, -1.00],
            "std_rating_gain": [0.01] * 12,
            "proportion_increment_games": [1.00, 1.00, 1.00, 1.00, 1.00, 1.00]
            + [0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
            "rating_bin": [1500] * 6 + [1600] * 6,
        }
    )

    return sample_train_data


@pytest.mark.usefixtures("get_sample_train_data", "build_training_data")
class TestPlayerAnomalyDetectionModel(unittest.TestCase):
    @mock.patch(
        "player_account_handler.PlayerAccountHandler.update_player_account_status"
    )
    def setUp(self, mock_update_player_account_status):
        player_account_handler = PlayerAccountHandler()
        self.model = PlayerAnomalyDetectionModel(player_account_handler)

    @pytest.fixture(autouse=True)
    def build_training_data(self, get_sample_train_data):
        self.sample_train_data = get_sample_train_data

    def test_fit(self):
        ## this is a workaround to avoid calling get_player_account_status
        self.model._player_account_handler._account_statuses = {
            "test_player1": "open",
            "test_player2": "open",
            "test_player3": "tosViolation",
            "test_player4": "tosViolation",
            "test_player5": "tosViolation",
            "test_player6": "closed",
        }

        ## expected thresholds are 0.16, 0.17
        ## and NOT the 0.15 default initially set within the model
        expected_thresholds = copy.deepcopy(self.model._thresholds)
        expected_thresholds[("blitz", "perf_delta_thresholds")]["1500-1600"] = 0.16
        expected_thresholds[("bullet", "perf_delta_thresholds")]["1600-1700"] = 0.17
        self.model.fit(self.sample_train_data, generate_plots=False)
        assert expected_thresholds == self.model._thresholds

    def test_predict(self):
        pass

    def test_save_model(self):
        pass

    def test_load_model(self):
        pass
