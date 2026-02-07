import os
import sys
import json 

from extractions_subj import load_sentences_json, get_dep
from extractions import get_sentences_part, generate_excel_file, generate_csv_file
import argparse
from pathlib import Path
from conllup.conllup import sentenceJsonToConll
from grewpy import Request, Corpus

def get_gov(sentence_json, dep):
    for token in sentence_json['treeJson']['nodesJson'].values():
        #print(token)
        if str(token['ID']) == str(dep):
            return token
    return 'Null'

def get_coordination_conj_form(sentence_json, pivot_id, pivot_upos):
    # verbatim query on a specified sentence. Then filter the result by pivot_id and extract data
    if(pivot_upos == 'VERB'): pattern=f"pattern {{PV[upos=VERB]; PV[VerbForm=Fin];PV -[cc]-> CC; meta.sent_id = \"{sentence_json['metaJson']['sent_id']}\";}}"
    elif (pivot_upos == 'AUX'): pattern=f"pattern {{PV[upos=AUX]; HPV->PV;HPV -[cc]-> CC; meta.sent_id = \"{sentence_json['metaJson']['sent_id']}\";}}"
    else: return 'Null'

    pattern = Request(pattern)
    sentence_conll = sentenceJsonToConll(sentence_json)
    corpus = Corpus(sentence_conll)
    occurences = corpus.search(pattern)

    if occurences:
        for occ in occurences:
            if occ['matching']['nodes']['PV'] == pivot_id:
              return sentence_json['treeJson']['nodesJson'][occ['matching']['nodes']['CC'] ]['FORM'] 
 
    return 'Null'    
  
def get_coordination_conj_id(sentence_json, pivot_id, pivot_upos):
    # verbatim query on a specified sentence. Then filter the result by pivot_id and extract data
    if(pivot_upos == 'VERB'): pattern=f"pattern {{ PV[upos=VERB]; PV[VerbForm=Fin]; PV -[cc]-> CC; meta.sent_id = \"{sentence_json['metaJson']['sent_id']}\";}}"
    elif (pivot_upos == 'AUX'): pattern=f"pattern {{ PV[upos=AUX]; PV[VerbForm=Fin]; HPV->PV; HPV -[cc]-> CC; meta.sent_id = \"{sentence_json['metaJson']['sent_id']}\";}}"
    else: return 'Null'

    pattern = Request(pattern)
    sentence_conll = sentenceJsonToConll(sentence_json)
    corpus = Corpus(sentence_conll)
    occurences = corpus.search(pattern)
    
    if occurences:
        for occ in occurences:
            if occ['matching']['nodes']['PV'] == pivot_id:
             try:
              return occ['matching']['nodes']['CC']
             except: 
              return' Null'
 
    return 'Null'      


def get_subj_pron_num(sentence_json, pivot_id, pivot_upos):
    # verbatim query on a specified sentence. Then filter the result by pivot_id and extract data    
    if(pivot_upos == 'VERB'): pattern=f"pattern {{ PV[upos=VERB]; PV[VerbForm=Fin]; PV -[nsubj]-> S; meta.sent_id = \"{sentence_json['metaJson']['sent_id']}\";}}"
    elif (pivot_upos == 'AUX'): pattern=f"pattern {{ PV[upos=AUX]; PV[VerbForm=Fin]; HPV->PV; HPV -[nsubj]-> S; meta.sent_id = \"{sentence_json['metaJson']['sent_id']}\";}}"
    else: return 'Null'

    pattern = Request(pattern)
    sentence_conll = sentenceJsonToConll(sentence_json)
    corpus = Corpus(sentence_conll)
    occurences = corpus.search(pattern)
    
    if occurences:
        for occ in occurences:
            if occ['matching']['nodes']['PV'] == pivot_id:
             return sentence_json['treeJson']['nodesJson'][occ['matching']['nodes']['N'] ]['FORM'] 
 
    return 'Null'      

def get_subj_pron_gender(sentence_json, pivot_id, pivot_upos):
    # verbatim query on a specified sentence. Then filter the result by pivot_id and extract data
    if(pivot_upos == 'VERB'): pattern=f"pattern {{ PV[upos=VERB]; PV[VerbForm=Fin]; PV -[nsubj]-> S; S[Gender= G]; meta.sent_id = \"{sentence_json['metaJson']['sent_id']}\";}}"
    elif (pivot_upos == 'AUX'): pattern=f"pattern {{ PV[upos=AUX]; PV[VerbForm=Fin]; HPV->PV; HPV -[nsubj]-> S; S[Gender= G]; meta.sent_id = \"{sentence_json['metaJson']['sent_id']}\";}}"
    else: return 'Null'

    pattern = Request(pattern)
    sentence_conll = sentenceJsonToConll(sentence_json)
    corpus = Corpus(sentence_conll)
    occurences = corpus.search(pattern)
    
    if occurences:
        for occ in occurences:
            if occ['matching']['nodes']['PV'] == pivot_id:
             return sentence_json['treeJson']['nodesJson'][occ['matching']['nodes']['G'] ]['FORM'] 
 
    return 'Null'      


