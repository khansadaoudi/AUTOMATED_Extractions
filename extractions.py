import os
import json
import pandas as pd

from conllup.conllup import readConlluFile

import grewpy
from grewpy import Corpus, Request


def load_corpus(file_path):
    return Corpus(file_path)

def load_corpus_json(file_path):
    return readConlluFile(file_path)

def extract_structures(corpus, request_pattern):
   
    results = []
    request = Request(request_pattern)
    occurences = corpus.search(request)

    for occurence in occurences: 
        result = {
            'Sent-ref': occurence['sent_id'], 
            'root-position': occurence['matching']['nodes']['Y'],
            'subject-position': occurence['matching']['nodes']['Z'] if 'Z' in occurence['matching']['nodes'].keys() else ''
        }
        results.append(result)
    return results

   
def get_subj(sentence_json, root_position):
    pivot = sentence_json['treeJson']['nodesJson'][str(root_position)]
    for token in sentence_json['treeJson']['nodesJson'].values():
        if str(token['HEAD']) == pivot["ID"] and token['DEPREL'] == 'nsubj':
            return token['FORM'], token['ID']
    return None, None


def get_pivot(sentence_json, root_position):

    pivot= sentence_json['treeJson']['nodesJson'][str(root_position)]
    pivot_rel = ["aux", "cop", "aux:pass"]
    
    for token in sentence_json['treeJson']['nodesJson'].values():
        if str(token['HEAD']) == pivot["ID"] and token['DEPREL'] in pivot_rel and token["UPOS"] == 'AUX' and pivot["UPOS"] != 'AUX':
            return token["FORM"], token["ID"]
    
    return pivot["FORM"], pivot["ID"]


def get_sentences_part(sentence_json, pivot_position, subject_position):

    first_part_sentence = list(sentence_json['treeJson']['nodesJson'].values())[:pivot_position-1]
    second_part_sentence = list(sentence_json['treeJson']['nodesJson'].values())[pivot_position:]
    if subject_position == 0:
        first_part = ' ' .join([token['FORM'] for token in first_part_sentence])
        second_part = ' '.join([token['FORM'] for token in second_part_sentence])

    elif pivot_position > subject_position:
        first_part = ' ' .join([token['FORM'] if int(token['ID']) != subject_position else f"**{token['FORM']}**" for token in first_part_sentence])
        second_part = ' '.join([token['FORM'] for token in second_part_sentence])

    elif pivot_position < subject_position:
        first_part = ' ' .join([token['FORM'] for token in first_part_sentence])
        second_part = ' '.join([token['FORM'] if int(token['ID']) != subject_position else f"**{token['FORM']}**" for token in second_part_sentence])
    
    return first_part, second_part

def generate_excel_file(results, pattern_name, file_path):
    df = pd.DataFrame(results)
    try: 
        writer = pd.ExcelWriter(file_path, engine='openpyxl', mode="a", if_sheet_exists="replace")
    except FileNotFoundError:
        writer = pd.ExcelWriter(file_path, engine="openpyxl", mode="w")

    df.to_excel(writer, sheet_name=pattern_name, index=False)
    writer.close()

if __name__ == "__main__":

    grewpy.set_config("ud")
    requests_file = open("request_sub.json")
    requests = json.load(requests_file)['patterns']
    dir_path = 'Files/'

    for conll_file in os.listdir(dir_path):
        if ".conllu" in conll_file:
            corpus = load_corpus(os.path.join(dir_path, conll_file))
            sentences_json = load_corpus_json(os.path.join(dir_path, conll_file))
    
            for request in requests:
                results = extract_structures(corpus, request['request_pattern'])
                data = []
                if results: 
                    for result in results:
                        sentence_json = [sentence_json for sentence_json in sentences_json if sentence_json['metaJson']['sent_id'] == result['Sent-ref']][0]
                        pivot_form , pivot_id = get_pivot(sentence_json, result['root-position']) 
                        if result['subject-position'] == '':
                            subj_form, subj_id = get_subj(sentence_json, result['root-position'])
                            if subj_form and subj_id:
                                subject_position = 'PROpreV' if int(subj_id) < int(pivot_id) else 'PROpostV'
                                subject = subj_form
                            else: 
                                subject_position = ''
                                subject = ''
                                subj_id = '0'
                        else: 
                            subj_id = result['subject-position']
                            subject= sentence_json['treeJson']['nodesJson'][str(result['subject-position'])]['FORM']
                            subject_position = 'PROpreV' if int(subj_id) < int(result['root-position']) else 'PROpostV'

                        sent_first_part, sent_second_part = get_sentences_part(sentence_json, int(pivot_id), int(subj_id))
                        
                        entry = {
                            'Sent-Ref': result['Sent-ref'],
                            'Clause': 'SUB',
                            'Subject Position': subject_position,
                            'subject': subject,
                            'Left Context': sent_first_part,
                            'Pivot': pivot_form,
                            'Right Context': sent_second_part, 
                            'Type-SUB': request['type_sub']
                        }
                        data.append(entry)

                excel_file_name = f"sub_extractions/{conll_file.split('.conllu')[0]}.xlsx"
                sheet_name = f"{request['request_type']}_{request['subject_position']}_{request['type_sub']}"
                generate_excel_file(data, sheet_name, excel_file_name)

                