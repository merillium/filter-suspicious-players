import numpy as np
import pandas as pd

## the following model 

class AnomalyDetectionModel:
    """
    The AnomalyDetectionModel class 
    """
    def __init__(self, train_data):
        self.train_data