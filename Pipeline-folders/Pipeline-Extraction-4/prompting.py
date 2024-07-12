import json
import openai
from openai import OpenAI
from datetime import datetime
import os
import sys 
import os
import getpass

os.environ["OPENAI_API_KEY"] = getpass.getpass("OpenAI API Key:")
openai.api_key = os.environ["OPENAI_API_KEY"]

# Define the prompt template
prompt_template = """

CONTEXT:
Document abstract: {document_abstract} 
Entity: {entity}, {entity_context} 
TEXT INPUT: 
{text} 

Extract the following information step by step:
Is {entity} mentioned as having an opinion about the given document? First, determine if {entity} is reported in the given text. Then, check if {entity}, directly or indirectly, has been credited or says something about the document. Return 'True' or 'False'. If False, you can use null in all the following questions. 
Does {entity} think the document is authentic, a forgery, or are they only suspicious of its authenticity? First, identify any clue from the evaluative statements that might justify this choice. Check if the entity is talking of the document in a positive, negative or uncertain way. Infer if the entities, from their description and from the sentence(s) you can see, think the document could be authentic or not, even if not saying it explicitly. Then, return 'authentic', 'forgery', or 'suspicious'. 
Given the previous answer, does {entity} point out any evidence or feature that might justify the previous choice? Look for specific characteristics or evidence provided by {entity} to support their opinion, and choose one or more of the the following features: authentication marks / chronology and dating / content / document provenance / format (spacing, signs) /  handwriting  / historical context / illustration or other graphical device /  indentation / ink  / inter-punctuation / interpolations / legal formulas  / list of witnesses /  material support / metre and style / original document  / orthography / sigillum or seal / content / language.
Return the feature(s) with one or more of the following evaluations. 
- reliability: is the analysed feature trustworthy? e.g. the list of witness, the document provenance... (return: True/False)
- completeness: is the document complete of all its parts or elements? i.e., is it partially broken, in a bad state... (return:True/False)
- consistency: is the analysed feature consistent with other information? For example, if the ink is not consistent with the times, if the handwriting not consistent with other documents... (return: True/False)
- presence: some feature may be reported as present or absent. If the feature is original document, interpolation, list of witnesses, legal formulas, sigillum or seal, document provenance. (return: True/False)
- veridicality: is the analysed feature truthful and accurate? For example, if the content is not thruthful (return: True/False)

Does {entity} provide an intention for why the document might have been forged? Check if the entity mentions any motives or circumstances that might explain a forgery. E.g. money, propaganda, political gain. Return only terms or 'null'. 
Does {entity} attribute a possible author of the document/forgery? See if the entity identifies any individuals or groups as the potential author of the document (or of the forgery). Return only names, terms or 'null'. 
Does {entity} attribute a possible date for the creation/forgery? Look for any dates or periods when {entity} thinks the forgery might have occurred. Return only a date or 'null'. 
Does {entity} attribute a possible location of the creation/forgery? Identify if {entity} mentions any specific places where the forgery might have taken place. Return only a place or 'null'. 
Did {entity} study the document from a specific perspective? Determine if {entity} analyzed the document using a particular academic or methodological approach. Use one or more of the following terms or 'null':
Scientific analysis, Historical analysis, Philologic analysis, Diplomatic analysis, Paleographic analysis, Literary analysis. Before choosing a term, reason if the opinion might align with one of these terms.

Example 1:
CONTEXT:
Document abstract: Posthumous Diary (Diario postumo) is a series of poems attributed to the Italian poet Eugenio Montale which first appeared in full in 1996, after the poet's death. 
Entity: Federico Condello (Verona, 1973), works as classical philologist, university professor
TEXT INPUT: 
The controversy was reignited in 2014 with the publication of the book 'I filologi e gli angeli. È di Eugenio Montale il Diario postumo?' by Federico Condello, which thoroughly analyzes the editorial history of the Diario, highlighting various inconsistencies. 'Montale e pseudo Montale. Autopsia del 'Diario postumo'. This volume includes numerous linguistic, metrical, and stylistic analyses, as well as some documentary investigations that, referring to the materials used (primarily facsimiles of the autographed manuscripts of the Diario) or to letters and notes preserved in the Scheiwiller Archive (now at the Apice Center of the University of Milan), allow for the reconstruction of certain periods of Annalisa Cima's activity, especially between 1981 and 1986. From these documents, no elements emerge in favor of the thesis of authenticity, while some data conflict with all the reconstructions proposed in the various statements of the Diario's dedicatee.
{{
  \"is_expressing_opinion\": true,
  \"opinion_evaluation\": \"suspicious\",
  \"opinion_evidence_provided\": [
    {{
      \"feature\": \"chronology and dating\",
      \"reliability\": false
    }},
    {{
      \"feature\": \"metre and style\",
      \"completeness\": false,
      \"consistency\": false
    }}
  ],
  \"opinion_reason\": null,
  \"opinion_document_author\": [
    \"Annalisa Cima\"
  ],
  \"opinion_document_date\": [
    \"1981-1986\"
  ],
  \"opinion_document_location\": null,
  \"opinion_specific_perspective\": [
    \"Philologic analysis\",
    \"Literary analysis\"
  ]
}}

Example 2:
CONTEXT:
Document Abstract: The Tulli Papyrus is an apocryphal document in the form of an ancient papyrus written in hieratic script, discovered in Egypt in 1934, which purportedly contains descriptions of strange sightings of lights and objects in the sky. After being cited for decades as a "mysterious" and "anachronistic" object, in 2006, following analysis by enthusiasts and scholars from an online community, it was definitively established to be a fake, composed of phrases taken from Alan Gardiner's Egyptian Grammar, a well-known grammar of the Egyptian language.
Entity: Franco Brussino, egyptologist, linguist
TEXT INPUT: The papyrus text was subjected to analysis in April 2006 by enthusiasts and scholars: through an Italian online community (egittologia.net), the "case" began to be studied starting from a new translation of the text, derived from the image published by De Rachewiltz. Franco Brussino at first thought the document to be authentic. During the translation, however, being an expert in Egyptology, Brussino noticed a few inconsistencies: first, the similarity between some passages of the papyrus and phrases from known texts. The text also lacked any official marking that would be required from the bureaucratic source. Also, through simple radiocarbon dating, the papyrus could not have bee written before 1880, and the ink use was probably industrially produced. Then, by looking at the sources regarding the papyrus's finding, he noticed a lot of inchoerencies in the archeological report. Bibliographic research led to the discovery of the same phrases from the incriminated papyrus in a fundamental text on the Egyptian language, Sir Alan H. Gardiner's Egyptian Grammar, published in 1927 and therefore preceding the discovery of the papyrus.
{{
  \"is_expressing_opinion\": true,
  \"opinion_evaluation\": \"forgery\",
  \"opinion_evidence_provided\": [
    {{
      \"feature\": \"language\",
      \"consistency\": false,
      \"veridicality\": false
    }},
    {{
      \"feature\": \"material support\",
      \"reliability\": false
    }},
    {{
      \"feature\": \"document provenance\", 
      \"reliability\": false,
      \"consistency\": false
    }},
    {{
      \"feature\": \"ink\", 
      \"reliability\": false
    }},
    {{
      \"feature\": \"sigillum or seal\", 
      \"presence\": false
    }}
  ],
  \"opinion_reason\": [
    \"phrases taken from known texts\"
  ],
  \"opinion_document_author\": null,
  \"opinion_document_date\": [
    \"after 1927\"
    ],
  \"opinion_document_location\": null,
  \"opinion_specific_perspective\": [
    \"Philologic analysis\",
    \"Literary analysis\",
    \"Scientific analysis\"
  ]
}}

Example 3:
CONTEXT:
Document Abstract: The Magna Carta Redux is a purported medieval charter that claims to be a lost extension of the original Magna Carta, discovered in the early 20th century by some members of the Parliament in the House of Commons Library. This document allegedly provides additional rights and privileges to the barons of England and extends additional taxation to commoners. It was supposedly written in 1217, two years after the original Magna Carta. 
Entity: Dr. Emily Richards (born 1980), historian and manuscript specialist
TEXT INPUT: In her 2020 paper "The Forgery of the Magna Carta Redux," Dr. Emily Richards presents a detailed critique of the document's authenticity. Richards points to several discrepancies in the handwriting, composition, and legal formulas used. No illumination or mark was to be found in the manuscript, which would be rare for such an important document. She highlights that the handwriting does not match any known samples from the 13th century, and the ink contains chemical compounds that were not available until the 19th century. The manuscript was also exceptionally well-preserved for the time of its finding. Additionally, no other document from that period ever mentioned or reported any of the laws stated in the Redux charter. Richards concludes that the manuscript was probably an attempt by some members of Parliament to reignite the debate around the hereditary privileges of England's nobility.

{{
  \"is_expressing_opinion\": true,
  \"opinion_evaluation\": \"forgery\",
  \"opinion_evidence_provided\": [
    {{
      \"feature\": \"handwriting\",
      \"consistency\": false
    }},
    {{
      \"feature\": \"material support\",
      \"reliability\": false
    }},
    {{
      \"feature\": \"legal formulas\",
      \"reliability\": false,
      \"consistency\": false
    }},
    {{
      \"feature\": \"illustration or other graphical device\", 
      \"presence\": false
    }},
    {{
      \"feature\": \"ink\", 
      \"reliability\": false
    }},
    {{
      \"feature\": \"sigillum or seal\", 
      \"presence\": false
    }},
    {{
      \"feature\": \"list of witnesses\", 
      \"presence\": false
    }}
  ],
  \"opinion_reason\": [
    \"political reasons\"
  ],
  \"opinion_document_author\": [
    \"English members of the Parliament\"
    ],
  \"opinion_document_date\": null,
  \"opinion_document_location\": null,
  \"opinion_specific_perspective\": [
    \"Philologic analysis\",
    \"Scientific analysis\"
  ]
}}

Example 4:
CONTEXT:
Document Abstract: The Flower Manuscript is an allegedly medieval Polish manuscript that describes the various types of flowers sold in the Krakow market between 990 and 1100. The document has often been considered a forgery, suspected to be a publicity stunt orchestrated to attract tourists and boost the local economy.

Entity: Jan Tokarczuk (born 1945), philologist 

TEXT INPUT:
J. Tokarczuk thought it was produced for a flowerists exposition for advertising. [...] The language was not even consistent for the times. 

{{
  \"is_expressing_opinion\": true,
  \"opinion_evaluation\": \"forgery\",
  \"opinion_evidence_provided\": [
    {{
      \"feature\": \"language\",
      \"consistency\": false    
      }}
      ],
  \"opinion_reason\": [
    \"advertising\"
  ],
  \"opinion_document_author\": [
    "local merchants"
    ],
  \"opinion_document_date\": null,
  \"opinion_document_location\": null,
  \"opinion_specific_perspective\": [
    \"Philologic analysis\"  ]
}}

Return the extracted information in the given JSON format 
{{
  \"type\": \"object\",
  \"properties\": {{
    \"is_expressing_opinion\": {{
      \"type\": \"boolean\"
    }},
    \"opinion_evaluation\": {{
      \"type\": \"string\",
      \"enum\": [\"authentic\", \"forgery\", \"suspicious\"]
    }},
    \"opinion_evidence_provided\": {{
      \"type\": \"array\",
      \"items\": {{
        \"type\": \"object\",
        \"properties\": {{
          \"feature\": {{
            \"type\": \"string\",
            \"enum\": [
              \"authentication marks\",
              \"chronology and dating\",
              \"content\",
              \"document provenance\",
              \"format (spacing, signs)\",
              \"handwriting\",
              \"historical context\",
              \"illustration or other graphical device\",
              \"indentation\",
              \"ink\",
              \"inter-punctuation\",
              \"interpolations\",
              \"legal formulas\",
              \"list of witnesses\",
              \"material support\",
              \"metre and style\",
              \"original document\",
              \"orthography\",
              \"sigillum or seal\",
              \"language\"
            ]
          }},
          \"reliability\": {{
            \"type\": \"boolean\",
            \"nullable\": true
          }},
          \"completeness\": {{
            \"type\": \"boolean\",
            \"nullable\": true
          }},
          \"consistency\": {{
            \"type\": \"boolean\",
            \"nullable\": true
          }},
          \"presence\": {{
            \"type\": \"boolean\",
            \"nullable\": true
          }},
          \"veridicality\": {{
            \"type\": \"boolean\",
            \"nullable\": true
          }}
        }},
        \"required\": [\"feature\"]
      }},
      \"nullable\": true
    }},
    \"opinion_reason\": {{
      \"type\": \"array\",
      \"items\": {{
        \"type\": \"string\"
      }},
      \"nullable\": true
    }},
    \"opinion_document_author\": {{
      \"type\": \"array\",
      \"items\": {{
        \"type\": \"string\"
      }},
      \"nullable\": true
    }},
    \"opinion_document_date\": {{
      \"type\": \"array\",
      \"items\": {{
        \"type\": \"string\"
      }},
      \"nullable\": true
    }},
    \"opinion_document_location\": {{
      \"type\": \"array\",
      \"items\": {{
        \"type\": \"string\"
      }},
      \"nullable\": true
    }},
    \"opinion_specific_perspective\": {{
      \"type\": \"array\",
      \"items\": {{
        \"type\": \"string\",
        \"enum\": [
          \"Scientific analysis\",
          \"Historical analysis\",
          \"Philologic analysis\",
          \"Diplomatic analysis\",
          \"Paleographic analysis\",
          \"Literary analysis\"
        ]
      }},
      \"nullable\": true
    }}
  }},
  \"required\": [\"is_expressing_opinion\"]
}}

"""