def get_subj_pron_person(sentence_json, pivot_id, pivot_upos):
    # verbatim query on a specified sentence. Then filter the result by pivot_id and extract data
    if(pivot_upos == 'VERB'): pattern=f"pattern {{ PV[upos=VERB]; PV[VerbForm=Fin]; PV -[nsubj]-> S; S[PronType=P]; meta.sent_id = \"{sentence_json['metaJson']['sent_id']}\";}}"
    elif (pivot_upos == 'AUX'): pattern=f"pattern {{ PV[upos=AUX]; PV[VerbForm=Fin]; HPV->PV; HPV -[nsubj]-> S; S[PronType= P]; meta.sent_id = \"{sentence_json['metaJson']['sent_id']}\";}}"
    else: return 'Null'

    pattern = Request(pattern)
    sentence_conll = sentenceJsonToConll(sentence_json)
    corpus = Corpus(sentence_conll)
    occurences = corpus.search(pattern)
    #print(sentence_json['metaJson']['sent_id'])
    
    if occurences:
        for occ in occurences:
            if occ['matching']['nodes']['PV'] == pivot_id:
             return sentence_json['treeJson']['nodesJson'][occ['matching']['nodes']['P'] ]['FORM'] 
 
    return 'Null'      

        
def get_subj(sentence_json, pivot):
    list_deps = get_dep(sentence_json, pivot)
    for token in list_deps:
        if token['DEPREL'] == 'nsubj':
            return {
                'subject': token,
                'subj_position': 'PreV' if int(token['ID']) < int(pivot) else 'PostV',
            }

def get_conj(sentence_json, pivot):
    if pivot['DEPREL'] == 'conj':
        gov = get_gov(sentence_json, pivot['ID'])
        if gov != 'Null' and gov['DEPREL'] == 'conj':
            return get_gov(sentence_json, gov['ID'])['DEPREL']
        else: 
            'Null'
    
def get_enonciatif(sentence_json, pivot_id, pivot_upos):
    # verbatim query on a specified sentence. Then filter the result by pivot_id and extract data
    if(pivot_upos == 'VERB'): pattern=f"pattern {{PV[upos=VERB] ; PV[VerbForm=Fin];PV -[discourse:enunc]-> E; meta.sent_id = \"{sentence_json['metaJson']['sent_id']}\";}}"
    elif (pivot_upos == 'AUX'): pattern=f"pattern {{PV[upos=AUX]; HPV->PV;HPV -[discourse:enunc]-> E; meta.sent_id = \"{sentence_json['metaJson']['sent_id']}\";}}"
    else: return 'Null'

    pattern = Request(pattern)
    sentence_conll = sentenceJsonToConll(sentence_json)
    corpus = Corpus(sentence_conll)
    occurences = corpus.search(pattern)
    
    if occurences:
        for occ in occurences:
            if occ['matching']['nodes']['PV'] == pivot_id:
             return sentence_json['treeJson']['nodesJson'][occ['matching']['nodes']['E'] ]['FORM'] 
 
    return 'Null'      
 



def get_subj_pron(sentence_json, pivot_id, pivot_upos):
    # verbatim query on a specified sentence. Then filter the result by pivot_id and extract data
    if(pivot_upos == 'VERB'): pattern=f"pattern {{ PV[upos=VERB]; PV[VerbForm=Fin]; PV -[nsubj]-> S; meta.sent_id = \"{sentence_json['metaJson']['sent_id']}\";}}"
    elif (pivot_upos == 'AUX'): pattern=f"pattern {{ PV[upos=AUX]; PV[VerbForm=Fin]; HPV->PV; HPV -[nsubj]-> S; meta.sent_id = \"{sentence_json['metaJson']['sent_id']}\";}}"
    else: return 'Null','Null','Null','Null'

    pattern = Request(pattern)
    sentence_conll = sentenceJsonToConll(sentence_json)
    corpus = Corpus(sentence_conll)
    occurences = corpus.search(pattern)

    if occurences:
        for occ in occurences:
            if  occ['matching']['nodes']['PV'] == pivot_id:
             try:
              Pron  =  sentence_json['treeJson']['nodesJson'][occ
              ['matching']['nodes']['S'] ]['FEATS']['PronType']
             except:
              Pron= 'Null'
             try:  
              Number= sentence_json['treeJson']['nodesJson'][occ['matching']['nodes']['S'] ]['FEATS']['Number']
             except: Number='Null' 
             try:
              Gender=sentence_json['treeJson']['nodesJson'][occ['matching']['nodes']['S'] ]['FEATS']['Gender']
             except:Gender='Null' 
             return  Number,Pron,Gender,sentence_json['treeJson']['nodesJson'][occ['matching']['nodes']['S'] ]['FORM']
 
    return 'Null','Null','Null','Null'


