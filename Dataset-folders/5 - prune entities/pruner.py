import json

def prune_entities(data):
    for document in data:
        for chunk in document['Chunks']:
            pruned_entities = []
            for entity in chunk.get('entities', []):
                labels = [label.lower() for label in entity.get('labels', [])]
                instance_of = entity.get('instance_of', '').lower()
                
                # If the entity is labeled as 'group' or 'organisation' and is an instance of 'person', prune it
                if any(label in ['group', 'organisation'] for label in labels) and instance_of == 'human':
                    print("Pruning entity (group/organisation with instance_of 'human'):")
                    print(json.dumps(entity, ensure_ascii=False, indent=4))
                    continue  # Prune this entity
                
                # If the entity is labeled as 'person' and is not an instance of 'human', remove Wikidata information
                if 'person' in labels and instance_of != 'human':
                    print("Removing Wikidata information (person with incorrect instance_of):")
                    print(json.dumps(entity, ensure_ascii=False, indent=4))
                    entity.pop('wikidata_id', None)
                    entity.pop('label', None)
                    entity.pop('description', None)
                    entity.pop('occupation', None)
                    entity.pop('country of citizenship', None)
                    entity.pop('date of birth', None)
                    entity.pop('date of death', None)
                    entity.pop('instance_of', None)
                
                pruned_entities.append(entity)
            chunk['entities'] = pruned_entities
    return data

# Load the JSON file
with open('unpruned_input.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Prune entities
pruned_data = prune_entities(data)


# Save the pruned data to a new file
with open('pruned_entities_output.json', 'w', encoding='utf-8') as file:
    json.dump(pruned_data, file, ensure_ascii=False, indent=4)
