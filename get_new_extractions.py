import json
import os

import extractions
import grewpy

from conllup.conllup import sentenceJsonToConll
from grewpy import Request, Corpus

def load_sentences_json(file_path): 
    mapped_sentences = {}
    sentences_json = extractions.load_corpus_json(file_path)
    for sentence_json in sentences_json:
        sent_id = sentence_json['metaJson']['sent_id']
        mapped_sentences[sent_id] = sentence_json

    return mapped_sentences
   
def get_extraction(request, corpus):

    results = {}

    pattern = Request(request["request_pattern"])

    occurences = corpus.search(pattern)
    
    for occurence in occurences:
        if occurence['sent_id'] not in results.keys():
            results[occurence['sent_id']] = {
                'root-position': occurence['matching']['nodes'][request['pivot']],
            }
    
    return results

def get_subj(sentence_json, root_position):

    pattern = "pattern { X -[root]-> Y;\nY -[nsubj]-> Z}"

    pattern = Request(pattern)
    sentence_conll = sentenceJsonToConll(sentence_json)
    corpus = Corpus(sentence_conll)
    occurences = corpus.search(pattern)

    if occurences:
        node_id = occurences[0]['matching']['nodes']['Z']
        token = sentence_json['treeJson']['nodesJson'][node_id]
        
        subj_info = {
            'subj_position': token['ID'],
            'form': token['FORM'],
            'position': 'preV' if int(token['ID']) < int(root_position) else 'postV',
            'upos': token['UPOS'],
        }
        return subj_info
    
    return { 'subj_position': 'Null' }
            
def check_que_enonciatif(sentence_json):
    
    sentence_conll = sentenceJsonToConll(sentence_json)
    request = "pattern { X -[root]-> Y;\nY -[expl]->A;\nA[upos=\"PART\"]}"

    corpus = Corpus(sentence_conll)
    request = Request(request)
    occurences = corpus.search(request)

    return 'Y' if len(occurences) > 0 else 'N'

def get_dep(sentence_json, gov):

    list_deps = []
    for token in sentence_json['treeJson']['nodesJson'].values():
        if str(token['HEAD']) == str(gov):
            list_deps.append(token)
    
    return list_deps

def check_subj(sentence_json, subject_position, deprel):
    for token in sentence_json['treeJson']['nodesJson'].values():
        dep = get_dep(sentence_json, subject_position)
        if token['ID'] == subject_position:
            if deprel == 'det':
                for d in dep:
                    if d['DEPREL'] == deprel and d['UPOS'] == 'DET':
                        return 'Y'
                return 'N'
            else:
                for d in dep:
                    if d['DEPREL'] == deprel:
                        return 'Y'
                return 'N'

def get_mark(sentence_json):
    for token in sentence_json['treeJson']['nodesJson'].values():
        if token['HEAD'] == '0': 
            children = get_dep(sentence_json, token['ID'])
            for child in children:
                if child['DEPREL'] == 'mark':
                    return child['FORM']
    return None

if __name__ == "__main__":

    grewpy.set_config("ud")
    requests_file = open("new_requests.json")
    requests = json.load(requests_file)['patterns'] 

    requests_file = open("request_subj.json")
    requests_subj = json.load(requests_file)['patterns']

    dir_path = 'new_files/'
    for conll_file in os.listdir("new_files"):
        if ".conllu" in conll_file:

            corpus = extractions.load_corpus(os.path.join(dir_path, conll_file))
            sentences_json = load_sentences_json(os.path.join(dir_path, conll_file))

            data = []
            for request in requests:
                results = get_extraction(request, corpus)

                if results:
                    for sent_id, root_position in results.items():
                        sentence_json = sentences_json[sent_id]
                        subj_info = get_subj(sentence_json, root_position['root-position'])
                        pivot = sentence_json['treeJson']['nodesJson'][root_position['root-position']]

                        if subj_info['subj_position'] != 'Null':
                            subj_info['Que énnociatif'] = check_que_enonciatif(sentence_json)
                            first_part, second_part = extractions.get_sentences_part(sentence_json, int(root_position['root-position']), int(subj_info['subj_position']))

                        else:
                            first_part, second_part = extractions.get_sentences_part(sentence_json, int(root_position['root-position']), 0)
                        
                        entry = {
                            'Sent-ID': sent_id,
                            'Clause': 'MAT',
                            'Subject position': subj_info['position'] if subj_info['subj_position'] != 'Null' else 'Null',
                            'Subject with nmod': check_subj(sentence_json, subj_info['subj_position'], 'nmod') if subj_info['subj_position'] != 'Null' else 'Null',
                            'Subject with relative': check_subj(sentence_json, subj_info['subj_position'], 'acl:relc') if subj_info['subj_position'] != 'Null' else 'Null',
                            'mark': get_mark(sentence_json),
                            'Subject Pos': subj_info['upos'] if subj_info['subj_position'] != 'Null' else 'Null',
                            'Subject PronType': subj_info['FEATS']['PronType'] if 'FEATS' in subj_info and 'PronType' in subj_info['FEATS'] else 'Null',
                            'Subject Number': subj_info['FEATS']['Number'] if 'FEATS' in subj_info and 'Number' in subj_info['FEATS'] else 'Null',
                            'Subject Person': subj_info['FEATS']['Person'] if 'FEATS' in subj_info and 'Person' in subj_info['FEATS'] else 'Null',
                            'Subject Det': check_subj(sentence_json, subj_info['subj_position'], 'det') if subj_info['subj_position'] != 'Null' else 'Null',
                            'Que énonciatif': check_que_enonciatif(sentence_json),
                            'Left context': first_part,
                            'pivot': pivot['FORM'],
                            'Right context': second_part,                                           
                        }
                        data.append(entry)

            excel_file_name = f"Corag_files/{conll_file.split('.conllu')[0]}.xlsx"
            sheet_name = "MAT"
            extractions.generate_excel_file(data, sheet_name, excel_file_name)
                    




                        
                        
                    


