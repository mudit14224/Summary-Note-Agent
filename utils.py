# Imports
import json
from typing import Dict

# Function to create the qa string from the json file
def get_qa_string(data):
    # with open(json_path) as f:
    #     data = json.load(f)
    n = len(data)
    qa_string = ""
    for i in range(n):
        q = data[i]['q']
        a = data[i]['a']
        string = "q: " + q + "\n" + "a: " + a
        qa_string += string + "\n"
    return qa_string

def parse_split_result(result):
    # Create a dictionary from the parsed result
    categorized_dict: Dict[str, str] = {category.category: category.questions_and_answers for category in result.categories}
    string = ""
    for category in categorized_dict:
        string += "\n"
        qa = categorized_dict[category]
        partial_str = category + ":\n" + qa
        string += partial_str
    return string, categorized_dict