def get_subj_position_prev(sentence_json, pivot_id, pivot_upos):
    # verbatim query on a specified sentence. Then filter the result by pivot_id and extract data
    if(pivot_upos == 'VERB'): pattern=f"pattern {{PV[upos=VERB]; PV[VerbForm=Fin]; PV-[nsubj]->S; S<<PV; meta.sent_id = \"{sentence_json['metaJson']['sent_id']}\";}}"
    elif (pivot_upos == 'AUX'): pattern=f"pattern {{PV[upos=AUX]; PV[VerbForm=Fin]; HPV->PV; HPV-[nsubj]->S;S<<PV; meta.sent_id = \"{sentence_json['metaJson']['sent_id']}\";}}"
    else: return 'Null'

    pattern = Request(pattern)
    sentence_conll = sentenceJsonToConll(sentence_json)
    corpus = Corpus(sentence_conll)
    occurences = corpus.search(pattern)

    if occurences:
        for occ in occurences:
            if occ['matching']['nodes']['PV'] == pivot_id:
             try:
              #print(occ)
              return occ['matching']['nodes']['S']
             except: 
              return' Null'
 
    return 'Null'      

def get_subj_position_postv(sentence_json, pivot_id, pivot_upos):
    # verbatim query on a specified sentence. Then filter the result by pivot_id and extract data
    if(pivot_upos == 'VERB'): pattern=f"pattern {{PV[upos=VERB]; PV[VerbForm=Fin]; PV-[nsubj]->S; S>>PV; meta.sent_id = \"{sentence_json['metaJson']['sent_id']}\";}}"
    elif (pivot_upos == 'AUX'): pattern=f"pattern {{PV[upos=AUX]; PV[VerbForm=Fin]; HPV->PV; HPV-[nsubj]->S;S>>PV; meta.sent_id = \"{sentence_json['metaJson']['sent_id']}\";}}"
    else: return 'Null'

    pattern = Request(pattern)
    sentence_conll = sentenceJsonToConll(sentence_json)
    corpus = Corpus(sentence_conll)
    occurences = corpus.search(pattern)
    
    if occurences:
        for occ in occurences:
            if occ['matching']['nodes']['PV'] == pivot_id:
             try:
              return occ['matching']['nodes']['S']
             except: 
              return' Null'
 
    return 'Null'  


def get_subordinate_conj_single(sentence_json, pivot_id, pivot_upos):
    # verbatim query on a specified sentence. Then filter the result by pivot_id and extract data
    if(pivot_upos == 'VERB'): pattern=f"pattern {{ PV[upos=VERB] ; PV[VerbForm=Fin];PV -[mark]-> M; meta.sent_id = \"{sentence_json['metaJson']['sent_id']}\";}}"
    elif (pivot_upos == 'AUX'): pattern=f"pattern {{ PV[upos=AUX]; HPV->PV;HPV -[mark]-> M; meta.sent_id = \"{sentence_json['metaJson']['sent_id']}\";}}"
    else: return 'Null'

    pattern = Request(pattern)
    sentence_conll = sentenceJsonToConll(sentence_json)
    corpus = Corpus(sentence_conll)
    occurences = corpus.search(pattern)

    if occurences:
         for occ in occurences:
            if occ['matching']['nodes']['PV'] == pivot_id:
             try:
              form= sentence_json['treeJson']['nodesJson'][occ['matching']['nodes']['M']]['FORM']
              return form
             except: 
              return 'Null'
 
    return 'Null'  

