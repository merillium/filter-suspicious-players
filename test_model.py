import pandas as pd
from model import PlayerAnomalyDetectionModel

## sample code, this should be refactored into a unit test
    
BASE_FILE_NAME = 'lichess_db_standard_rated_2015-01'
train_data = pd.read_csv(f'lichess_player_data/{BASE_FILE_NAME}_player_features.csv')

## training data: 6 players, 2 time controls
# train_data = pd.DataFrame({
#     'player': [f'player{i}' for i in range(1,6)] + [f'player{i}' for i in range(1,6)],
#     'time_control': ['blitz']*6 + ['bullet']*6,
#     'number_of_games': [100]*12,
#     'mean_perf_diff': [-0.01, 0.01, 0.15, 0.22, 0.24, 0.21] + [-0.40, 0.20, 0.24, -0.10, -0.10, 0.00]
#     'std_perf_diff': [0.005]*12,
#     'mean_rating': [1510, 1520, 1530, 1540, 1550, 1560] + [1510, 1520, 1530, 1540, 1550, 1560],
#     'median_rating': [1510, 1520, 1530, 1540, 1550, 1560] + [1510, 1520, 1530, 1540, 1550, 1560],
#     'std_rating': [10]*12,
#     'mean_opponent_rating': [1510, 1520, 1530, 1540, 1550, 1560] + [1510, 1520, 1530, 1540, 1550, 1560],
#     'std_opponent_rating': [10]*12,
#     'mean_rating_gain': [1.00, -1.00, 1.00, -1.00, 1.00, -1.00] + [1.00, -1.00, 1.00, -1.00, 1.00, -1.00],
#     'std_rating_gain': [0.01]*12,
#     'proportion_increment_games': [1.00, 1.00, 1.00, 1.00, 1.00, 1.00] + [0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
#     'rating_bin': ['1500 - 1600']*6 + ['1500 - 1600']*6,
# })

## we will need to mock the player retreival functions
def test_fit():
    model = PlayerAnomalyDetectionModel()
    pass

def test_predict():
    model = PlayerAnomalyDetectionModel()
    pass

model = PlayerAnomalyDetectionModel()
model.fit(train_data)
model.save_model(f'{BASE_FILE_NAME}_model')
predictions = model.predict(train_data)