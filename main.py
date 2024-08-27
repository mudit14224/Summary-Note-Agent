# Imports
from pprint import pprint
from utils import get_qa_string
from graph import create_graph_workflow
from dotenv import load_dotenv

load_dotenv()

def main(json_path):
    # Get the qa_string from the json file
    qa_string = get_qa_string(json_path=json_path)

    # Create the graph workflow app
    app = create_graph_workflow()
    # See the graph
    # print(app.get_graph())
    inputs = {"qa_string": qa_string}
    for output in app.stream(inputs):
        for key, value in output.items():
            # Node
            pprint(f"Node '{key}':")
        pprint("\n---\n")
    pprint(value['summaries'])


if __name__ == '__main__':
    main('./filled_form.json')