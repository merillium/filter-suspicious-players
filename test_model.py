import pandas as pd
from model import PlayerAnomalyDetectionModel

## sample code, this should be refactored into a unit test
    
BASE_FILE_NAME = 'lichess_db_standard_rated_2015-01'
train_data = pd.read_csv(f'lichess_player_data/{BASE_FILE_NAME}_player_features.csv')
model = PlayerAnomalyDetectionModel()
model.fit(train_data)
model.save(f'{BASE_FILE_NAME}_model')
predictions = model.predict(train_data)