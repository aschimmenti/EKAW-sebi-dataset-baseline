import json
import requests

def get_wikidata_info(entity_name):
    # Query Wikidata for the entity
    url = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbsearchentities",
        "format": "json",
        "language": "en",
        "search": entity_name
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    # Check if any entities were found
    if not data['search']:
        return None
    
    # Get the Wikidata ID of the first result
    wikidata_id = data['search'][0]['id']
    
    # Query Wikidata for the properties (P106, P27, P569, P570, P31)
    properties = ["P106", "P27", "P569", "P570", "P31"]
    entity_info = {"wikidata_id": wikidata_id}
    
    # Fetch labels, descriptions, and aliases
    url = f"https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbgetentities",
        "format": "json",
        "ids": wikidata_id,
        "props": "labels|descriptions|aliases",
        "languages": "en"
    }
    response = requests.get(url, params=params)
    entity_data = response.json()
    entity = entity_data['entities'][wikidata_id]
    
    # Get label
    if 'en' in entity.get('labels', {}):
        entity_info["label"] = entity['labels']['en']['value']
    
    # Get description
    if 'en' in entity.get('descriptions', {}):
        entity_info["description"] = entity['descriptions']['en']['value']
    
    # Get aliases
    if 'en' in entity.get('aliases', {}):
        entity_info["also_known_as"] = [alias['value'] for alias in entity['aliases']['en']]
    
    for prop in properties:
        url = f"https://www.wikidata.org/w/api.php"
        params = {
            "action": "wbgetclaims",
            "format": "json",
            "entity": wikidata_id,
            "property": prop
        }
        response = requests.get(url, params=params)
        data = response.json()
        
        # Check if the property exists
        if prop not in data.get('claims', {}):
            continue
        
        # Get the property values
        values = []
        for claim in data['claims'][prop]:
            if 'datavalue' in claim['mainsnak']:
                value_data = claim['mainsnak']['datavalue']['value']
                value_id = value_data.get('id', None)
                value_time = value_data.get('time', None)
                
                if value_id:
                    url = f"https://www.wikidata.org/w/api.php"
                    params = {
                        "action": "wbgetentities",
                        "format": "json",
                        "ids": value_id,
                        "props": "labels",
                        "languages": "en"
                    }
                    response = requests.get(url, params=params)
                    value_data = response.json()
                    if 'en' in value_data['entities'][value_id]['labels']:
                        value_label = value_data['entities'][value_id]['labels']['en']['value']
                        values.append(value_label)
                elif value_time:
                    values.append(value_time)
        
        if prop == "P106":
            entity_info["occupation"] = ", ".join(values)
        elif prop == "P27":
            entity_info["country of citizenship"] = ", ".join(values)
        elif prop == "P569":
            entity_info["date of birth"] = values[0] if values else None
        elif prop == "P570":
            entity_info["date of death"] = values[0] if values else None
        elif prop == "P31":
            entity_info["instance_of"] = ", ".join(values)
    
    return entity_info

# Load the JSON file
with open('resolved_entities_input.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Process each document
for document in data:
    document_id = document["Page ID"]
    
    # Process each chunk
    for chunk in document['Chunks']:
        for entity in chunk.get('entities', []):
            resolved_label = entity.get("resolved_label", entity["text"])
            entity_info = get_wikidata_info(resolved_label)
            if entity_info:
                entity.update(entity_info)
                # Print the updated entity information
                print(json.dumps(entity, ensure_ascii=False, indent=4))

# Save the updated JSON
with open('updated_entities_output.json', 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=4)
