import json

# Define the path to your input JSON file
input_file_path = 'chunked_forgeries_corpus_w_entities.json'

# Load the JSON file with UTF-8 encoding
with open(input_file_path, 'r', encoding='utf-8') as file:
    documents = json.load(file)

# Function to transform the document structure
def transform_documents(documents):
    transformed = []
    for doc in documents:
        transformed_doc = {
            "Page ID": doc["Page ID"],
            "Source": doc["Source"],
            "Page URL": doc["Page URL"],
            "Document description": doc["Document description"],
            "Document claims": doc["Document claims"],
            "Chunks": []
        }
        for i, chunk in enumerate(doc["Chunks"]["claims"], start=1):
            valid_entities = [ent for ent in chunk.get("entities", []) if ent["text"] != "NER model"]
            grouped_entities = {}
            for ent in valid_entities:
                if ent["text"] in grouped_entities:
                    grouped_entities[ent["text"]].add(ent["label"])
                else:
                    grouped_entities[ent["text"]] = {ent["label"]}
            grouped_entities_list = [{"text": text, "labels": list(labels)} for text, labels in grouped_entities.items()]
            transformed_chunk = {
                "claim-id": f"{doc['Page ID']}-{i:03}",
                "claim": chunk["claim"],
                "bibliography": chunk.get("bibliography", []),
                "entities": grouped_entities_list
            }
            transformed_doc["Chunks"].append(transformed_chunk)
        transformed.append(transformed_doc)
    return transformed

# Transform the documents
transformed_documents = transform_documents(documents)

# Output the transformed JSON to a file
output_file_path = 'chunked_forgeries_corpus_w_only_entities.json'
with open(output_file_path, 'w', encoding='utf-8') as file:
    json.dump(transformed_documents, file, ensure_ascii=False, indent=4)

# Print the output to verify
print(json.dumps(transformed_documents, ensure_ascii=False, indent=4))
