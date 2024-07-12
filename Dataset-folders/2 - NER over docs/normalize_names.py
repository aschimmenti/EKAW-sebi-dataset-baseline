import json
from collections import defaultdict

# Load the JSON data from the file
with open('chunked_wikipedia_forgeries_corpus.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Extract all entities from the claims while keeping track of the claim number
all_entities = []

for claim_id, claim in enumerate(data['Chunks']['claims']):
    if 'entities' in claim:
        for entity in claim['entities']:
            all_entities.append((entity['text'], claim_id))
        # Ensure to add the claim_id even if there are no entities
        if not claim['entities']:
            all_entities.append((None, claim_id))

# Print all entities for debugging purposes
print("Extracted entities:", all_entities)

# Function to clean and normalize names
def clean_name(name):
    return ''.join(e for e in name if e.isalnum()).lower()

# Perform basic string containment check to cluster similar entities
clusters = defaultdict(list)
seen = set()
cluster_id = 0

for i, (name1, claim_id1) in enumerate(all_entities):
    if name1 is None or name1 in seen:
        continue
    clusters[cluster_id].append(name1)
    seen.add(name1)
    name1_clean = clean_name(name1)
    for name2, claim_id2 in all_entities[i+1:]:
        if name2 is None or name2 in seen:
            continue
        name2_clean = clean_name(name2)
        if name1_clean in name2_clean or name2_clean in name1_clean:
            clusters[cluster_id].append(name2)
            seen.add(name2)
    cluster_id += 1

# Print the clusters of similar entities
print("Clusters of similar entities:")
for cluster_id, names in clusters.items():
    print(f"Cluster {cluster_id}: {set(names)}")
