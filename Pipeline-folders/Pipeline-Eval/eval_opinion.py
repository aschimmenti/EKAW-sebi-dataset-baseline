import json
from sklearn.metrics import classification_report
from difflib import SequenceMatcher

# Function to load JSON data from a file
def load_json(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)

# Load the manual and ML output data
manual_data = load_json("manual_output.json")
ml_data = load_json("ml_output.json")

# Function to filter and extract entities expressing opinions
def extract_opinion_entities(data):
    entities_by_doc = {}
    for doc in data:
        page_id = doc["Page ID"]
        entities_by_doc[page_id] = []
        if "Entities" in doc:
            for entity_name, entity_info in doc["Entities"].items():
                if entity_info["opinion_info"].get("is_expressing_opinion") == True:
                    if "entity_info" in entity_info:
                        entity_text = entity_info["entity_info"].get("entity_in_text")
                        if entity_text:  # Ensure the entity_in_text key exists
                            entities_by_doc[page_id].append(entity_info["entity_info"])
    return entities_by_doc

# Extract entities expressing opinions from both datasets
manual_entities = extract_opinion_entities(manual_data)
ml_entities = extract_opinion_entities(ml_data)

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

# Function to map entity names for comparison
def map_entities_by_name(entities):
    entity_map = {}
    for entity in entities:
        name = entity["entity_in_text"]
        aka = entity.get("wd_also_known_as", [])
        wdid = entity.get("wd_id", None)
        entity_map[name] = (aka, wdid)
    return entity_map

# Initialize counters for TP, FP, FN
tp, fp, fn = 0, 0, 0

# Initialize y_true and y_pred for F1 calculation
y_true = []
y_pred = []

for doc_id in manual_entities.keys() | ml_entities.keys():
    manual_set = manual_entities.get(doc_id, [])
    ml_set = ml_entities.get(doc_id, [])

    manual_map = map_entities_by_name(manual_set)
    ml_map = map_entities_by_name(ml_set)

    matched_manual = set()
    matched_ml = set()

    # Compare manual entities with ML entities
    for manual_name, (manual_aka, manual_wdid) in manual_map.items():
        matched = False
        for ml_name, (ml_aka, ml_wdid) in ml_map.items():
            if (manual_name == ml_name or 
                manual_name in ml_aka or 
                ml_name in manual_aka or 
                (manual_wdid and manual_wdid == ml_wdid) or 
                similar(manual_name, ml_name) > 0.7):
                matched = True
                matched_manual.add(manual_name)
                matched_ml.add(ml_name)
                break
        
        if matched:
            tp += 1
            y_true.append(1)
            y_pred.append(1)
        else:
            fn += 1
            y_true.append(1)
            y_pred.append(0)
    
    for ml_name in ml_map.keys():
        if ml_name not in matched_ml:
            fp += 1
            y_true.append(0)
            y_pred.append(1)

# Calculate precision, recall, and F1 score
precision = tp / (tp + fp) if (tp + fp) > 0 else 0
recall = tp / (tp + fn) if (tp + fn) > 0 else 0
f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

# Print results
print(f"True Positives: {tp}")
print(f"False Positives: {fp}")
print(f"False Negatives: {fn}")
print(f"Precision for is_expressing_opinion: {precision}")
print(f"Recall for is_expressing_opinion: {recall}")
print(f"F1 Score for is_expressing_opinion: {f1}")
