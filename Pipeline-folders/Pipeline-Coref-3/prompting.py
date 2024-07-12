import json
import openai
from openai import OpenAI

from datetime import datetime
import os
import getpass

os.environ["OPENAI_API_KEY"] = getpass.getpass("OpenAI API Key:")
openai.api_key = os.environ["OPENAI_API_KEY"]

# Define the prompt template
prompt_template = """
You are an expert coreference resolution system + sentence classifier. Given an entity, you find each sentence in which they are mentioned, speak or ar referred to by performing some kind of coreference resolution. Your reasoning to execute the task successfully shall be: 
1. Is {entity} mentioned, addressed or are they speaking in the text? Check the name, surname, and other ways the entity is named. Is the entity inside the text at all? 
2. If {entity} is found in the text, find the boundaries of the sentence. If the sentence is too simple, try to add a sentence more on the left (or in the right). The sentence must be, as much as possible, self-explanatory. Return the sentence even if the entity is only mentioned slightly (e.g. in a list or simply addressed.)
3. Do not apply any change to the sentence structure, grammar, errors or any other change that you might think to be useful for me. 
4. Add each sentence or paragraph as a "claim" following the JSON structure. Answer with the JSON and only with the JSON.
Identify and list each sentence where the given entity ({entity}) is speaking. Return each sentence along with its associated bibliography references (if present in the text) as elements in a JSON array. 
Below you are provided an example of this task and its execution:
EXAMPLE: 
EXAMPLE ENTITY: Entity: "John Doe, a literary historian"
EXAMPLE INPUT: [...] The debate over the authorship of Shakespeare's plays has been ongoing for centuries. John Doe, a prominent literary historian, argues that there is substantial evidence to suggest that the plays were actually written by Francis Bacon. He points out that the stylistic and thematic similarities between Bacon's known works and the Shakespearean canon are too significant to ignore. Additionally, Doe highlights that historical records from the period often reference Bacon's involvement in theatrical productions. Jane Smith, another historian, disputes this claim and believes the evidence is inconclusive. In his book, "The Real Shakespeare," John Doe claims that several coded messages within the plays point directly to Bacon as the true author. However, some experts, like Richard Roe, argue that these codes are open to interpretation and do not definitively prove Bacon's authorship. Despite some criticism, his findings have gained considerable attention in the academic community. [1][2][3] Many scholars continue to support the traditional view that Shakespeare himself wrote the plays.[...]

EXAMPLE OUTPUT: 
{{
  "John Doe": [
    {{
      "claim": "John Doe argues that there is substantial evidence to suggest that the plays were actually written by Francis Bacon.",
      "bibliography": []
    }},
    {{
      "claim": "He points out that the stylistic and thematic similarities between Bacon's known works and the Shakespearean canon are too significant to ignore.",
      "bibliography": []
    }},
    {{
      "claim": "Doe highlights that historical records from the period often reference Bacon's involvement in theatrical productions.",
      "bibliography": []
    }},
    {{
      "claim": "In his book, 'The Real Shakespeare,' John Doe claims that several coded messages within the plays point directly to Bacon as the true author.",
      "bibliography": []
    }},
    {{
      "claim": "Despite some criticism, his findings have gained considerable attention in the academic community.",
      "bibliography": [
        "[1]",
        "[2]",
        "[3]"
      ]
    }}
  ]
}}


SCHEMA TO FILL:
{{
  "<Entity Name>": [
    {{
      "claim": "<Sentence where the entity is making a claim>",
      "bibliography": [
        "<Bibliographic reference 1>",
        "<Bibliographic reference 2>",
        ...
      ]
    }},
    {{
      "claim": "<Another sentence where the entity is making a claim>",
      "bibliography": [
        "<Bibliographic reference 1>",
        ...
      ]
    }},
    ...
  ]
}}

Now, perform the task over the following content:
TEXT:
Entity: {entity}, {entity_context}
TEXT INPUT: 
{text} 
YOUR ANSWER:
"""


