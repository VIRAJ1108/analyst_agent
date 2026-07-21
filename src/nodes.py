import os
import pandas as pd
from src.workflow.state import GraphState, DatasetDescription, DatasetSummary, AnalysisPlan, PlanReview, AnalysisResult, AnalysisResults, BusinessInsights, VisualizationPlans, Report
from src.tools.metadata_extractor import extract_metadata
from src.llm.model import llm
from src.llm.prompts import DATASET_DESCRIPTION_PROMPT, PLANNER_PROMPT, PLAN_REVIEW_PROMPT, BUSINESS_INSIGHT_PROMPT, REPORT_GENERATOR_PROMPT, VISUALIZATION_PLANNER_PROMPT
from src.chart_utils import generate_bar_chart, generate_line_chart, generate_pie_chart, generate_scatter_chart

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

    try:

        review_feedback = ""

        if state.plan_review:
            review_feedback = state.plan_review.feedback

        # Step 1: Build Prompt
        prompt = PLANNER_PROMPT.format(dataset_summary=str(state.dataset_summary),user_query=state.user_query, review_feedback=review_feedback)
        
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
        prompt = PLAN_REVIEW_PROMPT.format(
            dataset_summary=str(state.dataset_summary),
            user_query=state.user_query,
            analysis_plan=(
                str(state.analysis_plan)
                if state.analysis_plan
                else "No previous analysis plan."
            ),
            review_feedback=(
                state.plan_review.feedback
                if state.plan_review
                else "No previous review."
            )
        )

        structured_llm = llm.with_structured_output(PlanReview)
        response = structured_llm.invoke(prompt)

        print("LLM Response:")
        print(response)

        state.plan_review = response

        if not response.approved:
            state.review_attempts += 1

        state.error = None

        print("Reviewer State ID:", id(state))
        print("Analysis Plan:", state.analysis_plan)
        print("Plan Review:", state.plan_review)

        return state

    except Exception as e:

        print(e)
        raise


#------------------------------------
# ANALYZER NODES
#------------------------------------

def group_analysis(df, task):
    group_column = task.required_columns[0]
    metric_column = task.required_columns[1]

    grouped_result = (
        df.groupby(group_column)[metric_column].sum().to_dict()
    )

    return AnalysisResult(
        analysis_name=task.analysis_name,
        summary=f"Grouped {metric_column} by {group_column}.",
        result=grouped_result
    )


def trend_analysis(df, task):
    date_column = task.required_columns[0]
    metric_column = task.required_columns[1]

    trend_df = df.copy()
    trend_df[date_column] = pd.to_datetime(trend_df[date_column])
    trend_df["Month"] = (trend_df[date_column].dt.to_period("M").astype(str))

    trend_result = (trend_df.groupby("Month")[metric_column].sum().to_dict())

    return AnalysisResult(
        analysis_name=task.analysis_name,
        result=trend_result,
        summary=f"Analyzed the trend of {metric_column} over time.",
    )


def correlation_analysis(df, task):
    columns = task.required_columns
    numeric_columns = df[columns].select_dtypes(include="number").columns.tolist()

    if len(numeric_columns) < 2:
        return AnalysisResult(
            analysis_name=task.analysis_name,
            result={},
            summary="Correlation analysis requires at least two numeric columns."
        )
    
    correlation_result = (df[numeric_columns].corr().to_dict())

    return AnalysisResult(
        analysis_name=task.analysis_name,
        result=correlation_result,
        summary=f"Computed correlation among {', '.join(numeric_columns)}."
    )

def distribution_analysis(df, task):
    column = task.required_columns[0]

    distribution_result = (df[column].describe().to_dict())

    return AnalysisResult(
        analysis_name=task.analysis_name,
        result=distribution_result,
        summary=f"Computed distribution statistics for {column}."
    )


def ranking_analysis(df, task):
    group_column = task.required_columns[0]
    metric_column = task.required_columns[1]

    ranked_result = (df.groupby(group_column)[metric_column].sum().sort_values(ascending=False))
    TOP_K = 10
    if len(ranked_result) <= 20:
        result = ranked_result.to_dict()
    else:
        result = {
        "top_performers": ranked_result.head(TOP_K).to_dict(),
        "bottom_performers": ranked_result.tail(TOP_K).to_dict()
        }

    return AnalysisResult(
        analysis_name=task.analysis_name,
        summary=f"Ranked {group_column} based on total {metric_column}.",
        result=result
    )

