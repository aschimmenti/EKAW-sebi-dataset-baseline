import json

def merge_entity_info(existing_entity, new_entity):
    merged_entity = existing_entity.copy()
    for key, value in new_entity.items():
        if key in merged_entity and merged_entity[key] != value:
            # If there is a conflict, retain both versions with a _2 suffix for the new key
            merged_entity[key + "_2"] = value
        else:
            merged_entity[key] = value
    return merged_entity

def build_entity_claim_mapping(data):
    entity_claim_map = {}
    
    for document in data:
        doc_id = document['Page ID']
        document_info = {
            "Source": document.get('Source'),
            "Page URL": document.get('Page URL'),
            "Document description": document.get('Document description'),
            "Document claims": document.get('Document claims')
        }
        entity_map = {}
        
        for chunk in document['Chunks']:
            claim_id = chunk['claim-id']
            claim_text = chunk['claim']
            
            for entity in chunk.get('entities', []):
                resolved_label = entity.get('resolved_label', entity['text'])
                
                if resolved_label in entity_map:
                    existing_entity = entity_map[resolved_label]['entity_info']
                    entity_map[resolved_label]['entity_info'] = merge_entity_info(existing_entity, entity)
                else:
                    entity_map[resolved_label] = {
                        "entity_info": entity,
                        "claims": []
                    }
                
                entity_map[resolved_label]['claims'].append({
                    "claim-id": claim_id,
                    "claim": claim_text
                })
        
        entity_claim_map[doc_id] = {
            "document_info": document_info,
            "entities": entity_map
        }
    
    return entity_claim_map

# Load the JSON file
with open('clean_input.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Build the entity-claim mapping
entity_claim_map = build_entity_claim_mapping(data)

# Print the entity-claim mapping
print("Entity-Claim Mapping:")
print(json.dumps(entity_claim_map, ensure_ascii=False, indent=4))

# Save the entity-claim mapping to a new file
with open('entity_claim_mapping.json', 'w', encoding='utf-8') as file:
    json.dump(entity_claim_map, file, ensure_ascii=False, indent=4)
