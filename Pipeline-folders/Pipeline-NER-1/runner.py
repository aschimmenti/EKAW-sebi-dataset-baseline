import json
from ent_classification_pipeline import PipelineRunner, infer_years_for_dates
import spacy

# Define the paths for input and output JSON files
input_json_path = "./manual_annotation.json"
output_json_path = "./entities.json"

# Load the input data from the JSON file
with open(input_json_path, 'r', encoding='utf-8') as f:
    input_data = json.load(f)

# Initialize the pipeline runner
runner = PipelineRunner(config_path="./fewshot.cfg", examples_path="./examples.json")

# Initialize an empty dictionary for the output data
output_data = {}
max_tokens=8000

def split_text(text, max_tokens=8000):
    """Split text into chunks with a maximum number of tokens."""
    nlp = spacy.blank("en")
    nlp.add_pipe("sentencizer")
    doc = nlp(text)
    spans = list(doc.sents)
    
    chunks = []
    current_chunk = ""
    current_tokens = 0

    for span in spans:
        span_tokens = len(span.text.split())
        if current_tokens + span_tokens > max_tokens:
            if current_tokens == 0:
                # If a single span exceeds max_tokens, add it directly to avoid infinite loop
                chunks.append(span.text.strip())
            else:
                chunks.append(current_chunk.strip())
            current_chunk = span.text
            current_tokens = span_tokens
        else:
            current_chunk += " " + span.text
            current_tokens += span_tokens
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

# Process each document in the input data
for doc_key, doc_value in input_data.items():
    try:
        text = doc_value['document_info']['Document description'] + doc_value['document_info']['Document claims']
        
        # Apply the infer_years_for_dates function to the text
        text = infer_years_for_dates(text)
        
        # Split the text if it exceeds the maximum token limit
        chunks = split_text(text)

        # Initialize an empty list to collect entities from all chunks
        all_entities = []

        for chunk in chunks:
            # Re-split chunk if it still exceeds the limit (nested split)
            sub_chunks = split_text(chunk, max_tokens // 2)
            for sub_chunk in sub_chunks:
                # Run the pipeline on each sub-chunk
                doc = runner.run(sub_chunk)

                # Collect entities from the sub-chunk
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

    except Exception as e:
        # Save the current output data to a JSON file if an error occurs
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=4)
        print(f"Error processing document {doc_key}: {e}")
        break

# Save the output data to a JSON file with ensure_ascii=False
with open(output_json_path, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=4)

print(f"Processed data saved to {output_json_path}")
