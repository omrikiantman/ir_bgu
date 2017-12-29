
class DocumentDict():
    PRINT_DELIMITER = '*'

    def __init__(self, docno, max_tf, length, num_of_words):
        self.docno = docno
        self.max_tf = max_tf
        self.length = length
        self.num_of_words = num_of_words

    def __repr__(self):
        return "%s%s%s%s%s" % (self.max_tf, DocumentDict.PRINT_DELIMITER,
                                   self.length,DocumentDict.PRINT_DELIMITER,
                                   str(self.num_of_words))

    def __str__(self):
        return "%s%s%s%s%s" % (self.max_tf, DocumentDict.PRINT_DELIMITER,
                                   self.length,DocumentDict.PRINT_DELIMITER,
                                   str(self.num_of_words))
