import logging
from supervisor.events import EventType
from supervisor.state import AppState
from supervisor.rules import should_replan


class Supervisor:
    """
    Supervisor con advisory LLM + regole dure.
    """

    def __init__(
        self,
        planner_agent,
        coach_agent,
        memory_agent,
        critic_agent,
        advisor_agent
    ):
        self.planner = planner_agent
        self.coach = coach_agent
        self.memory = memory_agent
        self.critic = critic_agent
        self.advisor = advisor_agent

        logging.basicConfig(level=logging.INFO)

    # -------------------------

    def handle(self, state: AppState):

        if state.step_count >= state.max_steps:
            state.decisions.append("ABORT_MAX_STEPS")
            return None

        state.step_count += 1

        if state.event == EventType.NEW_GOAL:
            return self._handle_new_goal(state)

        if state.event == EventType.DAILY:
            return self._handle_daily(state)

        if state.event == EventType.WEEKLY:
            return self._handle_weekly(state)

    # -------------------------

    def _handle_new_goal(self, state):
        goal_id = self.planner.execute(state.meta["goal_text"])
        state.decisions.append("GOAL_CREATED")

        return self.handle(
            AppState(
                event=EventType.DAILY,
                goal_id=goal_id,
                decisions=state.decisions
            )
        )

    def _handle_daily(self, state):
        result = self.coach.daily_message(state.goal_id)
        state.decisions.append("DAILY_RUN")
        return result

    def _handle_weekly(self, state):

        # 1 memory
        self.memory.weekly_reflection(state.goal_id)

        # 2 critic (LLM)
        critic_output = self.critic.analyze_week(state.goal_id)

        # 3 advisor (LLM consultivo)
        advice = self.advisor.advise(critic_output)

        state.decisions.append(
            f"ADVISOR: suggest={advice['suggest_replan']} "
            f"conf={advice['confidence']}"
        )

        # 4 regole dure + advisory
        hard_rule = should_replan(critic_output)

        if hard_rule and advice["suggest_replan"] and advice["confidence"] > 0.6:
            self.planner.execute_with_feedback(
                goal_id=state.goal_id,
                critic_feedback=critic_output
            )
            state.decisions.append("REPLAN_EXECUTED")
        else:
            state.decisions.append("REPLAN_SKIPPED")

        return {
            "critic": critic_output,
            "advisor": advice,
            "decisions": state.decisions
        }