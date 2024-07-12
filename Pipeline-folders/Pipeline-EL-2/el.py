import json
import difflib

# Define the paths for input and output JSON files
manual_annotation_path = "./manual_annotation.json"
entities_path = "./entities.json"
output_path = "./updated_entities.json"

# Load the manual annotation data from the JSON file
with open(manual_annotation_path, 'r', encoding='utf-8') as f:
    manual_annotation_data = json.load(f)

# Load the entities data from the JSON file
with open(entities_path, 'r', encoding='utf-8') as f:
    entities_data = json.load(f)

def is_similar(a, b, threshold=0.8):
    """Check if two strings are similar above a certain threshold."""
    if a is None or b is None:
        return False
    return difflib.SequenceMatcher(None, a, b).ratio() > threshold

# Function to find and add entity_info from manual_annotation_data to entities_data
def add_entity_info(entities_data, manual_annotation_data):
    for doc_key, doc_value in entities_data.items():
        if doc_key in manual_annotation_data:
            for entity in doc_value["entities"]:
                entity_text = entity["text"]
                for entity_key, entity_value in manual_annotation_data[doc_key].items():
                    if entity_key == "document_info":
                        continue
                    if "entity_info" in entity_value:
                        entity_info = entity_value["entity_info"]
                        if (entity_text == entity_info.get("resolved_label") or
                            entity_text == entity_info.get("label") or
                            entity_text in entity_info.get("also_known_as", []) or
                            is_similar(entity_text, entity_info.get("resolved_label")) or
                            is_similar(entity_text, entity_info.get("label")) or
                            any(is_similar(entity_text, aka) for aka in entity_info.get("also_known_as", []))):
                            entity.update(entity_info)
                            break
    return entities_data

# Add entity_info to entities_data
updated_entities_data = add_entity_info(entities_data, manual_annotation_data)

# Save the updated entities data to a JSON file with ensure_ascii=False
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(updated_entities_data, f, ensure_ascii=False, indent=4)

print(f"Updated entities data saved to {output_path}")
