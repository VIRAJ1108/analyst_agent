import pandas as pd
from src.workflow.state import GraphState, DatasetDescription, DatasetSummary, AnalysisPlan, PlanReview
from src.tools.metadata_extractor import extract_metadata
from src.llm.model import llm
from src.llm.prompts import DATASET_DESCRIPTION_PROMPT, PLANNER_PROMPT, PLAN_REVIEW_PROMPT

#Load Dataset Node
def load_dataset(state: GraphState) -> GraphState:
    """
    Loads the dataset from the CSV path provided in the GraphState.
    Updates the dataframe field on success or the error field on failure.
    """

    encodings = ["utf-8", "cp1252","latin1"]

    try:
        dataframe = None

        for encoding in encodings:
            try:
                dataframe = pd.read_csv(state.csv_path,encoding=encoding)
                print(f"✅ Dataset loaded successfully using '{encoding}' encoding.")
                break

            except UnicodeDecodeError:
                continue

        if dataframe is None:
            raise ValueError("Unable to read the CSV file. Unsupported or corrupted file encoding.")

        state.dataframe = dataframe
        state.error = None

    except Exception as e:
        state.dataframe = None
        state.error = str(e)

    return state

#------------------------------------
#Dataset Understanding Node
#------------------------------------

def dataset_understanding(state: GraphState) -> GraphState:
    """
    Generates a high-level understanding of the dataset.
    """
    try:
        metadata = extract_metadata(state.dataframe)

        prompt = DATASET_DESCRIPTION_PROMPT.format(metadata=str(metadata))

        structured_llm = llm.with_structured_output(DatasetDescription)

        response = structured_llm.invoke(prompt)

        dataset_summary = DatasetSummary(
            row_count=metadata["row_count"],
            column_count=metadata["column_count"],
            columns=metadata["columns"],
            data_types=metadata["data_types"],
            numeric_columns=metadata["numeric_columns"],
            categorical_columns=metadata["categorical_columns"],
            missing_values=metadata["missing_values"],
            sample_data=metadata["sample_data"],
            dataset_description=response.description
        )

        state.dataset_summary = dataset_summary
        state.error = None

    except Exception as e:
        state.error = str(e)

    return state

#------------------------------------
#Planner Node
#------------------------------------
def planner(state: GraphState) -> GraphState:
    """
    Generates an analysis plan based on the user's query
    and the dataset summary.
    """
    print("===== Planner Started =====")
    try:

        # Step 1: Build Prompt
        prompt = PLANNER_PROMPT.format(dataset_summary=str(state.dataset_summary),user_query=state.user_query)
        
        # Step 2: Structured LLM
        structured_llm = llm.with_structured_output(AnalysisPlan)

        # Step 3: Generate Plan
        response = structured_llm.invoke(prompt)

        # Step 4: Update State
        state.analysis_plan = response
        state.error = None
        print("===== Planner Finished =====")

    except Exception as e:
        state.error = str(e)

    return state

#------------------------------------
# Plan Reviewer Node
#------------------------------------

def plan_reviewer(state: GraphState) -> GraphState:
    """
    Reviews the generated analysis plan and decides
    whether it is sufficient.
    """

    try:

        prompt = PLAN_REVIEW_PROMPT.format(dataset_summary=str(state.dataset_summary),user_query=state.user_query,
                                           analysis_plan=(str(state.analysis_plan)
                                           if state.analysis_plan
                                            else "No previous analysis plan."),
                                            review_feedback=(state.plan_review.feedback
                                                            if state.plan_review
                                                            else "No previous review.")
                                            )

        structured_llm = llm.with_structured_output(PlanReview)

        response = structured_llm.invoke(prompt)

        state.plan_review = response
        if not response.approved:
            state.review_attempts += 1
        state.error = None
    
    except Exception as e:
        state.error = str(e)

    return state