# Function to convert Wikidata date format to a readable string
def convert_wikidata_date(wikidata_date):
    try:
        return datetime.strptime(wikidata_date[1:11], "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        return "Unknown"


# Load the JSON data from manual_annotation.json
# with open("manual_annotation.json", "r", encoding="utf-8") as f:
with open("manual_annotation_doc18.json", "r", encoding="utf-8") as f:
    manual_annotation = json.load(f)

# Load the JSON data from updated_entities.json
with open("updated_entities_doc18.json", "r", encoding="utf-8") as f:
    updated_entities = json.load(f)

# Create output directory if it doesn't exist
output_dir = "output-by-document"
os.makedirs(output_dir, exist_ok=True)

# Store the results for all entities
all_entities_output = {}

# Process each document
for document_id, document_data in manual_annotation.items():
    document_info = document_data["document_info"]
    document_description = document_info["Document description"]
    document_claims = document_info["Document claims"]

    # Merge document description and document claims into text
    text_to_analyze = document_description + " " + document_claims
    print(text_to_analyze)
    entities = updated_entities.get(document_id, {}).get("entities", [])

    # Store the results for the current document
    document_output = {}

    # Process each entity
    for entity in entities:
        entity_name = entity["text"]
        entity_info = entity
        name = entity_info.get("label", entity_info.get("text", "Unknown"))
        description = entity_info.get("description", "No description available")
        aka_list = entity_info.get("also_known_as", [])[:3]
        occupation = entity_info.get("occupation", "No occupation listed")
        date_of_birth = entity_info.get("date of birth", "")
        date_of_death = entity_info.get("date of death", "")

        # Convert dates
        date_of_birth = (
            convert_wikidata_date(date_of_birth) if date_of_birth else "Unknown"
        )
        date_of_death = (
            convert_wikidata_date(date_of_death) if date_of_death else "Unknown"
        )

        aka_text = ", ".join(aka_list) if aka_list else "No other known names"
        life_span = (
            f"{date_of_birth.split('-')[0]}-{date_of_death.split('-')[0]}"
            if date_of_birth != "Unknown" and date_of_death != "Unknown"
            else "Dates not available"
        )
        instance_of = entity_info.get("instance_of", "").lower()

        # Check if the entity is a human
        if instance_of == "human":
            entity_context = f"{name} ({life_span}) : {description}. Also known as {aka_text}, {occupation}."
        else:
            entity_context = "No additional context available."

        formatted_prompt = prompt_template.format(
            entity=entity_name, entity_context=entity_context, text=text_to_analyze
        )

        # Make the request to OpenAI
        client = OpenAI(api_key=openai.api_key)
        response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a sentence classifier. Your task is to identify and extract each sentence where a given entity is speaking and return each sentence as a list."},
                    {"role": "user", "content": formatted_prompt}
                ],
                response_format={"type": "json_object"}
            )

        # Parse the response
        raw_response = response.choices[0].message.content
        entity_output = json.loads(raw_response)

        # Add the entity output to the document output dictionary
        document_output[entity_name] = entity_output
        document_output[entity_name]['entity_info'] = entity_info  # Include the original entity information

    # Save the output for the current document to a separate JSON file
    document_output_filename = os.path.join(output_dir, f"{document_id}.json")
    with open(document_output_filename, "w", encoding="utf-8") as f:
        json.dump(document_output, f, ensure_ascii=False, indent=4)

    # Add the document output to the all_entities_output dictionary
    all_entities_output[document_id] = document_output

# Save the combined output to a single JSON file
output_filename = "doc18_final_output.json"
with open(output_filename, "w", encoding="utf-8") as f:
    json.dump(all_entities_output, f, ensure_ascii=False, indent=4)

print(
    f"All entity responses saved to {output_filename} and individual files in {output_dir}"
)