def get_subordinate_conj_multi(sentence_json, pivot_id, pivot_upos):
    # verbatim query on a specified sentence. Then filter the result by pivot_id and extract data
    if(pivot_upos == 'VERB'): pattern=f"pattern {{ PV[upos=VERB];PV[VerbForm=Fin]; PV -[mark]-> M1; PV-[mark]->M2; meta.sent_id = \"{sentence_json['metaJson']['sent_id']}\";}}"
    elif (pivot_upos == 'AUX'): pattern=f"pattern {{ PV[upos=AUX]; V->PV; V -[mark]-> M1; V-[mark]->M2; meta.sent_id = \"{sentence_json['metaJson']['sent_id']}\";}}"
    else: return 'Null'

    pattern = Request(pattern)
    sentence_conll = sentenceJsonToConll(sentence_json)
    corpus = Corpus(sentence_conll)
    occurences = corpus.search(pattern)

    if occurences:
         for occ in occurences:
            if occ['matching']['nodes']['PV'] == pivot_id:
             try:
              form= sentence_json['treeJson']['nodesJson'][occ['matching']['nodes']['M1']]['FORM']+ "|" + \
                    sentence_json['treeJson']['nodesJson'][occ['matching']['nodes']['M2']]['FORM']
              return form
             except: 
              return 'Null'
 
    return 'Null'  



def get_subj_determiner_single(sentence_json, pivot_id, pivot_upos):
    # verbatim query on a specified sentence. Then filter the result by pivot_id and extract data
    if(pivot_upos == 'VERB'): pattern=f"pattern {{ PV[upos=VERB]; PV[VerbForm=Fin]; PV -[nsubj]-> S ; S-[det]->D; meta.sent_id = \"{sentence_json['metaJson']['sent_id']}\";}}"
    elif (pivot_upos == 'AUX'): pattern=f"pattern {{ PV[upos=AUX]; PV[VerbForm=Fin]; HPV->PV; HPV -[nsubj]-> S; S-[det]->D; meta.sent_id = \"{sentence_json['metaJson']['sent_id']}\";}}"
    else: return 'Null'

    pattern = Request(pattern)
    sentence_conll = sentenceJsonToConll(sentence_json)
    corpus = Corpus(sentence_conll)
    occurences = corpus.search(pattern)

    if occurences:
         for occ in occurences:
            if  occ['matching']['nodes']['PV'] == pivot_id:
             try:
              form= sentence_json['treeJson']['nodesJson'][occ['matching']['nodes']['D']]['FORM']
              return form
             except: 
              return 'Null'
 
    return 'Null'  

