from dataclasses import dataclass, field
from typing import Optional, Dict, List
from supervisor.events import EventType


@dataclass
class AppState:
    event: EventType
    goal_id: Optional[int] = None
    meta: Dict = field(default_factory=dict)

    # loop protection
    step_count: int = 0
    max_steps: int = 5

    # v1: decision trace
    decisions: List[str] = field(default_factory=list)
