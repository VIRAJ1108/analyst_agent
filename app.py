from src.workflow.graph import workflow
from src.workflow.state import GraphState
from pprint import pprint

def main():

    # Initial Graph State
    state = GraphState(
        user_query="""Analyze the sales performance of the business and identify the key factors affecting revenue and profitability. Suggest the most important analyses
                        needed to generate meaningful business insights.""",
        csv_path="data/sample_superstore.csv"
    )

    # Run Workflow
    for event in workflow.stream(state):
        print(event)
    # result = workflow.invoke(state)


    # print("=" * 80)
    # print("DATASET SUMMARY")
    # print("=" * 80)
    # pprint(result["dataset_summary"].model_dump())

    # print("=" * 80)
    # print("ANALYSIS PLAN")
    # print("=" * 80)

    # for task in result["analysis_plan"].tasks:
    #     print(task.analysis_name)

    # print("=" * 80)
    # print("PLAN REVIEW")
    # print("=" * 80)

    # pprint(result["plan_review"].model_dump())

    # print("=" * 80)
    # print("REVIEW ATTEMPTS")
    # print("=" * 80)

    # print(result["review_attempts"])


if __name__ == "__main__":
    main()