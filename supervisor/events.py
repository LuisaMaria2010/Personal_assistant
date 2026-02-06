from enum import Enum


class EventType(str, Enum):
    NEW_GOAL = "new_goal"
    DAILY = "daily"
    WEEKLY = "weekly"
