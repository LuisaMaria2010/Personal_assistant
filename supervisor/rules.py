def should_replan(critic_output: dict) -> bool:
    """
    Regole dure per decidere se il re-planning è consentito.
    """

    if not critic_output:
        return False

    if critic_output.get("replan_needed") is True:
        return True

    issues = critic_output.get("issues", [])

    high_severity = [
        i for i in issues if i.get("severity") == "high"
    ]

    if len(high_severity) >= 2:
        return True

    return False
