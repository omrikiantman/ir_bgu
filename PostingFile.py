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
            self.lines_array = [self.file.readline().strip() for dummy in range(PostingFile.MAX_ROWS_TO_READ)]
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
        # remove the ':[' and ']'
        chars_to_del = 2 if postings[1] == '[' else 1
        postings = postings[chars_to_del:postings_size - chars_to_del + 1]
        self.postings = Term.postings_string_to_array_of_terms(self.term_name, postings)

    def read_line_by_position(self, position, is_cache, term_name=None):
        # given a specific position in the file (byte), read a line from there and parse it
        position = position - 1 if is_cache is True else position
        self.file.seek(int(position))
        line = self.file.readline().strip()
        if not is_cache:
            self.parse_posting_file_line(line)
        else:
            self.parse_posting_line_not_from_start(line, term_name)

    def parse_posting_line_not_from_start(self, line, term_name):
        # read a postings term not from the middle of the line, usually for a term in the cache
        # some sanity checks were made to avoid wicked errors.
        if line[0] == ',':
            line = line[1:].strip()
        elif line[1] == ',':
            line = line[2:].strip()
        self.postings = Term.postings_string_to_array_of_terms(term_name, line)

    def close_posting_file(self):
        self.file.close()
