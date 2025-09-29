import json
import os

import extractions_subj, extractions

import grewpy
from conllup.conllup import sentenceJsonToConll
from grewpy import Request, Corpus


def get_extraction(request, corpus): 

    results = {}

    pattern = Request(request["request_pattern"])

    occurences = corpus.search(pattern)
    
    for occurence in occurences: 
        results[occurence['sent_id']] = {
            node: occurence['matching']['nodes'][node] for node in occurence['matching']['nodes'].keys()
        }
    
    return results

def highlight_results(match_nodes, sentence_json): 

    text = ' '.join([token['FORM'] if token['ID'] not in match_nodes.values() else f"**{token['FORM']}**" for token in sentence_json['treeJson']['nodesJson'].values()])
    return text

def check_if_has_subject(match_nodes, sentence_json):
    
    for node, position in match_nodes.items():
        subj_exist = 'N'
        subject = {}
        if node != 'X' and node != 'R': 
            deps = extractions_subj.get_dep(sentence_json, position)
            for dep in deps:
                if dep['DEPREL'] == 'nsubj':
                    subj_exist = 'Y'
                    subject = dep
                    break
            

    return subj_exist, subject
            
            

if __name__ == "__main__":

    grewpy.set_config("ud")
    request_file = open("request_conj.json")

    requests = json.load(request_file)['patterns']

    dir_path = 'new_files/'
    for conll_file in os.listdir("new_files"):
        if conll_file.endswith(".conllu"):

            file_path = os.path.join(dir_path, conll_file)
            corpus = Corpus(file_path)
            sentences_json = extractions_subj.load_sentences_json(os.path.join(dir_path, conll_file))

            data = []
            for request in requests:
                results = get_extraction(request, corpus)
                
                for sent_id, match_nodes in results.items():
                    sentence_json = sentences_json[sent_id]
                    text = highlight_results(match_nodes, sentence_json)
                    conj_subj = check_if_has_subject(match_nodes, sentence_json)
                    entry = {
                        'Sent_ID': sent_id,
                        'Number of conjuncts': request['request_type'],
                        'Sentence': text,
                        'Conj subject': conj_subj,
                    }
                    data.append(entry)
        
            excel_file_name = f"new_files/{conll_file.split('.conllu')[0]}.xlsx"
            sheet_name = " MAIN CLAUSES with conjuncts"
            extractions.generate_excel_file(data, sheet_name, excel_file_name)


