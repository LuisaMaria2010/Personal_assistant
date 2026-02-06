from tools.feedback_tools import save_user_feedback

def run_tests():
    save_user_feedback(
        goal_id=1,
        task_id=1,
        feedback={
            "done": True,
            "difficulty": 3,
            "energy": 4,
            "note": "Un po' stanco"
        }
    )

    print("✅ feedback_tools tests passed")

if __name__ == "__main__":
    run_tests()
