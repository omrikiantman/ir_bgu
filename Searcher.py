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
        # given a query, search for  relveant documents and rank them
        query_terms = self.__string_to_terms(self.query)
        query_desc_terms = self.__string_to_terms(self.query_desc) if self.query_desc is not None else []
        # in case there's a query description, treat it as part of the query
        relevant_documents = self.__retrieve_relevant_documents(query_terms + query_desc_terms)
        ranker = Ranker(relevant_documents.values(), query_terms, query_desc_terms)
        return ranker.calculate_ranked_documents()

    def __string_to_terms(self, string):
        # given a string, parse into terms. in this case it's for a query
        parser = Parse(globs.constants, globs.stop_words, self.is_stemming)
        parser.parse_document(string)
        return parser.terms.keys()

    def __retrieve_relevant_documents(self, query_terms):
        # find relevant documents per query
        num_of_documents = globs.num_of_documents
        relevant_documents = {}
        posting_file = None
        for word in query_terms:
            # loop over each word in the query, add score to each Ranked Document
            term_dict = globs.main_dictionary.get(word,False)
            if term_dict is False:
                # if the word inside the query isn't located in the main dictionary
                continue
            df = term_dict.df
            pointer = int(term_dict.pointer)
            postings = []
            is_cache = term_dict.is_cache
            if is_cache is True:
                # in case the field was in the cache, first upload it's postings from their, then from disk
                cache_element = globs.cache[word]
                postings += cache_element.doc_list
                pointer = int(cache_element.pointer)
                if int(cache_element.bytes) == 0:
                    pointer = 0
            if pointer != 0:
                # read postings from disk (rest of cache or regular)
                first_letter = word[0] if word[0].isalpha() else '0'
                posting_file_path = os.path.join(self.postings_path,
                                                 ''.join([Indexer.STEMMING_PREFIX if self.is_stemming is True else '',
                                                          Indexer.POSTING_PREFIX, first_letter, '.txt']))
                posting_file = PostingFile.PostingFile(posting_file_path, '0', False)
                posting_file.read_line_by_position(pointer, is_cache, word)
                postings += posting_file.postings
            for posting_term in postings:
                # for each posting term, update it's relevant document score by tfidf & bm25
                document = globs.documents_dict[posting_term.docno]
                term_tf = posting_term.get_tf_value()
                tfidf = (term_tf / document.max_tf) * log(float(num_of_documents) / float(df), 2)
                bm25 = self.__calculate_bm25(document.real_length, df, posting_term.count)
                ranked_document = relevant_documents.get(posting_term.docno, False)
                if ranked_document is not False:
                    ranked_document.update_score(tfidf, word, bm25)
                else:
                    relevant_documents[posting_term.docno] = RankedDocument(posting_term.docno, tfidf, word,
                                                                            document.weight, bm25)
            if posting_file is not None:
                posting_file.close_posting_file()
        return relevant_documents

    def __calculate_bm25(self, document_size, df, term_tf):
        # calculate each term bm25 score according to the bm25 forumla
        b = 0.75
        k1 = 1.5
        idf = log((float(globs.num_of_documents) - float(df) + 0.5)/(float(df) + 0.5))
        b_comp = 1 - b + b*(float(document_size)/float(globs.average_doc_size))
        bm = (float(term_tf)*(k1+1))/(float(term_tf)+k1*b_comp)
        return bm*idf

