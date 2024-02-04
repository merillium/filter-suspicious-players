import os
import pandas as pd
import chess.pgn

from enums import TimeControl

BASE_FILE_NAME = "lichess_db_standard_rated_2015-01"
PGN_FILE_PATH = f"lichess-games-database/{BASE_FILE_NAME}.pgn"
LICHESS_PLAYER_DATA_FOLDER = "lichess_player_data"

if not os.path.exists(LICHESS_PLAYER_DATA_FOLDER):
    os.mkdir(LICHESS_PLAYER_DATA_FOLDER)

pgn = open(PGN_FILE_PATH)

all_player_info = {}
# dictionary storing player info in the following format:
# {
#     ('player1', 'bullet'): {
#         'ratings': [rating1, rating2, ...],
#         'opponent_ratings': [opp_rating1, opp_rating2, ...],
#         'actual_scores': [score1, score2, ...],
#         'rating_gains': [rating_gain1, rating_gain2, ...]
#         'increments': [increment1, increment2, ...]
#     },
#     ('player1', 'blitz'): {
#         ...
#     },
#     ...
#     ('playerN', 'bullet'): {
#         ...
#     }
# }


def update_all_player_info(
    player: str,
    time_control: str,
    current_rating: float,
    opponent_rating: float,
    score: int,
    rating_gain: float,
    is_increment: int,
    all_player_info: dict = all_player_info,
) -> None:
    # this particular (player, time control) has not been added to all_player_info
    if (all_player_info.get((player, time_control)) is None) & (
        current_rating != 1500.0
    ):
        all_player_info[(player, time_control)] = {
            "ratings": [current_rating],
            "opponent_ratings": [opponent_rating],
            "actual_scores": [score],
            "rating_gains": [rating_gain],
            "increments": [is_increment],
        }

    # exclude a rating of 1500.0 exactly as this could be a first game
    # refine analysis by excluding the first N0 = 10 games if the first rating is 1500.0
    elif (all_player_info.get((player, time_control)) is None) & (
        current_rating == 1500.0
    ):
        pass

    # this particular (player, time control) is already in all_player_info
    # so update or append each field as needed
    else:
        all_player_info[(player, time_control)]["ratings"].append(current_rating)
        all_player_info[(player, time_control)]["opponent_ratings"].append(
            opponent_rating
        )
        all_player_info[(player, time_control)]["actual_scores"].append(score)
        all_player_info[(player, time_control)]["rating_gains"].append(rating_gain)
        all_player_info[(player, time_control)]["increments"].append(is_increment)


number_of_games_parsed = 0
while True:
    game = chess.pgn.read_game(pgn)
    if game is None:
        print(f"{number_of_games_parsed} [valid] games parsed.")
        break

    headers = game.headers

    # get time control
    event = headers["Event"]
    if "bullet" in event.lower():
        time_control = "bullet"
    elif "blitz" in event.lower():
        time_control = "blitz"
    elif "rapid" in event.lower():
        time_control = "rapid"
    elif "classical" in event.lower():
        time_control = "classical"
    else:
        time_control = "other"

    # get info for both players
    white_player, black_player = headers.get("White"), headers.get("Black")
    white_rating, black_rating = headers.get("WhiteElo"), headers.get("BlackElo")
    white_gain, black_gain = headers.get("WhiteRatingDiff"), headers.get(
        "BlackRatingDiff"
    )
    increment = headers["TimeControl"][0]
    result = headers["Result"]

    # skip games with unknown players, ratings, rating difference, or result
    # if either opponent has not played rated games, their rating is 1500
    # but a rating difference is not calculated because this rating is misleading
    # therefore, we will exclude such games
    skip_game_condition = (
        ("?" in white_player)
        | ("?" in black_player)
        | (white_player is None)
        | (black_player is None)
        | ("?" in str(white_rating))
        | ("?" in str(black_rating))
        | (white_gain is None)
        | (black_gain is None)
        | (result not in ["1-0", "0-1", "1/2-1/2"])
    )
    if skip_game_condition:
        continue
    else:
        white_score = 1 if result == "1-0" else 0.5 if result == "1/2-1/2" else 0
        black_score = 0 if result == "1-0" else 0.5 if result == "1/2-1/2" else 1

        ## only convert rating and rating gain to a number once we know it's not None
        white_rating = float(white_rating)
        black_rating = float(black_rating)
        white_gain = float(white_gain)
        black_gain = float(black_gain)

        is_increment = 0 if increment == "0" else 1

        # update white player info
        update_all_player_info(
            player=white_player,
            time_control=time_control,
            current_rating=white_rating,
            opponent_rating=black_rating,
            score=white_score,
            rating_gain=white_gain,
            is_increment=is_increment,
        )

        # update black player info
        update_all_player_info(
            player=black_player,
            time_control=time_control,
            current_rating=black_rating,
            opponent_rating=white_rating,
            score=black_score,
            rating_gain=black_gain,
            is_increment=is_increment,
        )

        number_of_games_parsed += 1
        if number_of_games_parsed % 10000 == 0:
            print(f"{number_of_games_parsed} games parsed...")

# convert to pandas DataFrame
all_player_df = pd.DataFrame.from_dict(
    all_player_info,
    orient="index",
    columns=[
        "ratings",
        "opponent_ratings",
        "actual_scores",
        "rating_gains",
        "increments",
    ],
)

# explode all_player_df to each row corresponds to one game
all_player_games_exploded = all_player_df.explode(
    column=[
        "ratings",
        "opponent_ratings",
        "actual_scores",
        "rating_gains",
        "increments",
    ]
)

# save to csv
all_player_games_exploded.to_csv(f"{LICHESS_PLAYER_DATA_FOLDER}/{BASE_FILE_NAME}.csv")
