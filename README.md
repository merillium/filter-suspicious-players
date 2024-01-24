# filter-suspicious-players

This is a work-in-progress package that retrieves training data from the [lichess.org open database](https://database.lichess.org/), then trains a statistical model to detect suspicious players.

Currently the app is not functional, and has not been deployed. If cloning this repo for personal use, the structure of the python scripts assumes that there is a folder called `lichess-games-database` to which .pgn and .pgn.zst files are downloaded and unzipped(this may be automated in the future using a bash script), and that there is a folder called `lichess_player_data` to which .csv files are saved (this folder is created by `parse_pgn.py` if it doesn't exist)

To be done:
- write unit tests for scripts that perform feature extraction and data labelling
- write a bash script to download and unzip data from the lichess.org open database
- complete data labelling using lichess API calls, with a workaround or retry request if API rate limiting 