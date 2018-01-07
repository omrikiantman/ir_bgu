import os
import Term


class PostingFile:
    MAX_ROWS_TO_READ = 3

    def __init__(self, path, name, is_delete=True):
        self.path = path
        self.name = name
        self.is_delete = is_delete
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
            if self.is_delete is True:
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
        chars_to_del = 2 if postings[1] == '[' else 1
        postings = postings[chars_to_del:postings_size - chars_to_del]
        self.postings = Term.postings_string_to_array_of_terms(self.term_name, postings)

    def read_line_by_position(self, position, is_cache):
        self.file.seek(int(position))
        if not is_cache:
            self.parse_posting_file_line(self.file.readline())
        else:
            pass
        # TODO add something to read & parse the right position if it's a cache record

    def close_posting_file(self):
        self.file.close()
