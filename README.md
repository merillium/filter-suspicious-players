# filter-suspicious-players

This is a work-in-progress package that retrieves training data from the [lichess.org open database](https://database.lichess.org/), then trains a statistical model to detect suspicious players.

Currently the app is not functional, and has not been deployed. If cloning this repo for personal use, the structure of the python scripts assumes that there is a folder called `lichess-games-database` to which .pgn and .pgn.zst files are downloaded and unzipped(this may be automated in the future using a bash script), and that there is a folder called `lichess_player_data` to which .csv files are saved (this folder is created by `parse_pgn.py` if it doesn't exist).

### Model Description
This is a simple statistical model that flags players who have performed a certain threshold above their expected performance under the Glicko-2 rating system. The expected performance takes into account all player's complete game history and opponents in the span of the training data. The thresholds are initialized to default values, but are then adjusted separately for each 100 point rating bin in the training data. The metric used to adjust thresholds is the `log(number of players) * accuracy` where `accuracy = number of suspicious players / total number of players`, and `number of suspicious players = 0 * number of players with open accounts + 0.75 * number of players with closed accounts + 1.00 * number of players with a terms of service violation`. The `PlayerAnomalyDetectionModel` class has methods to load pre-defined thresholds, fit the thresholds to training data, generate threshold vs accuracy visualizations (shown below), make predictions on new data, and save the thresholds of the model.

[sample threshold vs accuracy plot](images/sample_model_threshold.png)

### Assumptions
The model is built on the assumption that cheating is a rare occurrence in any training data set on which the model is trained. There may be unexpected behavior if the training data is composed predomininantly of players who are cheating. The model will retain its default thresholds in the event that no players have shown any significant deviations from the mean expected performance in their rating bin. 

### Sample code:
```python
BASE_FILE_NAME = 'lichess_db_standard_rated_2015-01'
train_data = pd.read_csv(f'lichess_player_data/{BASE_FILE_NAME}_player_features.csv')
model = PlayerAnomalyDetectionModel()
model.fit(train_data)
predictions = model.predict(train_data) 
```

To-do:
- write unit tests for scripts that perform feature extraction and data labelling
- write a bash script to download and unzip data from the lichess.org open database
- complete data labelling using lichess API calls, with a workaround or retry request if API rate limiting 
- adjust the accuracy metric for evaluating the models's performance for different thresholds
- write unit tests for `PlayerAnomalyDetectionModel` class and methods