
class TermDict:
    PRINT_DELIMITER = '*'

    def __init__(self, name, df, tf, pointer, bytes, is_cache=False):
        # the pointer is the byte address in the file, the bytes is the size of the posting record
        self.name = name
        self.df = df
        self.tf = tf
        self.pointer = pointer
        self.bytes = bytes
        self.is_cache = is_cache

    def __cmp__(self, other):
        # compare first by df, then by tf
        if self.df < other.df:
            return -1
        elif self.df > other.df:
            return 1
        else:
            if self.tf < other.tf:
                return -1
            elif self.tf > other.tf:
                return 1
            else:
                return 0

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.name == other.name
        return False

    def __repr__(self):
        return "%s%s%s%s%s%s%s" % (self.tf, TermDict.PRINT_DELIMITER,
                                   self.df,TermDict.PRINT_DELIMITER,
                                   self.pointer,TermDict.PRINT_DELIMITER, self.bytes)

    def __str__(self):
        return "%s%s%s%s%s%s%s" % (self.tf, TermDict.PRINT_DELIMITER,
                                   self.df,TermDict.PRINT_DELIMITER,
                                   self.pointer,TermDict.PRINT_DELIMITER, self.bytes)


def create_main_dictionary_from_disk(path, cache_keys):
    # create main dictionary from disk
    main_dictionary = {}
    with open(path,'r') as cache_file:
        while True:
            line = cache_file.readline()
            if line == '':
                return main_dictionary
            # find the :
            term_cut_point = line.index(':')
            term_name = line[0:term_cut_point]
            # find the rest of the information for the term.
            tf, df, pointer, bytes_var = line[term_cut_point + 1:len(line) - 1].split(TermDict.PRINT_DELIMITER)
            main_dictionary[term_name] = TermDict(term_name, df, tf, pointer, bytes_var, term_name in cache_keys)
