from langgraph.graph import StateGraph, START, END

from src.workflow.state import GraphState
from src.nodes import load_dataset, dataset_understanding, planner, plan_reviewer, analyzer, business_insight_generator, chart_generator, report_generator, visualization_planner
from src.workflow.router import review_router

graph = StateGraph(GraphState)

graph.add_node("load_dataset", load_dataset)
graph.add_node("dataset_understanding", dataset_understanding)
graph.add_node("planner", planner)
graph.add_node("plan_reviewer", plan_reviewer)
graph.add_node("analyzer", analyzer)
graph.add_node("business_insight_generator",business_insight_generator)
graph.add_node("visualization_planner",visualization_planner)
graph.add_node("chart_generator", chart_generator)
graph.add_node("report_generator",report_generator)

graph.add_edge(START, "load_dataset")
graph.add_edge("load_dataset", "dataset_understanding")
graph.add_edge("dataset_understanding", "planner")
graph.add_edge("planner", "plan_reviewer")
graph.add_conditional_edges("plan_reviewer",review_router, {"approved": "analyzer","replan": "planner"})
graph.add_edge("analyzer", "business_insight_generator")
graph.add_edge("business_insight_generator","visualization_planner")
graph.add_edge("visualization_planner","chart_generator")
graph.add_edge("chart_generator","report_generator")
graph.add_edge("report_generator", END)

workflow = graph.compile()