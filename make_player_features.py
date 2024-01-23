import requests
import time
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm

FILE_NAME = 'lichess_db_standard_rated_2015-01'

all_player_games_df = pd.read_csv(f'../lichess_player_data/{FILE_NAME}.csv', index_col=[0,1],)
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

## this is used to approximately label players as potentially suspicious or not
## closed account = suspicious
## methods: python-lichess can make API requests
## or beautiful soup may nor may not be able to scrape lichess player pages

## if this is time intensive, consider benchmarks to compare python-lichess vs bs4
def get_player_account_status(
    player_name: str, 
    max_retry_attempts: int = 3,
    min_wait_time: int = 61,
):
    URL = f"https://lichess.org/@/{player_name}"

    ## from lichess api documentation:
    # All requests are rate limited using various strategies, 
    # to ensure the API remains responsive for everyone. 
    # Only make one request at a time. If you receive an HTTP response with a 429 status, 
    # please wait a full minute before resuming API usage.

    page_request_count = 0
    while(page_request_count < max_retry_attempts):
        page = requests.get(URL)
        page_request_count += 1

        if page.status_code == 404:
            return "not found"

        elif page.status_code == 429:
            print(f"Status code 429: waiting {min_wait_time} seconds before retrying {URL}")
            time.sleep(61)
            continue
        else:
            soup = BeautifulSoup(page.content, "html.parser")
            if soup.find("div", class_="is2d").find("p").get_text() == "This account is closed.":
                return "closed"
            else:
                if soup.find("div", class_="warning tos_warning") is None:
                    return "open"
                else:
                    account_status = soup.find_all("div", class_="warning tos_warning")[0].contents[-1]
                    return account_status
    print(f"{max_page_requests} page requests reached for {player_name}")
    return "unknown"

## test this to see how many requests lichess can handle or if the computation time is an issue
## first attempt: 292 before timing out 

all_players = all_player_features.reset_index()['player'].tolist()
account_statuses = []
for p in tqdm(all_players):
    account_statuses.append(get_player_account_status(p))

## add account status to dataframe
all_player_features['account_status'] = account_statuses

## save to csv
all_player_features.to_csv(f'../lichess_player_data/{FILE_NAME}_player_features.csv')