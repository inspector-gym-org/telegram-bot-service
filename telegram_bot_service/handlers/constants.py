from enum import Enum, auto


class MenuState(Enum):
    MAIN_MENU = auto()

    INDIVIDUAL_PLAN_START = auto()
    SEX = auto()
    AGE_GROUP = auto()
    HEALTH_CONDITION = auto()
    GOAL = auto()
    ENVIRONMENT = auto()
    LEVEL = auto()
    FREQUENCY = auto()
    PAYMENT_SCREENSHOT = auto()
