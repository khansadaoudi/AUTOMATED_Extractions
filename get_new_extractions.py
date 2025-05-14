import json
import os

import extractions
import grewpy

from conllup.conllup import sentenceJsonToConll
from grewpy import Request, Corpus


def get_que_enonciatif(sentence_json):

    request = "pattern { X -[root]-> Y;\nY -[expl]->A;\nA[upos=\"PART\"]}"
    sentence_conll = sentenceJsonToConll(sentence_json)

    corpus = Corpus(sentence_conll)
    request = Request(request)
    occurences = corpus.search(request)

    return 'Y' if len(occurences) > 0 else 'N'


def get_subj_det(sentence_json):

    request = "pattern { X -[nsubj]-> Y;\nY -[det]->A;\nA[upos=\"DET\"];}"
    sentence_conll = sentenceJsonToConll(sentence_json)

    conrpus = Corpus(sentence_conll)
    request = Request(request)
    occurences = conrpus.search(request)

    return 'Y' if len(occurences) > 0 else 'N'

def get_subj_nmod(sentence_json):

    request = "pattern { s-[nmod]-> s}"
    sentence_conll = sentenceJsonToConll(sentence_json)

    corpus = Corpus(sentence_conll)
    request = Request(request)
    occurences = corpus.search(request)

    return 'Y' if len(occurences) > 0 else 'N'


def get_subj_rel(sentence_json):

    request = "pattern { s-[acl:relc]-> s}"
    sentence_conll = sentenceJsonToConll(sentence_json)

    corpus = Corpus(sentence_conll)
    request = Request(request)
    occurences = corpus.search(request)

    return 'Y' if len(occurences) > 0 else 'N'



if __name__ == "__main__":

    grewpy.set_config("ud")
    requests_file = open("new_requests.json")
    requests = json.load(requests_file)['patterns'] 
    dir_path = 'new_files/'

    for conll_file in os.listdir("new_files"):

        if ".conllu" in conll_file:

            corpus = extractions.load_corpus(os.path.join(dir_path, conll_file))
            sentences_json = extractions.load_corpus_json(os.path.join(dir_path, conll_file))

            for request in requests:
                results = extractions.extract_structures(corpus, request['request_pattern'])
                data = []
                if results: 
                    for sent_id, result in results.items():
                        sentence_json = [sentence_json for sentence_json in sentences_json if sentence_json['metaJson']['sent_id'] == sent_id][0]
                        pivot_form , pivot_id = extractions.get_pivot(sentence_json, result['root-position']) 
                        if result['subject-position'] == '':
                            subj_form, subj_id = extractions.get_subj(sentence_json, result['root-position'])
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
                            subject_upos = sentence_json['treeJson']['nodesJson'][str(result['subject-position'])]['UPOS']
                            subject_position = 'PROpreV' if int(subj_id) < int(result['root-position']) else 'PROpostV'

                        sent_first_part, sent_second_part = extractions.get_sentences_part(sentence_json, int(pivot_id), int(subj_id))

                        entry = {
                            'Sent-ID': sent_id,
                            'Clause': 'MAT',
                            'Subject Position': subject_position,
                            'Subject with nmod': get_subj_nmod(sentence_json),
                            'Subject with rel': get_subj_rel(sentence_json),
                            'subject Pos': subject_upos,
                            'Subject with det': get_subj_det(sentence_json),
                            'Que enonciatif': get_que_enonciatif(sentence_json),
                            'Left context': sent_first_part,
                            'Pivot': pivot_form,
                            'Right context': sent_second_part,

                        }
                        data.append(entry)
                    excel_file_name = f"new_files/{conll_file.split('.conllu')[0]}.xlsx"
                    sheet_name = f"{request['request_type']}_{subject_position}"
                    extractions.generate_excel_file(data, sheet_name, excel_file_name)


        
       