analysis_registry = {
    "group_analysis": group_analysis,
    "trend_analysis": trend_analysis,
    "correlation_analysis": correlation_analysis,
    "distribution_analysis": distribution_analysis,
    "ranking_analysis": ranking_analysis
}

def analyzer(state):
    print("Analyzer id:", id(state))
    print("Analyzer analysis_plan:", state.analysis_plan)

    df = state.dataframe
    plan = state.analysis_plan
    results = []

    for task in plan.tasks:

        function = analysis_registry.get(task.pattern)

        result = function(df, task)

        results.append(result)

    state.analysis_results = AnalysisResults(
        analyses=results
    )

    return state

#------------------------------------
# BUSINESS INSIGHTS NODE
#------------------------------------
def business_insight_generator(state: GraphState) -> GraphState:
    """
    Converts analytical findings into business insights.
    """

    print("===== Business Insight Generator Started =====")

    try:
        analysis_text = ""
        for analysis in state.analysis_results.analyses:
            analysis_text += f"""
            Analysis: {analysis.analysis_name}
            Summary:{analysis.summary}"""


        prompt = BUSINESS_INSIGHT_PROMPT.format(
            dataset_summary=str(state.dataset_summary),
            user_query=state.user_query,
            # analysis_results=str(state.analysis_results)
            analysis_results = analysis_text
        )

        structured_llm = llm.with_structured_output(BusinessInsights)

        response = structured_llm.invoke(prompt)

        state.business_insights = response
        state.error = None

        print("===== Business Insight Generator Finished =====")
        print(response)

        return state

    except Exception as e:
        print("===== Business Insight Generator Error =====")
        print(e)
        raise

#------------------------------------
# VISUALIZATION PLANNER NODE
#------------------------------------
def visualization_planner(state: GraphState) -> GraphState:

    print("===== Visualization Planner Started =====")

    try:

        prompt = VISUALIZATION_PLANNER_PROMPT.format(
            user_query=state.user_query,
            analysis_results=str(state.analysis_results),
            business_insights=str(state.business_insights),
            columns=", ".join(state.dataframe.columns)
        )

        structured_llm = llm.with_structured_output(VisualizationPlans)

        response = structured_llm.invoke(prompt)

        state.visualization_plans = response
        state.error = None

        print("===== Visualization Planner Finished =====")
        print(response)

        return state

    except Exception as e:

        print("===== Visualization Planner Error =====")
        print(e)

        raise

#------------------------------------
# CHART GENERATOR NODE
#------------------------------------
def chart_generator(state: GraphState) -> GraphState:

    print("===== Chart Generator Started =====")

    try:

        os.makedirs("charts", exist_ok=True)

        chart_paths = []

        for plan in state.visualization_plans.charts:

            chart_type = plan.chart_type.lower()

            if chart_type == "bar":
                path = generate_bar_chart(state.dataframe, plan)

            elif chart_type == "line":
                path = generate_line_chart(state.dataframe, plan)

            elif chart_type == "scatter":
                path = generate_scatter_chart(state.dataframe, plan)

            elif chart_type == "pie":
                path = generate_pie_chart(state.dataframe, plan)

            else:
                print(f"Unsupported chart type: {plan.chart_type}")
                continue

            chart_paths.append(path)

        state.chart_paths = chart_paths
        state.error = None

        print("Generated Charts:")
        print(chart_paths)

        print("===== Chart Generator Finished =====")

        return state

    except Exception as e:
        print("===== Chart Generator Error =====")
        print(e)
        raise
#------------------------------------
# REPORT GENERATOR NODE
#------------------------------------
def report_generator(state: GraphState) -> GraphState:

    print("===== Report Generator Started =====")

    try:
        analysis_summary = ""
        for analysis in state.analysis_results.analyses:
            analysis_summary += f"""
            Analysis: {analysis.analysis_name}
            Summary:{analysis.summary}"""

        prompt = REPORT_GENERATOR_PROMPT.format(
            user_query=state.user_query,
            dataset_summary=str(state.dataset_summary),
            analysis_results=analysis_summary,
            business_insights=str(state.business_insights)
        )

        structured_llm = llm.with_structured_output(Report)

        response = structured_llm.invoke(prompt)

        state.final_report = response
        state.error = None

        print("===== Report Generator Finished =====")
        print(response)

        return state

    except Exception as e:
        print("===== Report Generator Error =====")
        print(e)
        raise