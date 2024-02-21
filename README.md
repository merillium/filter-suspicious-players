# filter_suspicious_players

This is a work-in-progress package that retrieves training data from the [lichess.org open database](https://database.lichess.org/), then trains a statistical model to detect suspicious players. Currently the app is not functional, and has not yet been built.

### Data Download and Preprocessing
To download and preprocess data from the lichess.org open database, you can run the following command (specifying the year and month of the data you want to download, and the source of the data to be `lichess-open-database`):

```bash
python3 download_and_preprocess.py --year 2015 --month 1 --source lichess-open-database
```

The `download_and_preprocess.py` script downloads the `.pgn.zst` file corresponding to the month and year specified, decompresses the `.pgn` file, and creates the `lichess_downloaded_games` directory to which both files are saved. Then the script preprocesses the `.pgn` file and extracts relevant features, creates the `lichess_player_data` directory, to which a `.csv` file is saved. By default, all raw files in the `lichess_downloaded_games` directory are then deleted because they are typically large and not needed after preprocessing. (This process can be streamlined by directly reading from the decompressed `.pgn` file instead of first saving it)

### Model Description
This is a simple statistical model that flags players who have performed a certain threshold above their expected performance under the Glicko-2 rating system. The expected performance takes into account each player's complete game history and opponents in the span of the training data. The thresholds are initialized to default values, and then adjusted separately for each 100 point rating bin in the training data.

### Model Training
We define `N` as the number of players who have performed above some threshold, and the estimated number of cheaters as `X = 0.00 * N_open + 0.75 * N_closed + 1.00 * N_violation` where `N_open` is the number of players with open accounts, `N_closed` is the number of players with closed accounts, and `N_violation` is the number of players with a terms of service violation (where `N = N_open + N_closed + N_violation`), the metric used to evaluate the performance of the threshold is the `log(N+1) * X / N`. This is a simple metric intended to reward the model for `high accuracy = X / N` in detecting suspicious players without flagging too many players (observationally, if the threshold is too low, the accuracy will decrease faster than `log(N)`). Note that for a threshold that is too high and flags 0 players, the metric will be 0. This metric may be fine-tuned in the future, but is sufficient for a POC.

Below is an example of the threshold vs accuracy plot below for players in the 1400-1500 range for classical chess based on training data from the month of Jan 2015.

![sample threshold vs accuracy plot](images/sample_model_threshold.png)

### Assumptions
The model is built on the assumption that cheating is a rare occurrence in any data set on which the model is trained. There may be unexpected behavior if the training data is composed predomininantly of players who are cheating. The model will retain its default thresholds in the event that no players have shown any significant deviations from the mean expected performance in their rating bin. 

### Sample code:
```python
import pandas as pd
from player_account_handler import PlayerAccountHandler
from model import PlayerAnomalyDetectionModel

BASE_FILE_NAME = 'lichess_db_standard_rated_2015-01'
train_data = pd.read_csv(f'lichess_player_data/{BASE_FILE_NAME}_player_features.csv')
player_account_handler = PlayerAccountHandler()
model = PlayerAnomalyDetectionModel(player_account_handler)
model.fit(train_data)
model.save_model(f'{BASE_FILE_NAME}_model')
predictions = model.predict(train_data)
```

### Unit Tests
Currently working on unit tests, which can be run with the following command:
```make test```, or if you want to run test files individually ```PYTHONPATH=. pytest tests/test_model.py```

To-do:
- implement progress bars for preprocessing data and model training
- complete data labelling using lichess API calls, with a workaround or retry request if API rate limiting occurs 
- write unit tests for scripts that perform feature extraction and data labelling
- complete unit tests for `PlayerAnomalyDetectionModel` class and methods (in-progress)
- possible benchmarks for length of time to execute data downloading, preprocessing, and model training depending on the size of the raw data