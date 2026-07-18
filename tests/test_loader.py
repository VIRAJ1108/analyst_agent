from src.workflow.state import GraphState
from src.nodes import load_dataset


state = GraphState(
    user_query="Analyze employee salaries",
    csv_path="data/agent_sample.csv"
)

updated_state = load_dataset(state)

print(updated_state.dataframe)
print(updated_state.error)