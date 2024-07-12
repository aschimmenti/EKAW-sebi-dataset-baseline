from gliner import GLiNER
import json

# Initialize GLiNER with the base model
model = GLiNER.from_pretrained("knowledgator/gliner-multitask-large-v0.5")

# Sample prompt for entity prediction
prompt = """INSTRUCTION: You are a specialised NER model. Your task is to find entities that especially express, state, talk about or have been reported to express one or opinions. The following text has been already coreferenced, so you might find some redundancy or small mistake. 
Your task is to select entities of the given classes that relate to the above description.
TEXT: """

# Labels for entity prediction
labels = ["Person", "Organisation", "Group"]

# Define file paths
json_file_path = 'chunked_wikipedia_forgeries_corpus.json'
output_json_file_path = 'chunked_forgeries_corpus_w_entities.json'

# Define a function to process the text and extract entities
def extract_entities(text, labels):
    entities = model.predict_entities(text, labels=labels, threshold=0.5)
    print(f"Extracted entities from text: {entities}")
    return entities

# Function to clean and standardize entity names
def clean_entity(entity):
    return entity.strip().lower()

# Function to perform entity resolution across the entire document
def resolve_entities(entities):
    resolved = {}
    for entity in entities:
        cleaned_entity = clean_entity(entity)
        if cleaned_entity not in resolved:
            resolved[cleaned_entity] = entity
    return resolved

# Load the JSON file
with open(json_file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Process each document
for item in data:
    print(f"Processing document: {item['Page ID']}")
    all_entities = []
    
    # Extract entities from each chunk
    for chunk in item['Chunks']['claims']:
        text = prompt + chunk['claim']
        entities = extract_entities(text, labels)
        all_entities.extend([e['text'] for e in entities])  # Assuming 'text' contains the entity name
        chunk['entities'] = entities

    # Resolve entities across the entire document
    resolved_entities = resolve_entities(all_entities)
    print(f"Resolved entities: {resolved_entities}")

    # Replace entities in chunks with resolved entities
    for chunk in item['Chunks']['claims']:
        for entity in chunk['entities']:
            cleaned_entity = clean_entity(entity['text'])  # Assuming 'text' contains the entity name
            if cleaned_entity in resolved_entities:
                entity['resolved'] = resolved_entities[cleaned_entity]

# Save the modified JSON to a new file
with open(output_json_file_path, 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=4)

print("Entities resolved and added to chunks and saved to chunked_forgeries_corpus_w_entities.json")
