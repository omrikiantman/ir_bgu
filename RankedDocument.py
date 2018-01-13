class RankedDocument:
    PRINT_DELIMITER = '*'

    def __init__(self, docno, tfidf_score, term, document_weight, bm25):
        self.docno = docno
        self.tfidf_score = tfidf_score
        self.terms = {term}
        self.document_weight = document_weight
        self.bm25 = bm25
        self.final_score = 0

    def update_score(self, tfidf_score, term, bm25):
        # update the tfidf & bm25 score
        self.tfidf_score += tfidf_score
        self.bm25 += bm25
        self.terms.add(term)

    def __repr__(self):
        return "%s%s%s%s%s%s%s" % (self.docno, RankedDocument.PRINT_DELIMITER, self.tfidf_score,
                                   RankedDocument.PRINT_DELIMITER, str(self.terms),
                                   RankedDocument.PRINT_DELIMITER, self.final_score)

    def __str__(self):
        return "%s%s%s%s%s%s%s" % (self.docno, RankedDocument.PRINT_DELIMITER, self.tfidf_score,
                                   RankedDocument.PRINT_DELIMITER, str(self.terms),
                                   RankedDocument.PRINT_DELIMITER, self.final_score)

    def __cmp__(self, other):
        # compare between documents according to their final_score
        self.final_score = float(self.final_score)
        other.final_score = float(other.final_score)
        if self.final_score > other.final_score:
            return 1
        if self.final_score < other.final_score:
            return -1
        return 0
