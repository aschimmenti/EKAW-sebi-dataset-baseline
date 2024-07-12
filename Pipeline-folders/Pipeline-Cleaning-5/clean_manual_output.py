import json
import os

# Load the JSON data from the given file
with open("manual_annotation.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Function to restructure the entity data
def restructure_entity(entity_data):
    if "entity_info" not in entity_data:
        return None

    entity_info = entity_data["entity_info"]

    opinion_info = {
        "is_expressing_opinion": entity_data.get("is_expressing_opinion", None),
        "opinion_evaluation": entity_data.get("opinion_evaluation", None),
        "opinion_evidence_provided": entity_data.get("opinion_evidence_provided", None),
        "opinion_reason": entity_data.get("opinion_reason", None),
        "opinion_document_author": entity_data.get("opinion_document_author", None),
        "opinion_document_date": entity_data.get("opinion_document_date", None),
        "opinion_document_location": entity_data.get("opinion_document_location", None),
        "opinion_specific_perspective": entity_data.get("opinion_specific_perspective", None),
    }

    # Filter out None values from opinion_info
    opinion_info = {k: v for k, v in opinion_info.items() if v is not None}

    entity_info_structured = {
        "entity_in_text": entity_info.get("text", None),
        "wd_label": entity_info.get("label", None),
        "wd_description": entity_info.get("description", None),
        "wd_id": entity_info.get("wikidata_id", None),
        "wd_also_known_as": entity_info.get("also_known_as", None),
        "wd_occupation": entity_info.get("occupation", None),
        "wd_date_of_birth": entity_info.get("date of birth", None),
        "wd_date_of_death": entity_info.get("date of death", None),
        "wd_instance_of": entity_info.get("instance_of", None),
    }

    # Filter out None values from entity_info_structured
    entity_info_structured = {k: v for k, v in entity_info_structured.items() if v is not None}

    return {
        "opinion_info": opinion_info,
        "entity_info": entity_info_structured,
        "claims": entity_data.get("claims", [])
    }

# Process each document in the data
output_data = []

for document_id, document_data in data.items():
    entities = document_data.copy()
    document_info = entities.pop("document_info")

    processed_entities = {}
    for entity_name, entity_data in entities.items():
        restructured_entity = restructure_entity(entity_data)
        if restructured_entity:
            processed_entities[entity_name] = restructured_entity

    output_data.append({
        "Page ID": document_id,
        "Source": document_info.get("Source"),
        "Page URL": document_info.get("Page URL"),
        "Document description": document_info.get("Document description"),
        "Document claims": document_info.get("Document claims"),
        "Entities": processed_entities
    })

# Save the modified data to a new JSON file
output_filename = "manual_output.json"
with open(output_filename, "w", encoding="utf-8") as f:
    json.dump(output_data, f, ensure_ascii=False, indent=4)

print(f"Modified output saved to {output_filename}")

