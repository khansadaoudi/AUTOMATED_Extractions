# this file contains utilities which are required by individual extraction operations
from conllup.conllup import readConlluFile
import pandas as pd
from grewpy import Request, Corpus
import json
import sys


def load_sentences_json(file_path): 
    mapped_sentences = {}
    sentences_json_raw = readConlluFile(file_path)
    for sentence_json_raw in sentences_json_raw:
        # print(json.dumps(sentence_json_raw, indent=4))
        sent_id = sentence_json_raw['metaJson']['sent_id']
        mapped_sentences[sent_id] = sentence_json_raw
        # print(json.dumps(mapped_sentences, indent=4))
        # sys.exit(0)

    return mapped_sentences

def get_dep(sentence_json, gov):

    list_deps = []
    for token in sentence_json['treeJson']['nodesJson'].values():
        if str(token['HEAD']) == str(gov):
            list_deps.append(token)
    return list_deps


def get_sentences_part(sentence_json, pivot_position):
    #extract the dictionary part before and after the pivot 
    first_part_sentence = list(sentence_json['treeJson']['nodesJson'].values())[:pivot_position-1]
    second_part_sentence = list(sentence_json['treeJson']['nodesJson'].values())[pivot_position:]
    #extract form from the left and right part of the sentence and glue into a string with spaces
    first_part = ' ' .join([token['FORM'] for token in first_part_sentence])
    second_part = ' '.join([token['FORM'] for token in second_part_sentence])

    return first_part, second_part

def generate_excel_file(results, pattern_name, file_path):
    df = pd.DataFrame(results)
    try: 
        writer = pd.ExcelWriter(file_path, engine='openpyxl', mode="a", if_sheet_exists="replace")
    except FileNotFoundError:
        writer = pd.ExcelWriter(file_path, engine="openpyxl", mode="w")

    df.to_excel(writer, sheet_name=pattern_name, index=False)
    writer.close()

def generate_csv_file(results, file_path):
    df = pd.DataFrame(results)
    df.to_csv(file_path, index=False)


def get_gov(sentence_json, dep):
    for token in sentence_json['treeJson']['nodesJson'].values():
        if str(token['ID']) == str(dep):
            return token
    return 'Null'
