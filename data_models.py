# Imports 
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List

# Data Models for categorize chain
# Define the Pydantic Object for Function Calling
class SymptomCategory(BaseModel):
    category: str = Field(description="The name of the category")
    questions_and_answers: str = Field(description="The Q&A pairs in that category as a single string")

class CategorizedQA(BaseModel):
    categories: List[SymptomCategory] = Field(description="A list of categorized Q&A pairs")

# Data Model for split grader
class SplitGrader(BaseModel):
    """Binary score to assess if the splits are correct or not and if there is any missing information or hallucinations"""

    binary_score: str = Field(
        description="A binary indicator ('correct' or 'incorrect') that evaluates if the Q&A pairs are categorized correctly without any missing information or hallucinations."
    )

# Data Model for summary grader
class SummaryGrader(BaseModel):
    """Binary score to assess if the response is a natural, conversational response or not and if there is any missing information or hallucinations"""

    binary_score: str = Field(
        description="A binary indicator ('correct' or 'incorrect') that evaluates if the response is a natural, conversational response or not without any missing information or hallucinations."
    )