class AppState:
    def __init__(self):
        self.goal = None
        self.current_tasks = []
        self.last_event = None

    def __repr__(self):
        return (
            f"AppState(goal={self.goal}, "
            f"tasks={len(self.current_tasks)}, "
            f"last_event={self.last_event})"
        )
