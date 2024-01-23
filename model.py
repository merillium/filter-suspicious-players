from typing import Union
import numpy as np
import pandas as pd


class PlayerAnomalyDetectionModel:
    """
    The PlayerAnomalyDetectionModel class returns a model with methods:
    .fit to tune the model's internal thresholds on training data
    .predict to make predictions on test data
    """
    def __init__(self):
        self._thresholds = None

    ## this should contain some binary search type logic 
    ## to adjust the thresholds based on the feature
    def fit(self, train_data: Union[pd.DataFrame, np.array]):
        self.set_default_thresholds()

    def set_default_thresholds(self):
        pass

    def predict(self, test_data: Union[pd.DataFrame, np.array]):
        """Returns pd.DataFrame or np.array of size k x m
        where k = (player, time_control) are 
        and m = number of features 
        """
        if test_data is None:
            # use a pretrained model
            thresholds = self._thresholds
        else:
            pass