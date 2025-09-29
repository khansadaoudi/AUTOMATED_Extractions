# Automated Extractions Workspace

This repository contains scripts and utilities for processing, extracting, and analyzing linguistic data from annotated corpora, primarily in CoNLL-U and XML formats. These scripts was applied on [UD_Occitan-CorAG](https://github.com/UniversalDependencies/UD_Occitan-CorAG). This work is a part of Automated project.

## Main Scripts

### Data Conversion

- [`convert_xml_2_conllu.py`](convert_xml_2_conllu.py): Converts XML corpus files to CoNLL-U format.  

- [`convert_pos.py`](convert_pos.py): Updates UPOS tags in CoNLL-U files using gold POS from the MISC field.

- [`convert_italic.py`](convert_italic.py): Processes DOCX files, converting bracketed text to bold italic formatting.

### Extraction & Analysis

- [`extractions.py`](extractions.py): Main extraction logic for structures in CoNLL-U files. Generates Excel files with extracted features.

- [`extractions_sub.py`](extractions_sub.py): Extracts features for subordinate and relative clauses.

- [`extractions_conj.py`](extractions_conj.py): Extracts and highlights conjunct structures in sentences.

- [`extractions_subj.py`](extractions_subj.py): Advanced extraction logic for main clauses, including subject and context features.

- [`extractions_part.py`](extractions_part.py): Extracts information about participial constructions.

- [`extractions_finite.py`](final_extractions.py): Extracts features for finite verbs.

## Input Files

- **request_sub.json**, **request_conj.json**, **request_subj.json**, **new_requests.json**: Pattern files for extraction requests.


## Requirements

In order to use the scripts you have to install [grewpy library](https://grew.fr/usage/python/)

Install dependencies with:
```
pip install -r requirements.txt
```
