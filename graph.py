# Imports
from typing import List, Dict
from typing_extensions import TypedDict
from nodes import *
from langgraph.graph import END, StateGraph, START


# Define the state of the graph
class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        qa_string: Question and answer string (Input to the Model)
    """
    qa_string: str
    categorized_qa: str
    categorized_dict: Dict[str, str]
    summaries: Dict[str, str]
    incorrect_summary_cats: List[str]
    regen_summaries: Dict[str, str]


def create_graph_workflow():
    workflow = StateGraph(GraphState)

    # Define the nodes
    workflow.add_node("split_qa", split_qa)
    workflow.add_node("generate_summaries", generate_summaries)
    workflow.add_node("correct_summaries", correct_summaries)
    workflow.add_node("grade_regen_summaries", grade_regen_summaries)
    workflow.add_node('grade_summaries', grade_summaries)

    # Build the graph
    workflow.add_edge(START, 'split_qa')
    workflow.add_conditional_edges(
        'split_qa', 
        grade_split, 
        {
            'correct splits': 'generate_summaries',
            'incorrect splits': 'split_qa'
        },
    )
    workflow.add_edge('generate_summaries', 'grade_summaries')
    workflow.add_conditional_edges(
        'grade_summaries', 
        decide_to_regenerate,
        {
            'continue': END,
            'regen summaries': 'correct_summaries'
        }
    )
    workflow.add_edge('correct_summaries', 'grade_regen_summaries')
    workflow.add_conditional_edges(
        'grade_regen_summaries', 
        decide_to_regenerate, 
        {
            'continue': END, 
            'regen summaries': 'correct_summaries'
        }
    )

    # Compile
    app = workflow.compile()

    return app

