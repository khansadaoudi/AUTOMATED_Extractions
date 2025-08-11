import os
from extractions_sub import get_nsubj, get_dep, get_sentences_part
from extractions import load_corpus_json, generate_excel_file

def get_object(sentence_json, position_id):
    deps = get_dep(sentence_json, position_id)
    for dep in deps:
        if dep['DEPREL'] == 'obj':
            return dep
    return None

def get_part_info(sentence_json):

    for token in sentence_json['treeJson']['nodesJson'].values():
        if 'VerbForm' in token['FEATS'].keys() and token['FEATS']['VerbForm'] == 'Part':
            subject = get_nsubj(sentence_json, token['ID'])
            object = get_object(sentence_json, token['ID'])
            deps = get_dep(sentence_json, token['ID'])
            first_part, second_part = get_sentences_part(sentence_json, int(token['ID']), int(subject['ID']) if subject else 0)
            part_info = {
                'sentence_id': sentence_json['metaJson']['sent_id'],
                'PoS': token['UPOS'],
                'Tense': token['FEATS'].get('Tense', 'None'),
                'Gender': token['FEATS'].get('Gender', 'None'),
                'Number': token['FEATS'].get('Number', 'None'),
                'Voice': token['FEATS'].get('Voice', 'None'),
                'deprel': token['DEPREL'],
                'nsubj': 'Yes' if subject else 'No',
                'nsubj-PoS': subject['UPOS'] if subject else 'N/A',
                'nsubj-PRON-Type': subject['FEATS'].get('PronType', 'N/A') if subject else 'N/A',
                'nsubj-Form': subject['FORM'] if subject else 'N/A',
                'obj': 'Yes' if object else 'No',
                'obj-PoS': object['UPOS'] if object else 'N/A',
                'obj-Form': object['FORM'] if object else 'N/A',
                'obj-PRON-Type': object['FEATS'].get('PronType', 'N/A') if object else 'N/A',
                'aux': 'Yes' if any(dep['DEPREL'] == 'aux' for dep in deps) else 'No',
                'aux:passive': 'Yes' if any(dep['DEPREL'] == 'aux:pass' for dep in deps) else 'No',
                'context_gauche': first_part,
                'pivot': token['FORM'],
                'context_droite': second_part,

            }
            return part_info
        
    


if __name__ == "__main__":

    excel_file_name = "CorAG_Part.xlsx"

    for conll_file in os.listdir('Corag_files'):
        print(f"Processing {conll_file}...")
        if conll_file.endswith(".conllu"):

            sentences_json = load_corpus_json(os.path.join('Corag_files', conll_file))
            data = []
            for sentence_json in sentences_json:
                part_info = get_part_info(sentence_json)
                if part_info:
                    data.append(part_info)
            if data:
                generate_excel_file(data, conll_file.replace('.conllu', ''), excel_file_name)
                

