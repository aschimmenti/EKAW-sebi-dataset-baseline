import csv
import json
from difflib import SequenceMatcher

# Function to load JSON data from a file
def load_json(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)

# Load the manual and ML output data
manual_data = load_json("manual_output.json")
ml_data = load_json("ml_output.json")

# Function to extract entities expressing opinions from data
def extract_opinion_entities(data):
    entities_by_doc = {}
    for doc in data:
        page_id = doc["Page ID"]
        entities_by_doc[page_id] = []
        if "Entities" in doc:
            for entity_name, entity_info in doc["Entities"].items():
                if entity_info["opinion_info"].get("is_expressing_opinion") == True:
                    entities_by_doc[page_id].append(entity_info)
    return entities_by_doc

# Extract entities expressing opinions from both datasets
manual_entities = extract_opinion_entities(manual_data)
ml_entities = extract_opinion_entities(ml_data)

# Function to check similarity between two strings
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

# Create CSV file
with open('entities_opinions_evaluation.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow([
        "doc_id", "entity_name_manual", "entity_name_ml", 
        "manual_opinion_evaluation", "ml_opinion_evaluation",
        "manual_opinion_evidence_provided", "ml_opinion_evidence_provided",
        "manual_opinion_specific_perspective", "ml_opinion_specific_perspective"
    ])

    # Iterate over all documents
    for doc_id in manual_entities.keys() | ml_entities.keys():
        manual_set = manual_entities.get(doc_id, [])
        ml_set = ml_entities.get(doc_id, [])
        
        for manual_entity in manual_set:
            manual_name = manual_entity["entity_info"]["entity_in_text"]
            manual_aka = manual_entity["entity_info"].get("wd_also_known_as", [])
            manual_wdid = manual_entity["entity_info"].get("wd_id", None)
            manual_opinion_evaluation = manual_entity["opinion_info"].get("opinion_evaluation")
            manual_opinion_evidence_provided = ", ".join(
                [evidence["feature"] for evidence in manual_entity["opinion_info"].get("opinion_evidence_provided", [])]
            )
            manual_opinion_specific_perspective = ", ".join(
                manual_entity["opinion_info"].get("opinion_specific_perspective", [])
            )
            
            matched = False
            for ml_entity in ml_set:
                ml_name = ml_entity["entity_info"]["entity_in_text"]
                ml_aka = ml_entity["entity_info"].get("wd_also_known_as", [])
                ml_wdid = ml_entity["entity_info"].get("wd_id", None)
                ml_opinion_evaluation = ml_entity["opinion_info"].get("opinion_evaluation")
                ml_opinion_evidence_provided = ", ".join(
                    [evidence["feature"] for evidence in ml_entity["opinion_info"].get("opinion_evidence_provided", [])]
                )
                ml_opinion_specific_perspective = ", ".join(
                    ml_entity["opinion_info"].get("opinion_specific_perspective", [])
                )
                
                if (manual_name == ml_name or 
                    manual_name in ml_aka or 
                    ml_name in manual_aka or 
                    (manual_wdid and manual_wdid == ml_wdid) or 
                    similar(manual_name, ml_name) > 0.7):
                    writer.writerow([
                        doc_id, manual_name, ml_name, 
                        manual_opinion_evaluation, ml_opinion_evaluation,
                        manual_opinion_evidence_provided, ml_opinion_evidence_provided,
                        manual_opinion_specific_perspective, ml_opinion_specific_perspective
                    ])
                    matched = True
                    break
