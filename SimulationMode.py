from enum import Enum

class SimulationMode(Enum):
    # Percentage of data disseminated from its own collected data
    K_ZERO = 100
    K_ONE = 75
    K_TWO = 50
    K_TREE = 25
    # K_FOUR = 0