# Function to convert Wikidata date format to a readable string
def convert_wikidata_date(wikidata_date):
    try:
        return datetime.strptime(wikidata_date[1:11], "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        return "Unknown"


# Load the JSON data from manual_annotation.json
with open("manual_annotation.json", "r", encoding="utf-8") as f:
    manual_annotation = json.load(f)

# Load the JSON data from all_entities_output.json
with open("all_entities_output.json", "r", encoding="utf-8") as f:
    all_entities_output = json.load(f)

# Create output directory if it doesn't exist
output_dir = "output-by-document"
os.makedirs(output_dir, exist_ok=True)

# Store the results for all entities
final_entities_output = {}

start_doc_id = None

if len(sys.argv) > 1:
    start_doc_id = sys.argv[1]

# Flag to indicate if we should start processing
start_processing = True if start_doc_id is None else False

# Process each document
for document_id, document_data in manual_annotation.items():
    # Check if we should start processing
    if not start_processing:
        if document_id == start_doc_id:
            start_processing = True
        else:
            continue

    document_info = document_data["document_info"]
    document_description = document_info["Document description"]

    entities = all_entities_output.get(document_id, {})

    # Store the results for the current document
    document_output = {}

    # Process each entity
    for entity_name, entity_data in entities.items():
        entity_info = entity_data.get("entity_info", {})
        claims_data = entity_data.get(entity_name, entity_data.get("claims", []))

        if not claims_data:
            print(f"No claims found for entity: {entity_name} in document: {document_id}")
            continue

        claims = [claim["claim"] for claim in claims_data]
        text_to_analyze = " [...] ".join(claims)

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
            entity=entity_name,
            entity_context=entity_context,
            text=text_to_analyze,
            document_abstract=document_description,
        )
        print(f"Processing entity: {entity_name} in document: {document_id}")

        # Make the request to OpenAI
        try:
            client = OpenAI(api_key=openai.api_key)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a model that specializes in opinion mining. You will be given an entity and a text that might or not contain a related opinion, which may be directly or indirectly addressed to the given entity. You will also be given some context, both about the document (as an abstract) and about the entity (birthdate, jobs, other names). Use only the content inside the given text, and not from the context, to generate the output. You must output a JSON following the given schema.",
                    },
                    {"role": "user", "content": formatted_prompt},
                ],
                response_format={"type": "json_object"},
            )

            # Parse the response
            raw_response = response.choices[0].message.content # Parse the response
            print(f"Raw response for entity {entity_name}: {raw_response}")
            entity_output = json.loads(raw_response)

            # Add the entity output and entity info to the document output dictionary
            document_output[entity_name] = entity_output
            document_output[entity_name]["entity_info"] = entity_info

        except Exception as e:
            print(f"Error processing entity {entity_name} in document {document_id}: {e}")
            document_output[entity_name] = {"error": str(e)}

    # Save the output for the current document to a separate JSON file
    document_output_filename = os.path.join(output_dir, f"{document_id}.json")
    with open(document_output_filename, "w", encoding="utf-8") as f:
        json.dump(document_output, f, ensure_ascii=False, indent=4)

    # Add the document output to the all_entities_output dictionary
    final_entities_output[document_id] = document_output

# Save the combined output to a single JSON file
output_filename = "all_entities_output_final.json"
with open(output_filename, "w", encoding="utf-8") as f:
    json.dump(final_entities_output, f, ensure_ascii=False, indent=4)

print(f"All entity responses saved to {output_filename} and individual files in {output_dir}")