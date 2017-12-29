import Term


class CacheTerm:
    PRINT_DELIMITER = '*'

    def __init__(self, name, pointer, bytes, doc_list=None):
        self.name = name
        self.pointer = pointer
        self.bytes = bytes
        self.doc_list = doc_list

    def __repr__(self):
        return "%s%s%s%s%s" % (self.pointer, CacheTerm.PRINT_DELIMITER,
                               self.bytes, CacheTerm.PRINT_DELIMITER,
                               str(self.doc_list))

    def __str__(self):
        return "%s%s%s%s%s" % (self.pointer, CacheTerm.PRINT_DELIMITER,
                               self.bytes, CacheTerm.PRINT_DELIMITER,
                               str(self.doc_list))


def create_cache_from_disk(path):
    # read a cache file from the disk and return a dictionary
    cache_dict = {}
    with open(path, 'r') as cache_file:
        while True:
            line = cache_file.readline()
            if line == '':
                return cache_dict
            # find the :
            term_cut_point = line.index(':')
            term_name = line[0:term_cut_point]
            # find the first delimiter to find the pointer.
            pointer_cut_point = line.index(CacheTerm.PRINT_DELIMITER)
            pointer = line[term_cut_point + 1:pointer_cut_point]
            line = line[pointer_cut_point + 1:]
            bytes_cut_point = line.index(CacheTerm.PRINT_DELIMITER)
            bytes_var = line[:bytes_cut_point]
            postings = line[bytes_cut_point:]
            postings_size = len(postings)
            # remove the '*[' and ']\n'
            postings = postings[2:len(postings) - 2]
            postings = Term.postings_string_to_array_of_terms(term_name, postings)
            cache_dict[term_name] = CacheTerm(term_name, pointer, bytes_var, postings)
