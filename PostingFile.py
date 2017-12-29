import os
import Term


class PostingFile:
    MAX_ROWS_TO_READ = 3

    def __init__(self, path, name):
        self.path = path
        self.name = name
        self.file = open(path, 'r')
        self.term_name = None
        self.postings = None
        self.lines_array = []
        self.read_next_term_string()

    def read_next_term_string(self):
        # read the next string from a posting file
        if not bool(self.lines_array):
            self.lines_array = [self.file.readline() for dummy in range(PostingFile.MAX_ROWS_TO_READ)]
        line = self.lines_array[0]
        if line.strip() == '':
            self.file.close()
            os.remove(self.path)
            return False
        self.parse_posting_file_line(line)
        del self.lines_array[0]
        return True

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.name == other.name
        return False

    def __hash__(self):
        return hash(self.name)

    def parse_posting_file_line(self, line):
        # parse a line from a posting file, convert it to a terms list and find the term name
        # find the :
        cut_point = line.index(':')
        self.term_name = line[0:cut_point]
        postings = line[cut_point:]
        postings_size = len(postings)
        # remove the ':[' and ']\n'
        postings = postings[2:postings_size - 2]
        self.postings = Term.postings_string_to_array_of_terms(self.term_name, postings)
