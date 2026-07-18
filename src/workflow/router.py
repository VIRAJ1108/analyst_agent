from src.workflow.state import GraphState


def review_router(state: GraphState):

    if state.plan_review.approved:
        return "approved"

    if state.review_attempts >= 2:
        return "approved"

    return "replan"