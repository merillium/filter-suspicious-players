import time
import multiprocessing
from tqdm import tqdm
import pandas as pd
import lichess.api
from lichess.api import ApiHttpError

BASE_FILE_NAME = 'lichess_db_standard_rated_2015-01'
    
# from lichess api documentation:
# All requests are rate limited using various strategies, 
# to ensure the API remains responsive for everyone. 
# Only make one request at a time. If you receive an HTTP response with a 429 status, 
# please wait a full minute before resuming API usage.

# BASE_FILE_NAME = 'lichess_db_standard_rated_2015-01'
# all_player_features = pd.read_csv(f'lichess_player_data/{BASE_FILE_NAME}_player_features.csv')

all_players = ['joddle','merillium','LOKI_184','thisplayerdoesnotexist123456','test']
# all_players = ['joddle']

account_statuses = {}

## this is used to approximately label players as potentially suspicious or not
## closed = possibly cheating
## tosViolation = cheating or rating manipulation
## open = account in good standing

def get_player_account_status(player, account_statuses):
    try:
        ## this will halt indefinitely if our request has hit the lichess API rate limit
        user = lichess.api.user(player)
        if user.get('tosViolation'):
            account_statuses[player] = "tosViolation"
        elif user.get('disabled'):
            account_statuses[player] = "closed"
        # elif player == 'test':
        #     time.sleep(10)
        else:
            account_statuses[player] = "open"
    except ApiHttpError: 
        account_statuses[player] = "not found"
    
    # print(f"updated account statuses: {account_statuses}")

# if __name__ == '__main__':
#     with multiprocessing.Manager() as manager:
#         account_statuses = manager.dict()

#         player = 'test'
#         get_player_account_status(player, account_statuses)

#         p = multiprocessing.Process(target=get_player_account_status, args=(player, account_statuses))
#         p.start()
#         p.join(timeout=5)  # Set a timeout for the process to avoid hanging indefinitely

#         if p.is_alive():
#             p.terminate()
#             p.join(5)

#     updated_account_statuses = dict(account_statuses)