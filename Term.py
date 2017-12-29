# define a term in a document


class Term:

    def __init__(self, name, is_header, first_location, docno=0, count=1):
        self.name = name
        self.count = count
        self.is_header = is_header
        self.docno = docno
        self.first_location = first_location

    def add_count(self):
        self.count = self.count + 1

    def __repr__(self):
        return "%s|%s|%s|%s" % (self.count, 1 if self.is_header is True else 0, self.first_location, self.docno)

    def __str__(self):
        return "%s|%s|%s|%s" % (self.count, 1 if self.is_header is True else 0, self.first_location, self.docno)

    def __cmp__(self, other):
        # compare to for each term, by name, then by is_header, then by first location.
        if self.name < other.name:
            return -1
        elif self.name > other.name:
            return 1
        else:
            if self.is_header is True and (other.is_header is None or other.is_header is False):
                return 1
            elif other.is_header is True and (self.is_header is None or self.is_header is False):
                return -1
            elif other.is_header is True and self.is_header is True:
                if self.count < other.count:
                    return -1
                elif self.count > other.count:
                    return 1
                else:
                    return 0
            elif self.first_location < 200 or other.first_location < 200:
                if self.first_location < other.first_location:
                    return 1
                elif self.first_location > other.first_location:
                    return -1
                else:
                    return 0
            else :
                if self.count < other.count:
                    return -1
                elif self.count > other.count:
                    return 1
                else:
                    if self.first_location < other.first_location:
                        return 1
                    elif self.first_location > other.first_location:
                        return -1
                    else:
                        return 0

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.name == other.name
        return False

    def __hash__(self):
        return hash(self.name)


def term_string_to_term_object(name, term_string):
    # convert a term string, the was it's written in disk, to a term object
    count, is_header, first_location, docno = term_string.split("|")
    return Term(name,bool(int(is_header)), int(first_location), docno,int(count))


def postings_string_to_array_of_terms(term_name, posting_string):
    # convert a list of terms, written in the disk, to an array of terms
    return [term_string_to_term_object(term_name, term_string) for term_string in posting_string.split(', ')]
