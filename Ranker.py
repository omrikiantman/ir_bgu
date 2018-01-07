from math import sqrt


class Ranker:

    def __init__(self, relevant_documents, query_terms, query_desc_terms):
        self.relevant_documents = relevant_documents
        self.query_terms = query_terms
        self.query_desc_terms = query_desc_terms

    def calculate_ranked_documents(self):
        # calulate each document rank by the cosSim formula and some other attributes
        query_weight = self.__calculate_query_weight()
        for relevant_document in self.relevant_documents:
            relevant_document.final_score = relevant_document.score/sqrt(query_weight*relevant_document.document_weight)
        return sorted(self.relevant_documents, reverse=True)


    def __calculate_query_weight(self):
        # calculate query weight, assuming equal weight for each word
        terms = set(self.query_terms + self.query_desc_terms)
        return len(terms)
