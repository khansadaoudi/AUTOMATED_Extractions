import os
from extractions_subj import load_sentences_json, get_dep
from extractions import get_sentences_part, generate_excel_file



def get_gov(sentence_json, dep):
    for token in sentence_json['treeJson']['nodesJson'].values():
        if str(token['ID']) == str(dep):
            return token
    return 'Null'

def get_coordination_conj(sentence_json, pivot):

    gov = get_gov(sentence_json, pivot['ID'])
    list_deps = get_dep(sentence_json, gov)
    deps_function = {}
    for token in list_deps:
        deps_function[token['DEPREL']] = token['FORM']
    
    deps_function_pivot = {}
    list_deps_pivot = get_dep(sentence_json, pivot['ID'])
    for token in list_deps_pivot:
        deps_function_pivot[token['DEPREL']] = token['FORM']

    if pivot['UPOS'] == 'AUX' and 'cc' in deps_function.keys():
        return deps_function['cc']
    if pivot['UPOS'] != 'AUX' and 'cc' in deps_function_pivot.keys():
        return deps_function_pivot['cc']
    
    return 'Null'


def get_subordinate_conj(sentence_json, pivot):

    gov = get_gov(sentence_json, pivot['ID'])
    list_deps = get_dep(sentence_json, gov)
    deps_function = {}
    for token in list_deps:
        deps_function[token['DEPREL']] = token
    
    if 'mark' in deps_function.keys():
        if deps_function['mark']['UPOS'] == 'SCONJ':
            return deps_function['mark']['FORM']
        else:
            list_deps = get_dep(sentence_json, deps_function['mark']['ID'])
            for token in list_deps:
                if token['DEPREL'] == 'fixed' and token['FEATS']['ExtPos'] == 'SCONJ':
                    return token['FORM']
    
    return 'Null'
        
def get_subj(sentence_json, pivot):
    list_deps = get_dep(sentence_json, pivot)
    for token in list_deps:
        if token['DEPREL'] == 'nsubj':
            return {
                'subject': token,
                'subj_position': 'PreV' if int(token['ID']) < int(pivot) else 'PostV',
            }

def get_det_subj(sentence_json, subject_position):
    dep = get_dep(sentence_json, subject_position)
    for token in dep:
        if token['DEPREL'] == 'det' and token['UPOS'] == 'DET':
            return token['FORM']
    return 'Null'

def get_conj(sentence_json, pivot):
    if pivot['DEPREL'] == 'conj':
        gov = get_gov(sentence_json, pivot['ID'])
        if gov != 'Null' and gov['DEPREL'] == 'conj':
            return get_gov(sentence_json, gov['ID'])['DEPREL']
        else: 
            'Null'
    


if __name__ == "__main__":
    
    dir_path = "corag_new_files/"
    for conll_file in os.listdir(dir_path):
        
        if ".conllu" in conll_file:
            conll_file = os.path.join(dir_path, conll_file)
            sentences_json = load_sentences_json(conll_file)
            data = []

            for sent_id, sentence in sentences_json.items():
                for token in sentence['treeJson']['nodesJson'].values():
                    if 'VerbForm' in token['FEATS'].keys() and token['FEATS']['VerbForm'] == 'Fin': 
                        pivot = token 
                        first_part, second_part = get_sentences_part(sentence, int(pivot['ID']), 0)
                        gov = get_gov(sentence, pivot['ID'])
                        gov_of_gov = get_gov(sentence, gov['ID'])

                        subject = get_subj(sentence, pivot['ID'])['subject'] if get_subj(sentence, pivot['ID']) else 'Null'
                        subject_position = get_subj(sentence, pivot['ID'])['subj_position'] if get_subj(sentence, pivot['ID']) else 'Null'


                        entry = {
                            "sent_id": sent_id,
                            "pivot": pivot['FORM'],
                            'Pos Pivot': pivot['UPOS'],
                            'person': pivot['FEATS']['Person'] if 'Person' in pivot['FEATS'].keys() else 'Null',
                            'number': pivot['FEATS']['Number'] if 'Number' in pivot['FEATS'].keys() else 'Null',
                            'function': pivot['DEPREL'] if pivot['UPOS'] != 'AUX' else gov['DEPREL'],
                            'function of gov': gov['DEPREL'] if pivot['UPOS'] == 'AUX' else 'Null',
                            'function of conj': gov['DEPREL'] if pivot['DEPREL'] == 'conj' else gov_of_gov['DEPREL'],
                            'conj function': get_conj(sentence, pivot),
                            'coordinating_conjunction': get_coordination_conj(sentence, pivot),
                            'subordinating_conjunction': get_subordinate_conj(sentence, pivot),
                            'subject': subject['FORM'] if subject != 'Null' else 'Null',
                            'subject_position': subject_position,
                            'subject_upos': subject['UPOS'] if subject != 'Null' else 'Null',
                            'subject_det': get_det_subj(sentence, subject['ID']) if subject != 'Null' else 'Null',
                            'subject pronoun type': subject['FEATS']['PronType'] if subject != 'Null' and 'PronType' in subject['FEATS'].keys() else 'Null',
                            'subject number': subject['FEATS']['Number'] if subject != 'Null' and 'Number' in subject['FEATS'].keys() else 'Null',
                            'subject person': subject['FEATS']['Person'] if subject != 'Null' and 'Person' in subject['FEATS'].keys() else 'Null',
                            'subject pronoun gender': subject['FEATS']['Gender'] if subject != 'Null' and 'Gender' in subject['FEATS'].keys() else 'Null',
                            'Left context': first_part,
                            'Right context': second_part,
                        }
                        data.append(entry)
            excel_file_name = conll_file.replace('.conllu', '_final_extractions.xlsx')
            sheet_name = 'extractions'
            generate_excel_file(data, sheet_name, excel_file_name)


