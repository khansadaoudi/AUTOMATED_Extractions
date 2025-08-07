import json
import os

from conllup.conllup import sentenceJsonToConll, readConlluFile
from grewpy import Request, Corpus

import grewpy

from extractions import get_sentences_part, load_corpus, generate_excel_file
from get_new_extractions import load_sentences_json, get_dep


def extract_pivot(sentence_json, patterns):

    for pattern in patterns:
        request = Request(pattern["request_pattern"])
        corpus = Corpus(sentenceJsonToConll(sentence_json))
        occurences = corpus.search(request)

        if occurences:
            root_position = occurences[0]['matching']['nodes'][pattern['pivot']]
            return root_position
    return None 

def extract_pivot_rel(sentence_json, position_y, position_x):

    deps = get_dep(sentence_json, position_y)
    print(sentence_json['metaJson']['sent_id'], position_y, position_x)
    relations = ['aux', 'aux:pass', 'cop']
    for dep in deps:
        if dep['DEPREL'] in relations:
            return dep 
        
    return sentence_json['treeJson']['nodesJson'][position_y]

def extract_antecedant(corpus):

    results = {}
    pattern = Request("pattern { X -[acl:relcl]-> Y;Y -> P;P[upos=PRON];P<<Y}")

    occurences = corpus.search(pattern) 

    for occurence in occurences:
        sent_id = occurence['sent_id']
        result = {
            "antecedant": occurence['matching']['nodes']['X'],
            "P": occurence['matching']['nodes']['P'], 
            'Y': occurence['matching']['nodes']['Y'],
        }
        results[sent_id] = result
        
    return results

def check_conj(sentence_json, position):

    deps = get_dep(sentence_json, position)
    for dep in deps:
        if dep['DEPREL'] == 'conj':
            return 'Y', dep['UPOS']
    return 'N', 'N/A'

def get_first_pron(sentence_json, position):
    
    deps = get_dep(sentence_json, position)
    for dep in deps:
        if dep['UPOS'] == 'PRON':
            return dep
    return None

def get_nsubj(sentence_json, position):
    
    deps = get_dep(sentence_json, position)
    for dep in deps:
        if dep['DEPREL'] == 'nsubj':
            return dep
    return None


def get_extraction(corpus, sentences_json, patterns):

    results = extract_antecedant(corpus)

    for sent_id, match_nodes in results.items():
        sentence_json = sentences_json[sent_id]
        antecedant = sentence_json['treeJson']['nodesJson'][match_nodes['antecedant']]
        antecedant_upos = antecedant['UPOS']
        
        pivot = extract_pivot_rel(sentence_json, match_nodes['Y'], match_nodes['antecedant'])
        first_pron = get_first_pron(sentence_json, match_nodes['Y'])
        n_subj = get_nsubj(sentence_json, match_nodes['Y'])
        first_part, second_part = get_sentences_part(sentence_json, int(pivot['ID']), int(n_subj['ID']) if n_subj else 0)

        results[sent_id] = {
            "Sent-ID": sent_id, 
            "Sub/MAT": "REL",
            "Antecedant": antecedant["FORM"],
            "Antecedant-UPOS": antecedant_upos,
            "First PRON": first_pron['FORM'] if first_pron else 'N/A',
            "Function of PRON": first_pron['DEPREL'] if first_pron else 'N/A',
            "N subj form": n_subj['FORM'] if n_subj else 'N/A',
            "N subj UPOS": n_subj['UPOS'] if n_subj else 'N/A',
            "Left context": first_part,
            "pivot": pivot['FORM'],
            "Right context": second_part,
        }


    return results



if __name__ == "__main__":
    

    grewpy.set_config("ud")
    request_file = open("new_requests.json")

    requests = json.load(request_file)['patterns']

    dir_path = 'new_files/'
    for conll_file in os.listdir("new_files"):

        if conll_file.endswith(".conllu"):

            corpus = load_corpus(os.path.join(dir_path, conll_file))
            sentences_json = load_sentences_json(os.path.join(dir_path, conll_file))

            results = get_extraction(corpus, sentences_json, requests)
            data = results.values()
            
            excel_file_name = f"new_files/{conll_file.split('.conllu')[0]}_True_relatives.xlsx"
            sheet_name = "REL"
            generate_excel_file(data, sheet_name, excel_file_name)


                





    
