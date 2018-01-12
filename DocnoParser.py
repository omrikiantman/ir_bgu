# this is the docno parser
import re
from nltk import sent_tokenize, PorterStemmer, word_tokenize
import shared_variables as globs
from Parse import Parse
from math import log
import traceback
import sys
import os


class DocnoParser:
    def __init__(self, docno, file_name, is_stemming, max_tf):
        self.docno = docno
        self.file_name = file_name
        self.is_stemming = is_stemming
        self.max_tf = int(max_tf)
        self.content = None

    def load_docno(self, file_path):
        # load the content of the document
        with open(os.path.join(file_path, 'corpus', self.file_name), 'r') as doc_file_content:
            documents_raw = doc_file_content.read()
            documents = re.findall(r'<DOC>(.*?)</DOC>', documents_raw, re.DOTALL)
            # find the right document
            for doc in documents:
                docno = re.findall(r'<DOCNO>(.*?)</DOCNO>', doc, re.DOTALL)[0].strip()
                if self.docno == docno:
                    self.content = re.findall(r'<TEXT>(.*?)</TEXT>', doc, re.DOTALL)[0]
                    # strip off xml tags that could come in the way - cancled
                    # self.content = re.sub('<[^>]*>', '', self.content)
                    return True
        return False

    def find_top_5_sentences(self):
        # return a list of 5 top sentences, sorted by sum(tfidf) for each word in a sentence
        if self.is_stemming:
            stemmer = PorterStemmer()
        # find the tf of each word in th
        parser = Parse(globs.constants, globs.stop_words, self.is_stemming)
        parser.parse_document(self.content)
        terms = parser.terms
        sentences = sent_tokenize(self.content)
        parsed_sentences = []
        try:
            for position, sentence in enumerate(sentences):
                # assign grade for each document
                sentence_parser = Parse(globs.constants, globs.stop_words, self.is_stemming)
                sentence_parser.parse_document(sentence)
                sentence_terms = sentence_parser.terms
                sentence_length = sum([int(term.count) for key, term in sentence_terms.iteritems()])
                if sentence_length == 0:
                    continue
                sentence_score = sum([(float(terms[token].count)/self.max_tf)
                                      * log(float(globs.num_of_documents)/float(globs.main_dictionary[token].df), 2)
                                      for token in sentence_terms])/float(sentence_length)
                parsed_sentences.append((sentence, sentence_score, position))
            top_5_sentences = sorted(parsed_sentences, key=lambda tup: tup[1], reverse=True)[:5]
            ranked_5_sentences = []
            for rank, sentence in enumerate(top_5_sentences):
                ranked_5_sentences.append((sentence[0], rank+1, sentence[2]))
            return ranked_5_sentences
        except Exception as err:
            print (err)
            traceback.print_exc(file=sys.stdout)