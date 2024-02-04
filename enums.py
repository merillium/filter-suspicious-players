from enum import Enum


class TimeControl(Enum):
    """Enum to represent the time control of a chess game."""

    BULLET = "bullet"
    BLITZ = "blitz"
    RAPID = "rapid"
    CLASSICAL = "classical"
    OTHER = "other"
    ALL = ["bullet", "blitz", "rapid", "classical"]


class Folders(Enum):
    """Enum to represent the default folder name(s) in the project."""

    MODEL_PLOTS = "model_plots"
    SAVED_MODELS = "saved_models"
    EXPLORATORY_PLOTS = "exploratory_plots"
