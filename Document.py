# parses a document
import Parse


class Document:
    def __init__(self, content, constants, stop_words, is_stemming=False):
        # init function for document
        self.content = content
        self.constants = constants
        self.stop_words = stop_words
        self.is_stemming = is_stemming
        self.length = 0
        self.max_tf = 1
        self.docno = 0
        self.num_of_words = 1
        self.terms = None

    def parse_document(self):
        # extract all relevant document fields via the parser
        parser = Parse.Parse(self.constants, self.stop_words, self.is_stemming)
        parser.parse_document(self.content)
        self.length = parser.position
        self.max_tf = parser.max_tf
        self.docno = parser.docno
        self.terms = parser.terms
        del parser
        self.num_of_words = len(self.terms)
