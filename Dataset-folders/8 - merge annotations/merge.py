import json

# Load the first JSON file
with open('donation_all_entities_output.json', 'r', encoding='utf-8') as f:
    gpt_output = json.load(f)

# Load the second JSON file
with open('entity_donation_claim_mapping.json', 'r', encoding='utf-8') as f:
    mapping = json.load(f)

# Function to merge data from the second JSON into the first JSON
def merge_data(gpt_output, mapping):
    final_doc = {}
    for doc_id, doc_info in gpt_output.items():
        final_doc[doc_id] = {}

        # Merge document_info first
        if doc_id in mapping and 'document_info' in mapping[doc_id]:
            final_doc[doc_id]['document_info'] = mapping[doc_id]['document_info']
        
        # Merge entities from gpt_output
        for entity, info in doc_info.items():
            if entity == 'document_info':
                continue

            final_doc[doc_id][entity] = info

            # If the entity exists in the mapping, add its info and claims
            if doc_id in mapping and 'entities' in mapping[doc_id] and entity in mapping[doc_id]['entities']:
                entity_info = mapping[doc_id]['entities'][entity].get('entity_info', {})
                final_doc[doc_id][entity]['entity_info'] = entity_info

                claims = mapping[doc_id]['entities'][entity].get('claims', [])
                if 'claims' not in final_doc[doc_id][entity]:
                    final_doc[doc_id][entity]['claims'] = claims
                else:
                    final_doc[doc_id][entity]['claims'].extend(claims)
        
        # Add entities from mapping that are not in gpt_output
        if doc_id in mapping and 'entities' in mapping[doc_id]:
            for entity, entity_info in mapping[doc_id]['entities'].items():
                if entity not in final_doc[doc_id]:
                    final_doc[doc_id][entity] = entity_info

    return final_doc

# Merge the data
merged_data = merge_data(gpt_output, mapping)

# Save the updated JSON
with open('final_donation_document.json', 'w', encoding='utf-8') as f:
    json.dump(merged_data, f, indent=4, ensure_ascii=False)

print("Merged data successfully!")
