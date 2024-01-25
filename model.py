from typing import Union
import numpy as np
import pandas as pd
from get_player_labels import get_player_account_status

class PlayerAnomalyDetectionModel:
    """
    The PlayerAnomalyDetectionModel class returns a model with methods:
    .fit to tune the model's internal thresholds on training data
    .predict to make predictions on test data
    """
    def __init__(self):
        self.is_fitted = False
        self._thresholds = {
            'perf_delta_th': {
                f"{rating_bin}-{rating_bin+100}": 0.20 for rating_bin in np.arange(0,4000,100)
            }
        } 
        self._account_statuses = {} # store account statuses for each model instance
        self._ACCOUNT_STATUS_SCORE_MAP = {
            "open": 0,
            "tosViolation": 1,
            "closed": 0.5,
        }

    def fit(self, train_data: pd.DataFrame):
        if self.is_fitted:
            pass 
            # issue a warning that the user is retraining the model! 
            # give the user the option to combine multiple training data sets
        else:
            self.set_thresholds(train_data)
            self.is_fitted = True

    def set_thresholds(self, train_data):
        ## set thresholds by each rating bin, also updates player account statuses
        for rating_bin, train_rating_bin_df in train_data.groupby('rating_bin'):
            rating_bin_key = f"{rating_bin}-{rating_bin+100}"
            print("Setting threshold for rating bin {rating_bin_key}...")
            train_threshold = self._thresholds['perf_delta_th'][rating_bin_key]
            
            ## simple 1D grid search for the best threshold (this can be refined)
            delta_th = 0.01
            best_threshold = train_threshold # defaults to 0.20
            best_accuracy = 0.00
            while(True):
                
                all_flagged_players = train_rating_bin_df[
                    train_rating_bin_df['mean_perf_diff'] > train_threshold
                ]['player'].tolist()

                ## break if threshold is large enough to filter out all players
                if len(all_flagged_players) == 0:
                    break
                
                ## set the account status for each player
                for player in all_flagged_players:
                    if self._account_statuses.get(player) is None:
                        get_player_account_status(player, self._account_statuses)
                    else:
                        pass
                
                ## get the account status for each player
                train_predictions = [
                    self._account_statuses.get(player) for player in all_flagged_players
                ]
                
                ## get the score for each player
                train_scores = [
                    self._ACCOUNT_STATUS_SCORE_MAP.get(status) for status in train_predictions
                ]

                ## calculate accuracy of the model  
                train_accuracy = sum(train_scores) / len(train_predictions) 

                ## update the best threshold
                if train_accuracy > best_accuracy:
                    best_accuracy = train_accuracy
                    best_threshold = train_threshold
                train_threshold += delta_th
            
            print(f"Best threshold for {rating_bin_key} is {best_threshold} with accuracy {best_accuracy}")
            self._thresholds['perf_delta_th'][rating_bin_key] = best_threshold


    def predict(self, test_data: pd.DataFrame):
        """Returns pd.DataFrame or np.array of size k x m
        where k = (player, time_control) are 
        and m = number of features 
        """
        if not self.is_fitted:
            print("Warning: model is not fitted and will use default thresholds")
        
        test_data['is_anomaly'] = test_data.apply(
            lambda row: row['mean_perf_diff'] > self._thresholds['perf_delta_th'][
                f"{row['rating_bin']}-{row['rating_bin']+100}"
            ],
            axis=1
        )
        
        test_data['account_status'] = test_data.apply(
            lambda row: self._account_statuses.get(row['player']),
            axis=1
        )

        predictions = test_data[[
            'player', 'time_control', 'rating_bin', 
            'mean_perf_diff', 'is_anomaly', 'account_status'
        ]]

        return predictions

## sample code, this should be refactored into a unit test
# BASE_FILE_NAME = 'lichess_db_standard_rated_2015-01'
# train_data = pd.read_csv(f'lichess_player_data/{BASE_FILE_NAME}_player_features.csv')
# model = PlayerAnomalyDetectionModel()
# model.fit(train_data)
# predictions = model.predict(train_data)