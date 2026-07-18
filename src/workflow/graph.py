from langgraph.graph import StateGraph, START, END

from src.workflow.state import GraphState
from src.nodes import load_dataset, dataset_understanding, planner, plan_reviewer
from src.workflow.router import review_router

graph = StateGraph(GraphState)

graph.add_node("load_dataset", load_dataset)
graph.add_node("dataset_understanding", dataset_understanding)
graph.add_node("planner", planner)
graph.add_node("plan_reviewer", plan_reviewer)


graph.add_edge(START, "load_dataset")
graph.add_edge("load_dataset", "dataset_understanding")
graph.add_edge("dataset_understanding", "planner")
graph.add_edge("planner", "plan_reviewer")
graph.add_conditional_edges("plan_reviewer", review_router, {"approved": END,"replan": "planner"})
workflow = graph.compile()