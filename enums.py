from enum import Enum

class TimeControl(Enum):
    BULLET = 'bullet'
    BLITZ = 'blitz'
    RAPID = 'rapid'
    CLASSICAL = 'classical'
    ALL = ['bullet', 'blitz', 'rapid', 'classical']

class Folders(Enum):
    MODEL_PLOTS = 'model_plots'
    SAVED_MODELS = 'saved_models'
