class RankedDocument:
    PRINT_DELIMITER = '*'

    def __init__(self, docno, score, term, document_weight):
        self.docno = docno
        self.score = score
        self.terms = {term}
        self.document_weight = document_weight
        self.final_score = 0

    def update_score(self, score, term):
        self.score += score
        self.terms.add(term)

    def __repr__(self):
        return "%s%s%s%s%s%s%s" % (self.docno, RankedDocument.PRINT_DELIMITER, self.score,
                                   RankedDocument.PRINT_DELIMITER, str(self.terms),
                                   RankedDocument.PRINT_DELIMITER, self.final_score)

    def __str__(self):
        return "%s%s%s%s%s%s%s" % (self.docno, RankedDocument.PRINT_DELIMITER, self.score,
                                   RankedDocument.PRINT_DELIMITER, str(self.terms),
                                   RankedDocument.PRINT_DELIMITER, self.final_score)

    def __cmp__(self, other):
        self.final_score = float(self.final_score)
        other.final_score = float(other.final_score)
        if self.final_score > other.final_score:
            return 1
        if self.final_score < other.final_score:
            return -1
        return 0
