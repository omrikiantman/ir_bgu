import shared_variables as globs
from Parse import Parse
import PostingFile
from math import log
from RankedDocument import RankedDocument
import os
from Indexer import Indexer
from Ranker import Ranker


class Searcher:
    def __init__(self, query, is_stemming, postings_path, query_desc=None):
        self.query = query
        self.is_stemming = is_stemming
        self.postings_path = postings_path
        self.query_desc = query_desc

    def search_query(self):
        query_terms = self.__string_to_terms(self.query)
        query_desc_terms = self.__string_to_terms(self.query_desc) if self.query_desc is not None else []
        relevant_documents = self.__retrieve_relevant_documents(query_terms + query_desc_terms)
        ranker = Ranker(relevant_documents.values(), query_terms, query_desc_terms)
        return ranker.calculate_ranked_documents()

    def __string_to_terms(self,string):
        parser = Parse(globs.constants, globs.stop_words, self.is_stemming)
        parser.parse_document(string)
        return parser.terms.keys()

    def __retrieve_relevant_documents(self, query_terms):
        num_of_documents = globs.num_of_documents
        relevant_documents = {}
        for word in query_terms:
            term_dict = globs.main_dictionary.get(word,False)
            if term_dict is False:
                continue
            df = term_dict.df
            # TODO - get the position first by cache then by postings
            is_cache = False
            first_letter = word[0] if word[0].isalpha() else '0'
            posting_file_path = os.path.join(self.postings_path,
                                             ''.join([Indexer.STEMMING_PREFIX if self.is_stemming is True else '',
                                                      Indexer.POSTING_PREFIX, first_letter, '.txt']))
            posting_file = PostingFile.PostingFile(posting_file_path, '0', False)
            posting_file.read_line_by_position(term_dict.pointer, is_cache)
            for posting_term in posting_file.postings:
                document = globs.documents_dict[posting_term.docno]
                tfidf = (posting_term.get_tf_value() / document.max_tf) * log(float(num_of_documents) / float(df), 2)
                ranked_document = relevant_documents.get(posting_term.docno, False)
                if ranked_document is not False:
                    ranked_document.update_score(tfidf, word)
                else:
                    relevant_documents[posting_term.docno] = RankedDocument(posting_term.docno, tfidf, word,
                                                                            document.weight)
            posting_file.close_posting_file()
        return relevant_documents
