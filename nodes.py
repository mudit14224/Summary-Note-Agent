# Imports
from chains import create_categorize_chain, create_split_grader_chain, create_summary_chain, create_summary_grader_chain
from utils import parse_split_result
from dotenv import load_dotenv

load_dotenv()

# Create the chains
categorize_chain = create_categorize_chain()
split_grader = create_split_grader_chain()
summary_chain = create_summary_chain()
summary_grader = create_summary_grader_chain()


### Nodes
def split_qa(state):
    print("----SPLITTING INTO CATEGORIES---")
    qa_string = state['qa_string']

    # invoke rag chain
    split_result = categorize_chain.invoke({'input_text': qa_string})
    # Run the function to parse the result
    categorized_qa, categorized_dict = parse_split_result(result=split_result)

    return {"categorized_qa": categorized_qa, "categorized_dict": categorized_dict}

def grade_split(state):
    print("---CHECK IF SPLITS ARE RELEVANT---")
    # Get the categorized_qa and categorized_dict
    categorized_qa = state['categorized_qa']
    categorized_dict = state['categorized_dict']
    qa_string = state['qa_string']
    # Get the score
    score = split_grader.invoke({"qa_string": qa_string, "categorized_qa": categorized_qa})
    grade = score.binary_score

    # Check is splits are relevant
    if grade == 'correct':
        print('---DECISION: SPLITS ARE RELEVANT---')
        return 'correct splits'
    else:
        return 'incorrect splits'
    
def generate_summaries(state):
    print("---GENERATING SUMMARIES---")
    # Get the categorized dict
    categorized_dict = state['categorized_dict']
    summaries = {}
    for category in categorized_dict:
        summ_result = summary_chain.invoke({'category': category, 'q_and_a_pairs': categorized_dict[category]})
        summaries[category] = summ_result

    return {'summaries': summaries}

def grade_summaries(state):
    print("---GRADING GENERATED SUMMARIES---")
    # Get the categorized dict and the summaries
    categorized_dict = state['categorized_dict']
    summaries = state['summaries']
    incorrect_summary_cats = []
    for category in categorized_dict:
        score = summary_grader.invoke({"q_and_a_pairs": categorized_dict[category], "response": summaries[category]})
        grade = score.binary_score
        if grade == 'correct': 
            print(f'---SUMMARY FOR {category} IS CORRECT---')
            continue
        else:
            print(f'---SUMMARY FOR {category} IS INCORRECT---')
            incorrect_summary_cats.append(category)

    return {'incorrect_summary_cats': incorrect_summary_cats, 'summaries': summaries}

def decide_to_regenerate(state):
    print('---ASSESS WHETHER TO PROCEED OR REGENERATE---')
    # Get the incorrect_summary_cats dict
    incorrect_summary_cats = state['incorrect_summary_cats']
    if not incorrect_summary_cats: 
        print("---DECISION: ALL SUMMARIES ARE CORRECT (PROCEED)---")
        return 'continue'
    else:
        print("---DECISION: SOME SUMMARIES ARE INCORRECT (REGENERATE)---")
        return 'regen summaries'
    
def correct_summaries(state):
    print("---REGENERATING INCORRECT SUMMARIES---")
    # Get the categorized dict, the summaries and the incorrect summaries categories
    categorized_dict = state['categorized_dict']
    summaries = state['summaries']
    incorrect_summary_cats = state['incorrect_summary_cats']
    regen_summaries = {}
    for category in incorrect_summary_cats:
        summ_result = summary_chain.invoke({'category': category, 'q_and_a_pairs': categorized_dict[category]})
        regen_summaries[category] = summ_result
    
    return {'regen_summaries': regen_summaries}

def grade_regen_summaries(state): 
    print("---GRADING REGENERATED SUMMARIES---")
    # Get the categorized dict, regenerated summaries and summaries
    categorized_dict = state['categorized_dict']
    summaries = state['summaries']
    regen_summaries = state['regen_summaries']
    incorrect_summary_cats = []
    for category in regen_summaries:
        score = summary_grader.invoke({"q_and_a_pairs": categorized_dict[category], "response": regen_summaries[category]})
        grade = score.binary_score
        if grade == 'correct':
            print(f'---REGENERATED SUMMARY FOR {category} IS CORRECT---')
            summaries[category] = regen_summaries[category]
            continue
        else:
            print(f'---REGENERATED SUMMARY FOR {category} IS INCORRECT---')
            incorrect_summary_cats.append(category)
    return {'summaries': summaries, 'incorrect_summary_cats': incorrect_summary_cats}