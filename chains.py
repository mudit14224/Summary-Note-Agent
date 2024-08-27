# Imports
import json 
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from data_models import CategorizedQA, SplitGrader, SummaryGrader


# Categorize chain
def create_categorize_chain():
    split_prompt_template = """
    You will receive a list of questions and answers on various topics. Your task is to categorize the Q&A pairs into logical categories based on their content.

    Here is what you should do:
    1. Identify the main topics or categories based on the questions and answers. These categories could be related to symptoms, events, activities, preferences, etc.
    2. Group related questions and answers under the appropriate categories. If a question and answer do not fit well into an existing category, create a new category for them.
    3. Output the result as a JSON dictionary with the following structure:
    {{
    "category": "Category Name",
    "questions_and_answers": {{
        "Vomiting": "q: Question 1\\na: Answer 1\\nq: Question 2\\na: Answer 2",
        "diarrhea": "q: Question 3\\na: Answer 3\\nq: Question 4\\na: Answer 4"
    }}
    }}

    Here is the list of Q&A pairs:

    {input_text}

    Please return the categorized Q&A pairs in JSON format with category names as keys and the relevant Q&A pairs as values.
    """

    # Create the prompt template
    split_prompt = PromptTemplate(input_variables=['input_text'], template=split_prompt_template)

    # Initialize the llm
    split_llm = ChatOpenAI(model='gpt-4o', temperature=0)
    split_structured_llm = split_llm.with_structured_output(CategorizedQA)
    categorize_chain = split_prompt | split_structured_llm
    return categorize_chain
    # split_result = categorize_chain.invoke({'input_text': qa_string})

# Split Grader
def create_split_grader_chain():
    # Initialize the llm
    split_grader_llm = ChatOpenAI(model='gpt-4o', temperature=0)
    split_grader_structured_llm_grader = split_grader_llm.with_structured_output(SplitGrader)

    split_grader_system = """You are a grader assessing whether the question answer pairs have been correctly categorized into categories. \n
    You must also check if all the questions have been categorized. Check for hallucinations as well. \n
    Give a binary score 'correct' or 'incorrect'. 'correct' means that the Q&A pairs are categorized correctly without any missing information or hallucinations.
    """
    answer_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", split_grader_system), 
            ("human", "Q&A Input \n\n {qa_string} \n\n Categorized Q&A: {categorized_qa}")
        ]
    )

    split_grader = answer_prompt | split_grader_structured_llm_grader
    return split_grader
    # split_grader.invoke({"qa_string": qa_string, "categorized_qa": categorized_qa})

# Summary Chain
def create_summary_chain():
    # Initialize the llm
    llm = ChatOpenAI(model='gpt-4o', temperature=0)

    summ_system = """
    You are given a category and a set of questions and answers related to that category. Your task is to convert these questions and answers into a natural, conversational response as if someone is summarizing their situation based on the answers provided.

    Instructions:
    1. Use the answers to infer a coherent response that sounds natural and conversational.
    2. Incorporate relevant details from both the questions and answers.
    3. Avoid directly repeating the questions; instead, focus on integrating the information into a fluid conversation.

    Output format:
    - The response should be a short, concise paragraph that summarizes the answers in a conversational tone.

    Please convert the given category and Q&A pairs into a conversational summary.

    Input:
    - Category: {category}
    - Q&A Pairs:
    {q_and_a_pairs}
    """

    # Create the prompt template
    summ_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", summ_system), 
            ("human", "Category: {category} \n\n Q&A pairs: {q_and_a_pairs}")
        ]
    )

    summary_chain = summ_prompt | llm | StrOutputParser()
    return summary_chain
    # summ_result = summary_chain.invoke({'category': 'Diarrhea', 'q_and_a_pairs': categorized_dict['Diarrhea']})


# Summary Grader chain
def create_summary_grader_chain():
    summ_grader_llm = ChatOpenAI(model='gpt-4o', temperature=0)
    summ_grader_structured_llm_grader = summ_grader_llm.with_structured_output(SummaryGrader)

    # System Prompt
    summ_grader_system = """You are a grader assessing whether the response is a natural, conversational response as if someone is summarizing their situation or not. \n
    You must also check if all the questions and answers have been included. Check for hallucinations as well. \n
    Give a binary score 'correct' or 'incorrect'. 'correct' means that the Q&A pairs are correctly incorporated in the response without any missing information or hallucinations.
    """

    answer_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", summ_grader_system), 
            ("human", "Q&A pairs: {q_and_a_pairs} \n\n Response: {response}")
        ]
    )

    summary_grader = answer_prompt | summ_grader_structured_llm_grader 
    return summary_grader
    # summary_grader.invoke({"q_and_a_pairs": categorized_dict['Diarrhea'], "response": summ_result})


