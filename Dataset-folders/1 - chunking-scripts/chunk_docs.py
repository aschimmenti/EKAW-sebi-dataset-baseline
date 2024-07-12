import json
import re

# Define file paths
json_file_path = 'wikipedia_forgeries_corpus.json'
chunked_output_path = 'chunked_wikipedia_forgeries_corpus.json'

def chunk_document_claims(text):
    pattern = re.compile(r'\[\d+\]')
    matches = list(pattern.finditer(text))

    # Initialize variables
    output = {'claims': []}  # Create the main dictionary to hold all items
    previous_end = 0  # Track the end of the last match

    for i, match in enumerate(matches):
        start, end = match.span()  # Start and end indices of the current match
        if i == 0 or previous_end != start:
            preceding_text = text[previous_end:start].strip()  # Text before the current match
            # Add a new dictionary entry for each new section of text
            output['claims'].append({'claim': preceding_text, 'bibliography': []})

        # Append current bracket to the latest text entry
        output['claims'][-1]['bibliography'].append(text[start:end])

        previous_end = end  # Update the end of the last match

    # Handle any remaining text after the last match
    if previous_end < len(text):
        trailing_text = text[previous_end:].strip()
        if trailing_text:  # Ensure trailing text isn't just whitespace
            output['claims'].append({'claim': trailing_text, 'bibliography': []})

    # Output the structured data
    return output

def process_json():
    # Load JSON data with utf-8 encoding
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    # Process each document and chunk their claims
    for document in data:
        document_description = document.get("Document description", "")
        document_claims = document.get("Document claims", "")
        
        combined_text = document_description + " " + document_claims
        if combined_text:
            document['Chunks'] = chunk_document_claims(combined_text)
        else:
            document['Chunks'] = []
    
    # Save the modified data to a new JSON file
    with open(chunked_output_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# Run the script
process_json()
