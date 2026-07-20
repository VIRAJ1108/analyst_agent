from src.workflow.graph import workflow
from src.workflow.state import GraphState
from pprint import pprint

def main():

    # Initial Graph State
    state = GraphState(
        user_query="Analyze this dataset and generate meaningful business insights.",
        csv_path="data/sample_superstore.csv"
    )

    final_state = None

    print("=" * 80)
    print("RUNNING WORKFLOW")
    print("=" * 80)

    # Stream execution
    for event in workflow.stream(state):
        pprint(event)
        print("-" * 80)

        # Keep updating final_state
        final_state = list(event.values())[0]

    print("\n")
    print("=" * 80)
    print("FINAL OUTPUTS")
    print("=" * 80)

    print("\n📌 Dataset Summary")
    pprint(final_state.dataset_summary)

    print("\n📌 Analysis Plan")
    pprint(final_state.analysis_plan)

    print("\n📌 Plan Review")
    pprint(final_state.plan_review)

    print("\n📌 Analysis Results")
    pprint(final_state.analysis_results)

    print("\n📌 Business Insights")
    pprint(final_state.business_insights)

    print("\n📌 Visualization Plans")
    pprint(final_state.visualization_plans)

    print("\n📌 Generated Charts")
    pprint(final_state.chart_paths)

    print("\n📌 Final Report")
    pprint(final_state.final_report)

     
   
if __name__ == "__main__":
    main()