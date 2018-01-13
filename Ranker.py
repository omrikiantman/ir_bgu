from math import sqrt


class Ranker:

    def __init__(self, relevant_documents, query_terms, query_desc_terms):
        self.relevant_documents = relevant_documents
        self.query_terms = query_terms
        self.query_desc_terms = query_desc_terms

    def calculate_ranked_documents(self):
        # calculate each document rank by the cosSim & bm25 formula and some other attributes
        query_weight = self.__calculate_query_weight()
        for relevant_document in self.relevant_documents:
            cos_sim = float(relevant_document.tfidf_score)/sqrt(float(query_weight)*float(relevant_document.document_weight))
            relevant_document.final_score = cos_sim*float(relevant_document.bm25)
        return sorted(self.relevant_documents, reverse=True)

    def __calculate_query_weight(self):
        # calculate query weight, assuming equal weight for each word
        terms = set(self.query_terms + self.query_desc_terms)
        return len(terms)
