import time
import multiprocessing
import tqdm
import pandas as pd
import lichess.api
from lichess.api import ApiHttpError
from nordvpn_switcher import initialize_VPN, rotate_VPN, terminate_VPN

BASE_FILE_NAME = 'lichess_db_standard_rated_2015-01'
    
# from lichess api documentation:
# All requests are rate limited using various strategies, 
# to ensure the API remains responsive for everyone. 
# Only make one request at a time. If you receive an HTTP response with a 429 status, 
# please wait a full minute before resuming API usage.

BASE_FILE_NAME = 'lichess_db_standard_rated_2015-01'
all_player_features = pd.read_csv(f'../lichess_player_data/{BASE_FILE_NAME}_player_features.csv')

## get list of all players
all_players = all_player_features.reset_index()['player'].tolist()

## this is used to approximately label players as potentially suspicious or not
## closed = possibly cheating
## tosViolation = cheating or rating manipulation
## open = account in good standing

def get_player_account_status(queue):
    player = queue.get() ## we ensure the player is also the first in the queue (FIFO)
    account_statuses = queue.get()
    
    try:
        ## this will halt indefinitely if our request has hit the lichess API rate limit
        user = lichess.api.user(player_name)
        if user.get('tosViolation'):
            account_statuses[player] = "tosViolation"
        elif user.get('disabled'):
            account_statuses[player] = "closed"
        else:
            account_statuses[player] = "open"
    except ApiHttpError: 
        account_statuses[player] = "not found"


## initialize VPN
initialize_VPN(save=1, area_input=['complete rotation'])




for player in tqdm(all_players):

    ## check if get_player_account_status hangs
    ## create account_statuses dictionary status for each player
    queue = multiprocessing.Queue()
    queue.put(player)
    queue.put(account_statuses)

    p = multiprocessing.Manager().dict()
    p.start()
    p.join()

    ## if if hangs, rotate VPN and try again
    if account_status == "not found":
        rotate_VPN()
        account_status = get_player_account_status(player)

    ## add account status to list
    account_statuses['player'] = account_status

## terminate VPN
    
terminate_VPN()

## add account status to dataframe
all_player_features['account_status'] = account_statuses

## save dataframe
all_player_features.to_csv(f'../lichess_player_data/{BASE_FILE_NAME}_labeled_player_features.csv')