import json
import os

# Function to load JSON data from a file
def load_json(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)

# Load the initial document data from 'wikipedia_forgeries_corpus.json'
initial_document_data = load_json("wikipedia_forgeries_corpus.json")
claims_data = load_json("claims_list.json")

# Directory containing the entity files
entity_files_dir = "output-by-document"

# Function to load entity data from a file
def load_entity_data(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)

# Combined output data
combined_output = []

# Process each document
for doc_data in initial_document_data:
    page_id = doc_data["Page ID"]
    entity_filename = os.path.join(entity_files_dir, f"{page_id}.json")
    
    if os.path.exists(entity_filename):
        entity_data = load_entity_data(entity_filename)
        # Transform the structure of the entity data
        transformed_entities = {}
        for entity_name, entity_details in entity_data.items():
            opinion_info = {
                "is_expressing_opinion": entity_details.get("is_expressing_opinion"),
                "opinion_evaluation": entity_details.get("opinion_evaluation"),
                "opinion_evidence_provided": entity_details.get("opinion_evidence_provided"),
                "opinion_reason": entity_details.get("opinion_reason"),
                "opinion_document_author": entity_details.get("opinion_document_author"),
                "opinion_document_date": entity_details.get("opinion_document_date"),
                "opinion_document_location": entity_details.get("opinion_document_location"),
                "opinion_specific_perspective": entity_details.get("opinion_specific_perspective"),
            }
            opinion_info = {k: v for k, v in opinion_info.items() if v is not None}

            entity_info = {
                "entity_in_text": entity_details["entity_info"].get("text"),
                "wd_label": entity_details["entity_info"].get("resolved_label"),
                "wd_description": entity_details["entity_info"].get("description"),
                "wd_id": entity_details["entity_info"].get("wikidata_id"),
                "wd_also_known_as": entity_details["entity_info"].get("also_known_as"),
                "wd_occupation": entity_details["entity_info"].get("occupation"),
                "wd_date_of_birth": entity_details["entity_info"].get("date of birth"),
                "wd_date_of_death": entity_details["entity_info"].get("date of death"),
                "wd_instance_of": entity_details["entity_info"].get("instance_of"),
            }
            entity_info = {k: v for k, v in entity_info.items() if v is not None}

            # Add claims and bibliography from claims_list.json
            claims_list = claims_data.get(page_id, {}).get(entity_name, {}).get(entity_name, [])
            transformed_entities[entity_name] = {
                "opinion_info": opinion_info,
                "entity_info": entity_info,
                "claims": claims_list
            }
        doc_data["Entities"] = transformed_entities
    else:
        doc_data["Entities"] = {}
    
    combined_output.append(doc_data)

# Save the combined output to a single JSON file
output_filename = "combined_output.json"
with open(output_filename, "w", encoding="utf-8") as outfile:
    json.dump(combined_output, outfile, ensure_ascii=False, indent=4)

print(f"Combined output saved to {output_filename}")
