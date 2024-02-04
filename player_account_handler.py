import time
import lichess.api
from lichess.api import ApiHttpError


class PlayerAccountHandler:
    def __init__(self):
        self._account_statuses = {}

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

    def update_player_account_status(self, player):
        if player not in self._account_statuses:
            try:
                user = lichess.api.user(player)
                if user.get("tosViolation"):
                    self._account_statuses[player] = "tosViolation"
                elif user.get("disabled"):
                    self._account_statuses[player] = "closed"
                else:
                    self._account_statuses[player] = "open"
            except ApiHttpError:
                self._account_statuses[player] = "not found"
        else:
            pass
