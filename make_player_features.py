import lichess.api
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm

BASE_FILE_NAME = 'lichess_db_standard_rated_2015-01'

all_player_games_df = pd.read_csv(f'lichess_player_data/{BASE_FILE_NAME}.csv', index_col=[0,1],)
all_player_games_df.index = all_player_games_df.index.set_names(['player','time_control'])

## filter out users who have not played enough games
MIN_GAMES = 30
all_player_games_filtered_df = all_player_games_df.loc[
    all_player_games_df.groupby(level=['player','time_control']).size() >= MIN_GAMES
].copy()

## calculate how much someone exceeds expectations: (actual win rate - expected win rate)
## someone who has a high win rate could just play mostly lower rated opposition

## this is more involved and requires figuring out expected scores for each game
## e.g. if player 1 is 1500 and player 2 is also 1500, player 1 should have an expected score of 0.5
## but the exact nature of the curve depends on the glicko-2 rating system

## we use will the following paper: http://www.glicko.net/glicko/glicko2.pdf
## and this comment left by @chess_in_sgv:

# Let P2 = Expected outcome for player 2. Then:
# P2 = 1 / (1 + e-A)
# with A = g(sqrt(r12+r22)) * (s2-s1))
# and g(x) = 1/sqrt(1+3x2/pi2)

##  source: https://www.reddit.com/r/chess/comments/i0pnv1/comment/fzrhhwi/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button

def g(x):
    return 1/np.sqrt(1 + 3*x**2/np.pi**2)

def get_player_expected_score(player_rating, opponent_rating, player_rd=80.0, opponent_rd=80.0):
    """Returns expected score of player based on player rating, opponent rating, and RDs (if known)."""
    A = g(np.sqrt(player_rd**2 + opponent_rd**2)) * (player_rating - opponent_rating)
    return 1/(1+np.exp(-A))

all_player_games_filtered_df['expected_scores'] = get_player_expected_score(
    player_rating=all_player_games_filtered_df['ratings'].to_numpy(),
    opponent_rating=all_player_games_filtered_df['opponent_ratings'].to_numpy()
)

## how much better did a player perform than expected?
all_player_games_filtered_df['performance_difference'] = all_player_games_filtered_df['actual_scores'] - all_player_games_filtered_df['expected_scores']

## AGGREGATE GAME RESULTS FEATURES by player + time control
all_player_features = all_player_games_filtered_df.groupby(level=['player','time_control']).agg(
    number_of_games=('ratings','count'),
    mean_perf_diff=('performance_difference', 'mean'), # this takes into account opponent strength
    std_perf_diff=('performance_difference', 'std'), # this takes into account opponent strength
    mean_rating=('ratings', 'mean'),
    median_rating=('ratings', 'median'),
    std_rating=('ratings', 'std'),
    mean_opponent_rating=('opponent_ratings', 'mean'),

    # median_opponent_rating=('opponent_ratings', 'median'), 
    # probably not needed, it's unlikely that opponent ratings will be skewed or provisional

    std_opponent_rating=('opponent_ratings', 'std'),
    mean_rating_gain=('rating_gains', 'mean'),
    std_rating_gain=('rating_gains', 'std'),
    proportion_increment_games=('increments','mean')
)

## some [potentially] useful red flags for suspicious behavior:
# (1) consistently performing above expectation 
# (i.e. mean performance difference far from 0.00 with low standard deviation performance difference)
# we may refine this to drop the low standard deviation performance difference condition
# (2) high correlation between increment and expectation -- not yet implemented
# players who perform much better when playing increment are potentially suspicious
# but there are players who are not that fast with a mouse
# (3) high proportion of losses on time -- not yet implemented
# not conclusive by itself, but certainly supporting evidence
# most players don't want to lose! 
# (4) analysis of move times -- not yet implemented (unknown if such data is available)

min_rating, max_rating = all_player_features['mean_rating'].min(), all_player_features['mean_rating'].max()
min_bin_rating = np.floor(all_player_features['mean_rating'].min() / 100.0) * 100
max_bin_rating = 100 + np.ceil(all_player_features['mean_rating'].max() / 100.0) * 100
rating_bins = np.arange(min_bin_rating, max_bin_rating, 100)

## assign rating bin string to each mean_rating
rating_bin_labels = [f"{str(int(x))} - {str(int(x)+100)}" for x in rating_bins[:-1]]
all_player_features['rating_bin'] = pd.cut(all_player_features['mean_rating'], rating_bins, right=True, labels=rating_bins[:-1]).astype(int)
# all_player_features['rating_bin_label'] = pd.cut(all_player_features['mean_rating'], rating_bins, right=True, labels=rating_bin_labels)

## save to csv
all_player_features.to_csv(f'lichess_player_data/{BASE_FILE_NAME}_player_features.csv')