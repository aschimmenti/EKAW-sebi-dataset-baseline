import json
import spacy
from ent_classification_pipeline import PipelineRunner, infer_years_for_dates

# Define the paths for input and output JSON files
input_json_path = "./manual_annotation.json"
output_json_path = "./entities_doc18.json"

# Load the input data from the JSON file
with open(input_json_path, 'r', encoding='utf-8') as f:
    input_data = json.load(f)

# Initialize the pipeline runner
runner = PipelineRunner(config_path="./fewshot.cfg", examples_path="./examples.json")

# Initialize an empty dictionary for the output data
output_data = {}

def split_text_into_parts(text, num_parts=3):
    """Split text into a specified number of equal parts with proper sentence boundaries."""
    nlp = spacy.blank("en")
    nlp.add_pipe("sentencizer")
    doc = nlp(text)
    
    sentences = list(doc.sents)
    total_sentences = len(sentences)
    part_size = total_sentences // num_parts

    parts = []
    for i in range(num_parts):
        start = i * part_size
        if i == num_parts - 1:  # last part
            end = total_sentences
        else:
            end = (i + 1) * part_size
        part_text = " ".join([sent.text for sent in sentences[start:end]]).strip()
        if not part_text.endswith('.'):
            part_text += '.'
        parts.append(part_text)
    
    return parts

def process_document(doc_key, doc_value):
    text = doc_value['document_info']['Document description'] + " " + doc_value['document_info']['Document claims']
    
    # Apply the infer_years_for_dates function to the text
    text = infer_years_for_dates(text)
    
    # Split the text into 3 equal parts with proper sentence boundaries
    parts = split_text_into_parts(text, num_parts=3)

    # Initialize an empty list to collect entities from all parts
    all_entities = []

    for part in parts:
        # Run the pipeline on each part
        doc = runner.run(part)

        # Collect entities from the part
        for ent in doc.ents:
            entity = {
                "text": ent.text,
                "start_char": ent.start_char,
                "end_char": ent.end_char,
                "label": ent.label_,
                "description": None  # Placeholder for additional information
            }
            all_entities.append(entity)
    
    # Add entities to the output data
    output_data[doc_key] = {
        "entities": all_entities
    }

# Process only document doc18
try:
    process_document('doc18', input_data['doc18'])
except Exception as e:
    print(f"Error processing document doc18: {e}")

# Save the output data to a JSON file with ensure_ascii=False
with open(output_json_path, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=4)

print(f"Processed data for doc18 saved to {output_json_path}")
