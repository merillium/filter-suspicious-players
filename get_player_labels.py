import time
import multiprocessing
from tqdm import tqdm
import pandas as pd
import lichess.api
from lichess.api import ApiHttpError

BASE_FILE_NAME = 'lichess_db_standard_rated_2015-01'
    


def get_player_account_status(player, account_statuses):
    """This function sends an API request to lichess to get the account status
    of the player passed in as an argument, and updates the account_statuses
    dictionary with the result.

    'closed' = possibly cheating
    'tosViolation' = cheating or rating manipulation
    'open' = account in good standing
    'not found' = account does not exist (this should not happen)

    Note:

    From lichess api documentation:
    All requests are rate limited using various strategies, 
    to ensure the API remains responsive for everyone. 
    Only make one request at a time. If you receive an HTTP response with a 429 status, 
    please wait a full minute before resuming API usage.
    """
    
    try:
        ## this will halt indefinitely if our request has hit the lichess API rate limit
        time.sleep(0.01)
        user = lichess.api.user(player)
        if user.get('tosViolation'):
            account_statuses[player] = "tosViolation"
        elif user.get('disabled'):
            account_statuses[player] = "closed"
        else:
            account_statuses[player] = "open"
    except ApiHttpError: 
        account_statuses[player] = "not found"