def get_subj_determiner_multi(sentence_json, pivot_id, pivot_upos):
    # verbatim query on a specified sentence. Then filter the result by pivot_id and extract data
    if(pivot_upos == 'VERB'): pattern=f"pattern {{ PV[upos=VERB]; PV[VerbForm=Fin]; PV -[nsubj]-> S ; S-[det]->D1; S-[det]->D2; meta.sent_id = \"{sentence_json['metaJson']['sent_id']}\";}}"
    elif (pivot_upos == 'AUX'): pattern=f"pattern {{ PV[upos=AUX]; PV[VerbForm=Fin]; HPV->PV; HPV -[nsubj]-> S; S-[det]->D1; S-[det]->D2; meta.sent_id = \"{sentence_json['metaJson']['sent_id']}\";}}"
    else: return 'Null'

    pattern = Request(pattern)
    sentence_conll = sentenceJsonToConll(sentence_json)
    corpus = Corpus(sentence_conll)
    occurences = corpus.search(pattern)

    if occurences:
         for occ in occurences:
            if occ['matching']['nodes']['PV'] == pivot_id:
             try:
              #print(occ)
              form= sentence_json['treeJson']['nodesJson'][occ['matching']['nodes']['D1']]['FORM']+ "|" + \
                    sentence_json['treeJson']['nodesJson'][occ['matching']['nodes']['D2']]['FORM']
              return form
             except: 
              return 'Null'
 
    return 'Null'  




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process files from input directory.")
    parser.add_argument("-i",  type=Path,dest="input_dir", default=Path("input"), help="Path to input directory. Default: input")
    parser.add_argument("-o",  type=Path,dest="output_dir", default=Path("output"), help="Path to output directory. Default: output")
    parser.add_argument("-t",  type=str, dest="output_type", choices=["excel", "csv"], default="excel", help="Output type excel/csv. Default: excel")

    args = parser.parse_args()

    # create output directory if it doesn't exist
    args.output_dir.mkdir(parents=True, exist_ok=True)
    
    dir_path = args.input_dir
    print(f"processing {dir_path}")
    for conll_file in os.listdir(dir_path):
        
        if conll_file.lower().endswith(".conllu"):
            conll_file = os.path.join(dir_path, conll_file)
            sentences_json = load_sentences_json(conll_file)
            print(f"processing:::: {conll_file}/{len(sentences_json)}")
            data = []
            i=0
            for sent_id, sentence in sentences_json.items():
                i=i+1
                print(f"sentence {i}/{len(sentences_json)}")
                for token in sentence['treeJson']['nodesJson'].values():
                    if 'VerbForm' in token['FEATS'].keys() and token['FEATS']['VerbForm'] == 'Fin': 
                        pivot = token 
                        first_part, second_part = get_sentences_part(sentence, int(pivot['ID']), 0)
                        #Get governors
                        gov = get_gov(sentence, pivot['HEAD'])
                        if  gov =='Null':
                           gov_of_gov={}
                           gov_of_gov['DEPREL']='Null'
                        else: 
                           gov_of_gov = get_gov(sentence, gov['HEAD'])
                           if  gov_of_gov =='Null':
                              gov_of_gov_of_gov={}
                              gov_of_gov_of_gov['DEPREL']='Null'
                           else:
                              gov_of_gov_of_gov = get_gov(sentence, gov_of_gov['HEAD'])
                        # Get subject
                        subject = get_subj(sentence, pivot['ID'])['subject'] if get_subj(sentence, pivot['ID']) else 'Null'

                        # Basic data
                        entry = {
                            "Sent_id": sent_id,
                            "pivot": pivot['FORM'],
                            'Pos Pivot': pivot['UPOS'],
                            'Person': pivot['FEATS']['Person'] if 'Person' in pivot['FEATS'].keys() else 'Null',
                            'Number': pivot['FEATS']['Number'] if 'Number' in pivot['FEATS'].keys() else 'Null',
                            'Function of pivot': pivot['DEPREL'] if pivot['UPOS'] != 'AUX' else gov['DEPREL'],
                            'Conjugated verb function': get_conj(sentence, pivot),
                            'Auxiliary function': pivot['DEPREL'] if  pivot['UPOS'] == 'AUX' else 'Null',
                        }
                        # Subject: 
                        entry['Subject UPOS']=subject['UPOS'] if subject != 'Null' else 'Null'
                        entry['Subject pronoun number'],entry['Subject pronoun person'],entry['Subject pronoun gender'],entry['Subject pronoun form']=  get_subj_pron(sentence,pivot['ID'],pivot['UPOS'])
                        subject_prev=get_subj_position_prev(sentence,pivot['ID'],pivot['UPOS'])
                        subject_post=get_subj_position_postv(sentence,pivot['ID'],pivot['UPOS'])
                        if (subject_prev !='Null'): entry['Subject position'] = 'PreV'
                        elif (subject_post!='Null'): entry['Subject position'] = 'PostV'
                        else: entry['Subject position']='Null'
                        entry['Subject determiner form single'] = get_subj_determiner_single(sentence,pivot['ID'],pivot['UPOS'])
                        entry['Subject determiner form multi'] = get_subj_determiner_multi(sentence,pivot['ID'],pivot['UPOS'])
                        # Enonciative particle:
                        entry['Enunciative particle'] = get_enonciatif(sentence,pivot['ID'],pivot['UPOS'])
                        # Subordinating conjunction:
                        entry['Subordinating conjunction'] = get_subordinate_conj_single(sentence,pivot['ID'],pivot['UPOS'])
                        entry['Subordinating conjunction multimark'] = get_subordinate_conj_multi(sentence,pivot['ID'],pivot['UPOS'])
                        # Coordinating conjunction:
                        entry['Coordinating Conjunction ID'] = get_coordination_conj_id(sentence,pivot['ID'],pivot['UPOS'])
                        entry['Coordinating Conjunction Form'] = get_coordination_conj_form(sentence, pivot['ID'],pivot['UPOS'])
                        # Function of conj:
                        entry['Function of conj of conj']='Null'
                        entry['Function of conj']='Null'
                        if (pivot['DEPREL'] == 'conj'):
                          if (pivot['UPOS'] == 'VERB'): 
                             entry['Function of conj']=gov['DEPREL']
                             if(gov['DEPREL']=='conj'):
                               entry['Function of conj of conj']=gov_of_gov['DEPREL'] 
                          else: 
                             entry['Function of conj']=gov_of_gov['DEPREL'] 
                             if(gov_of_gov['DEPREL']=='conj'):
                               entry['Function of conj of conj']=gov_of_gov_of_gov['DEPREL'] 
                        # context
                        entry['Left context'] = first_part
                        entry['Right context'] = second_part
                        data.append(entry)

            base_outfile_name=os.path.join(args.output_dir,os.path.basename(conll_file.replace('.conllu', '_final_extractions')))
            if(args.output_type=="excel"):  
                excel_file_name = base_outfile_name+".xlsx"
                sheet_name = 'extractions'
                generate_excel_file(data, sheet_name, excel_file_name)
            else:
                csv_file_name = base_outfile_name+".csv"
                generate_csv_file(data, csv_file_name)


