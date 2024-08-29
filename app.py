import gradio as gr
import json
from main import main

def process_json(file):
    # Read the JSON file
    with open(file.name, 'r') as f:
        data = json.load(f)
    
    summaries_dict = main(data=data)
    output = ''
    for category in summaries_dict:
        output += category + ': \n'
        output += summaries_dict[category] + "\n\n"
    return output

# Create a Gradio interface
iface = gr.Interface(
    fn=process_json, 
    inputs=gr.File(label="Upload JSON File"), 
    outputs="text", 
    title="Summary Note Agent",
    description="Upload the form as JSON file and get Note summary in Conversation form."
)

# Launch the interface
iface.launch()
