import json
import csv
from difflib import SequenceMatcher

# Function to load JSON data from a file
def load_json(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)

# Load the manual and ML output data
manual_data = load_json("manual_output.json")
ml_data = load_json("ml_output.json")

# Function to extract entities from the data
def extract_entities(data):
    entities_per_doc = {}
    for doc in data:
        page_id = doc["Page ID"]
        entities = {}
        if "Entities" in doc:
            for entity_name, entity_info in doc["Entities"].items():
                entity_text = entity_info["entity_info"].get("entity_in_text", entity_name)
                also_known_as = entity_info["entity_info"].get("wd_also_known_as", [])
                wikidata_id = entity_info["entity_info"].get("wd_id", "")
                entities[entity_text] = {
                    "also_known_as": also_known_as,
                    "wikidata_id": wikidata_id
                }
        entities_per_doc[page_id] = entities
    return entities_per_doc

# Function to find unmatched entities between two lists
def find_unmatched_entities(manual_entities, ml_entities):
    unmatched_manual = []
    unmatched_ml = []

    # Helper function to match entities
    def match_entities(entity, entities):
        if entity in entities:
            return True
        for alias in entities.get(entity, {}).get("also_known_as", []):
            if alias in entities:
                return True
        if entities.get(entity, {}).get("wikidata_id", "") in entities.values():
            return True
        return False

    for entity in manual_entities:
        if not match_entities(entity, ml_entities):
            unmatched_manual.append(entity)

    for entity in ml_entities:
        if not match_entities(entity, manual_entities):
            unmatched_ml.append(entity)

    return unmatched_manual, unmatched_ml

# Extract entities from both datasets
manual_entities_per_doc = extract_entities(manual_data)
ml_entities_per_doc = extract_entities(ml_data)

# Compare and find unmatched entities for each document
unmatched_entities_per_doc = {}

for page_id in manual_entities_per_doc.keys() | ml_entities_per_doc.keys():
    manual_entities = manual_entities_per_doc.get(page_id, {})
    ml_entities = ml_entities_per_doc.get(page_id, {})
    unmatched_manual, unmatched_ml = find_unmatched_entities(manual_entities, ml_entities)
    if unmatched_manual or unmatched_ml:
        unmatched_entities_per_doc[page_id] = {
            "unmatched_manual": unmatched_manual,
            "unmatched_ml": unmatched_ml
        }

# Print the unmatched entities for each document
for page_id, unmatched in unmatched_entities_per_doc.items():
    print(f"Document ID: {page_id}")
    print(f"Unmatched entities from Manual data: {unmatched['unmatched_manual']}")
    print(f"Unmatched entities from ML data: {unmatched['unmatched_ml']}")
    print()

# Save the unmatched entities to a CSV file for further analysis
with open("unmatched_entities.csv", "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["Page ID", "Unmatched Manual Entities", "Unmatched ML Entities"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for page_id, unmatched in unmatched_entities_per_doc.items():
        writer.writerow({
            "Page ID": page_id,
            "Unmatched Manual Entities": ", ".join(unmatched["unmatched_manual"]),
            "Unmatched ML Entities": ", ".join(unmatched["unmatched_ml"])
        })

print("Unmatched entities saved to unmatched_entities.csv")
