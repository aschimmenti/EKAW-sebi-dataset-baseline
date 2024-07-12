import json
import os

# Function to load JSON data from a file
def load_json(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)

# Load the initial document data and claims data
initial_document_data = load_json("wikipedia_forgeries_corpus.json")
claims_data = load_json("claims_list.json")

# Directory containing the entity files
entity_files_dir = "output-by-document"

# Function to load entity data from a file
def load_entity_data(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)

# Process a single document
page_id = "doc18"
entity_filename = os.path.join(entity_files_dir, f"{page_id}.json")

# Find the specific document in the initial document data
doc_data = next((doc for doc in initial_document_data if doc["Page ID"] == page_id), None)

if doc_data:
    print(f"Document data found for {page_id}")
else:
    print(f"No document data found for {page_id}")

if os.path.exists(entity_filename):
    print(f"Entity file found for {page_id}")
    entity_data = load_entity_data(entity_filename)
    print(f"Loaded entity data: {json.dumps(entity_data, indent=2)}")
else:
    print(f"No entity file found for {page_id}")

if doc_data and os.path.exists(entity_filename):
    entity_data = load_entity_data(entity_filename)
    # Transform the structure of the entity data
    transformed_entities = {}
    for entity_name, entity_details in entity_data[page_id].items():
        if "entity_info" in entity_details:
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
            print(f"Transformed entity: {json.dumps(transformed_entities[entity_name], indent=2)}")
    doc_data["Entities"] = transformed_entities
    
    # Save the combined output to a single JSON file
    output_filename = f"combined_output_{page_id}.json"
    with open(output_filename, "w", encoding="utf-8") as outfile:
        json.dump(doc_data, outfile, ensure_ascii=False, indent=4)
    
    print(f"Combined output saved to {output_filename}")
else:
    print(f"Document ID {page_id} not found in initial data or entity file does not exist.")
