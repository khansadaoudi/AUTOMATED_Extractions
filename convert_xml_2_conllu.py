from conllup.conllup import sentenceJsonToConll
import xml.etree.ElementTree as ET

def load_corpus_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    return root

def convert_xml_2_conllu(file_path):
    root = load_corpus_xml(file_path)

    sentences_json = {}
    last_sent_id = None
    last_index = 1


    for book in root.findall(".//div[@type='book']"):
        book_id = book.get('n')
        for chapter in book.findall(".//div[@type='chapter']"):
            chapter_id = chapter.get('n')
            for section in chapter.findall(".//div[@type='section']"):
                section_id = section.get('n')
                for p in section.findall(".//p"):
                    p_id = p.get('n')
                    for sentence in p.findall(".//s"):

                        if 'n' in sentence.attrib.keys():
                            sentence_id = sentence.get('n')
                            sent_id = f"{book_id}_{chapter_id}_{section_id}_{p_id}_{sentence_id}"
                            sentences_json[sent_id] = {
                                'treeJson': {
                                    'nodesJson': {},
                                    'groupsJson': {},
                                    'enhancedNodesJson': {}
                                }, 
                                'metaJson': {
                                    'sent_id': sent_id
                                },  
                            }
                            last_sent_id = sent_id
                            last_index = 1

                        elif last_sent_id:
                            sent_id = last_sent_id
                        
                        else:
                            continue

                        for token in sentence.findall('.//w'):
                            if token.findall('.//choice'):
                                token_form  = token.find('.//choice').find('.//corr').text
                            else:
                                token_form = token.text
                            token_json = {
                                'ID': str(last_index),
                                'FORM': token_form,
                                'LEMMA': token.attrib['lemma'] if 'lemma' in token.attrib.keys() else '_',
                                'UPOS': token.attrib['udpos'] if 'udpos' in token.attrib.keys() else '_',
                                'XPOS': '',
                                'HEAD': token.attrib['head'] if 'head' in token.attrib.keys() else '_',
                                'DEPREL': token.attrib['function'] if 'function' in token.attrib.keys() else '_',
                                'DEPS': {},
                                'MISC': {
                                    'gold_pos': token.attrib['udpos']   
                                } if 'udpos' in token.attrib.keys() else {},
                                'FEATS': {}
                            }
                            sentences_json[sent_id]['treeJson']['nodesJson'][str(last_index)] = token_json
                            last_index += 1
                        
    return sentences_json

def write_conllu(sentences_json, file_path):
    with open(file_path, "w") as outfile:
        for sentence_json in sentences_json.values():
            sentence_conll = sentenceJsonToConll(sentence_json)
            outfile.write(sentence_conll + "\n")
    outfile.close()                       
    

if __name__ == "__main__":
    path_file = "Files/StyleAnjou_lemma_RevNR.xml"
    sentences_json  = convert_xml_2_conllu(path_file)
    write_conllu(sentences_json, "StyleAnjou_lemma_RevNR.conllu")