# parsing text files into tokens
import re
import Term
from collections import defaultdict


class Parse:
    def __init__(self):
        self.tokens = defaultdict(lambda: Term.Term())

    def parse_document(self, document):
        last_word = None; last_char = None; last_capital = False;
        current_word = ''; is_number = None; num_contains_dot = None
        print('hi')
        for current_char in document:
            if ending_char(current_char) :
                print ("%s is number %s num_contains_dot %s" %(current_word, is_number, num_contains_dot) )
                if not ending_char(last_char):
                    last_char = current_char
                    last_word = current_word
                    is_number = None
                    current_word =''
                    num_contains_dot = None
                continue
            current_word += current_char
            if current_char.isdigit():
                if is_number is None:
                    is_number = True
            elif is_dot(current_char) and is_number is not None and is_number is True:
                num_contains_dot = True
                continue
            else:
                is_number = False
            last_char = current_char



    def parse_text(self):
        if self.text is not None:
            self.remove_double_spaces()
            self.split_to_tokens()

    def remove_double_spaces(self):
        self.text = re.sub(" +", " ", self.text)

    def split_to_tokens(self):
        for word in self.text.split(" "):
            self.tokens[word].add_count()


def is_letter(char):
    pass


def is_punctuation(char):
    pass


def is_dot(char):
    return char == "."


def is_slash(char):
    return char == "/"


def is_new_line(char):
    return char == "\n"


def ending_char(char):
    return char.isspace() or is_new_line(char)
