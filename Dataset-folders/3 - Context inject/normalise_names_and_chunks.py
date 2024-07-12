import json

# Define the path to your input JSON file
input_file_path = 'input.json'

# Load the JSON file with UTF-8 encoding
with open(input_file_path, 'r', encoding='utf-8') as file:
    documents = json.load(file)

# Function to normalize text by removing points and converting to lowercase
def normalize(text):
    return text.replace('.', '').lower()

# Function to check if one name is an abbreviation or a part of another name
def is_abbreviation_or_part_of(abbreviation, full_name):
    abbr_normalized = normalize(abbreviation)
    full_name_normalized = normalize(full_name)
    abbr_parts = abbr_normalized.split()
    full_name_parts = full_name_normalized.split()

    # Check if each part of the abbreviation matches the corresponding part of the full name
    if len(abbr_parts) > 1:
        if len(abbr_parts) > len(full_name_parts):
            return False
        return all(
            abbr_parts[i] == full_name_parts[i][0] or abbr_parts[i] == full_name_parts[i]
            for i in range(len(abbr_parts))
        )
    
    # For single part abbreviations
    if len(abbr_parts) == 1:
        return any(
            abbr_parts[0] == full_name_part[0] or abbr_parts[0] == full_name_part
            for full_name_part in full_name_parts
        )

    return False

# Function to find and resolve partial names within a document
def resolve_partial_names(doc):
    # Collect all entities with their normalized names
    entities = []
    for chunk in doc["Chunks"]:
        for entity in chunk["entities"]:
            entities.append({
                "original_text": entity["text"],
                "entity": entity
            })

    # Create a map to store resolved labels
    resolved_map = {}

    # Check each entity against all other entities to find fits
    for ent1 in entities:
        for ent2 in entities:
            if ent1 != ent2 and ent1["entity"]["labels"] == ent2["entity"]["labels"] and is_abbreviation_or_part_of(ent1["original_text"], ent2["original_text"]):
                if ent1["original_text"] not in resolved_map:
                    resolved_map[ent1["original_text"]] = ent2["original_text"]
                elif normalize(resolved_map[ent1["original_text"]]) not in normalize(ent2["original_text"]):
                    resolved_map[ent1["original_text"]] = ent2["original_text"]

    # Update entities with resolved labels
    for chunk in doc["Chunks"]:
        for entity in chunk["entities"]:
            if entity["text"] in resolved_map:
                entity["resolved_label"] = resolved_map[entity["text"]]
            else:
                entity["resolved_label"] = entity["text"]

# Apply the function to all documents
for doc in documents:
    resolve_partial_names(doc)

# Collect tuples of entity text and resolved text where they are different
differences = []
for doc in documents:
    for chunk in doc["Chunks"]:
        for entity in chunk["entities"]:
            if entity["text"] != entity["resolved_label"]:
                differences.append((entity["text"], entity["resolved_label"]))

# Output the transformed JSON to a file
output_file_path = 'chunked_forgeries_corpus_w_only_entities_resolved.json'
with open(output_file_path, 'w', encoding='utf-8') as file:
    json.dump(documents, file, ensure_ascii=False, indent=4)

# Print the differences
for original, resolved in differences:
    print(f"Original: '{original}', Resolved: '{resolved}'")
