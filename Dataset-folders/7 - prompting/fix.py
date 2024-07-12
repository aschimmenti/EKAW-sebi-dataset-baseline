import json

# Load the JSON files
with open("chunked_wikipedia_forgeries_corpus.json", 'r', encoding="utf-8") as f:
    first_json = json.load(f)

with open('entity_claim_mapping.json', 'r', encoding="utf-8") as f:
    second_json = json.load(f)

# Function to get citations from the first JSON
def get_citations(claim_text, chunks):
    for claim in chunks['claims']:
        if claim['claim'] == claim_text:
            return claim['bibliography']
    return []

# Update the second JSON with citations
for doc in first_json:
    page_id = doc['Page ID']
    if page_id in second_json:
        chunks = doc['Chunks']
        for entity, entity_data in second_json[page_id]['entities'].items():
            for claim in entity_data['claims']:
                citations = get_citations(claim['claim'], chunks)
                claim['bibliography'] = citations

# Save the updated JSON
with open('bibl_mapping.json', 'w', encoding='utf-8') as f:
    json.dump(second_json, f, indent=4, ensure_ascii=False)

print("Citations added successfully!")
