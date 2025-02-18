from conllup.conllup import readConlluFile, sentenceJsonToConll

def load_corpus_json(file_path):
    return readConlluFile(file_path)

def convert_upos(file_path):
    sentences_json = load_corpus_json(file_path)
    with open(file_path, "w") as outfile:
        for sentence_json in sentences_json:
            for token in sentence_json['treeJson']['nodesJson'].values():
                token['UPOS'] = token['MISC']['gold_pos']
            sentence_conll = sentenceJsonToConll(sentence_json)
            outfile.write(sentence_conll + "\n")
    
    outfile.close()
            
    

