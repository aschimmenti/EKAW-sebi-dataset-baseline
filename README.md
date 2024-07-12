# EKAW-sebi-dataset-baseline
Repository for the Ground Truth, Baseline and results for the EKAW 2024 paper "A baseline to mine scholarly claims on forged documents using GPT-4o and Wikidata". 

## Ground Truth Folder
Contains subfolders related to different steps and stages of dataset processing. The GT final dataset is contained in the Manual Annotation folder, alongside  

## Pipeline
Contains various subfolders for different parts of the pipeline. The order is: 
### Pipeline-NER-1
Uses spacy-llm NER to extract Named Entities of the commentator type 
### Pipeline-EL-2
Uses the Wikidata API to fetch information about the entities
### Pipeline-Coref-3
Uses GPT-4o to coreference and return potential claim sentences  
### Pipeline-Extraction-4
Uses GPT-4o to extract and structure claims
### Pipeline-Cleaning-5
### Pipeline-Eval
Evaluation scripts for f-1 score

##KB 
Contains the baseline and the manual output alongside the RDF (.trig) files. 
