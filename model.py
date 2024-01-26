import os
import pickle
from typing import Union
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from get_player_labels import get_player_account_status

BASE_FILE_NAME = 'lichess_db_standard_rated_2015-01'
MODEL_PLOTS_FOLDER = 'model_plots'
SAVED_MODELS_FOLDER = 'saved_models'


class PlayerAnomalyDetectionModel:
    """
    The PlayerAnomalyDetectionModel class returns a model with methods:
    .fit to tune the model's internal thresholds on training data
    .predict to make predictions on test data
    .save_model to save the model to a file
    .load_model to load a model from a file
    """
    def __init__(self):
        self.is_fitted = False
        self._thresholds = {
            'perf_delta_th': {
                f"{rating_bin}-{rating_bin+100}": 0.15 for rating_bin in np.arange(0,4000,100)
            }
        } 
        self._account_statuses = {} # store account statuses for each model instance
        self._ACCOUNT_STATUS_SCORE_MAP = {
            "open": 0,
            "tosViolation": 1,
            "closed": 0.75, # weight closed account as closer to a tosViolation
        }
    
    def load_model(self, model_file_name: str):
        """
        Loads a model from a file
        """
        pass

    def fit(self, train_data: pd.DataFrame):
        if self.is_fitted:
            pass 
            # issue a warning that the user is retraining the model! 
            # give the user the option to combine multiple training data sets
        else:
            self._set_thresholds(train_data)
            self.is_fitted = True

    def _set_thresholds(self, train_data, generate_plots=True):
        ## set thresholds by each rating bin, also updates player account statuses
        ## generate plots of threshold vs accuracy
        for rating_bin, train_rating_bin_df in train_data.groupby('rating_bin'):
            rating_bin_key = f"{rating_bin}-{rating_bin+100}"
            train_threshold = self._thresholds['perf_delta_th'][rating_bin_key]
            
            ## simple 1D grid search for the best threshold (this can be refined)
            delta_th = 0.01
            best_threshold = train_threshold # defaults to 0.20
            best_train_metric = 0.00

            train_accuracy_list = []
            train_threshold_list = []
            train_number_of_flagged_players = []

            while(True):
                
                all_flagged_players = train_rating_bin_df[
                    train_rating_bin_df['mean_perf_diff'] > train_threshold
                ]['player'].tolist()

                number_of_flagged_players = len(all_flagged_players)

                ## break if threshold is large enough to filter out all players
                if number_of_flagged_players == 0:
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
                train_accuracy_list.append(train_accuracy)
                train_threshold_list.append(train_threshold)
                train_number_of_flagged_players.append(number_of_flagged_players)

                ## this metric ensures that number of flagged players 
                ## doesn't disproportionately impact the metric:

                ## a threshold that flags 100 players with 0.50 accuracy 
                ## is worse than a threshold that flags 20 players with 1.00 accuracy
                train_metric = np.log(number_of_flagged_players+1) * train_accuracy

                ## update the best threshold
                if train_metric > best_train_metric:
                    best_train_metric = train_metric
                    best_threshold = train_threshold
                train_threshold += delta_th
            
            if generate_plots:
                fig = make_subplots(specs=[[{"secondary_y": True}]])
                fig.add_trace(
                    go.Scatter(
                        x=train_threshold_list,
                        y=train_accuracy_list,
                        name="Accuracy vs Threshold"
                    ), secondary_y=False
                )
                fig.add_trace(
                    go.Scatter(
                        x=train_threshold_list,
                        y=train_number_of_flagged_players,
                        name="Number of Flagged Players"
                    ), secondary_y=True
                )
                fig.add_vline(
                    x=best_threshold,
                    line_width=2,
                    line_dash="dash",
                    line_color="green",
                    annotation_text="Best Threshold"
                )
            fig.update_layout(
                title=f"Accuracy vs Threshold for Rating Bin {rating_bin_key}",
                xaxis_title="Threshold",
                yaxis_title="Accuracy",
                yaxis2_title="Number of Flagged Players",
                yaxis_range=[0, 1]
            )
            if not os.path.exists(MODEL_PLOTS_FOLDER):
                os.mkdir(MODEL_PLOTS_FOLDER)
            fig.write_html(f"{MODEL_PLOTS_FOLDER}/{BASE_FILE_NAME}_model_threshold_{rating_bin_key}.html")

            self._thresholds['perf_delta_th'][rating_bin_key] = best_threshold


    def predict(self, test_data: pd.DataFrame):
        """Returns pd.DataFrame or np.array of size k x m
        where k = (player, time_control) are 
        and m = number of features 
        """
        if not self.is_fitted:
            print("Warning: model is not fitted and will use default thresholds")
        
        predictions = test_data.copy()
        predictions['is_anomaly'] = predictions.apply(
            lambda row: row['mean_perf_diff'] > self._thresholds['perf_delta_th'][
                f"{row['rating_bin']}-{row['rating_bin']+100}"
            ],
            axis=1
        )
        
        predictions['account_status'] = predictions.apply(
            lambda row: self._account_statuses.get(row['player']),
            axis=1
        )

        return predictions
    

    def save_model(
        self, 
        saved_models_folder = SAVED_MODELS_FOLDER, 
        model_name: str = "player_anomaly_detection_model"
    ):
        if not os.path.exists(SAVED_MODELS_FOLDER):
            os.mkdir(SAVED_MODELS_FOLDER)
        with open(f'{SAVED_MODELS_FOLDER}/{BASE_FILE_NAME}_{model_name}.pkl', 'wb') as f:
            pickle.dump(self._thresholds, f)