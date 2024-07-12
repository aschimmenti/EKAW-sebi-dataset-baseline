import json

# Load the JSON file
with open('entity_claim_mapping_right.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Function to find and add sentences before and after the claim in the document text
def enrich_claim(claim_text, document_text):
    sentences = document_text.split('. ')
    enriched_claim = claim_text
    for i, sentence in enumerate(sentences):
        if claim_text in sentence:
            # Add the sentence before the claim if available
            if i > 0:
                enriched_claim = sentences[i - 1] + '. ' + enriched_claim
            # Add the sentence after the claim if available
            if i < len(sentences) - 1:
                enriched_claim = enriched_claim + '. ' + sentences[i + 1]
            return enriched_claim
    return enriched_claim

# Iterate through the documents and claims to enrich them
for doc_id, doc_data in data.items():
    document_text = doc_data['document_info']['Document claims']
    for entity, entity_data in doc_data['entities'].items():
        for claim in entity_data['claims']:
            claim_text = claim['claim']
            if len(claim_text.split()) < 20:  # Assuming a claim is short if it's less than 20 words
                enriched_claim = enrich_claim(claim_text, document_text)
                claim['claim'] = enriched_claim

# Save the updated JSON
with open('enriched_entity_richer_claims_mapping.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print("Enriched claims successfully!")
