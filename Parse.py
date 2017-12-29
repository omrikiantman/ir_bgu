# parsing text files into tokens
import Term
import sys
import traceback
from nltk import PorterStemmer


class Parse:
    ENDING_CHAR = ' '
    NO_CATEGORY = 0
    NUMBER_CATEGORY = 1
    NUMBER_WITH_DOT_CATEGORY = 2
    NUMBER_WITH_SLASH_CATEGORY = 3
    NUMBER_WRITTEN_CATEGORY = 4
    NUMBER_DD_CATEGORY = 5
    MONTH_ONLY_CATEGORY = 6
    MONTH_WITH_DAY_CATEGORY = 7
    CAPITAL_CATEGORY = 8
    PERCENT_CATEGORY = 9
    stemmed_terms = {}

    def __init__(self, constants, stop_words, is_stemming=False):
        # init function
        self.terms = dict()
        self.stop_words = stop_words
        self.current_word = ''
        self.init_all()
        self.constants = constants
        self.current_char = ''
        self.position = 0  # current position in the text
        self.tags = set()  # a set indicating all the tags that are read.
        self.is_xml_tag_now = None  # if we are currently pasring an xml tag, i.e. text between < >
        self.is_open_tag = None  # if the xml tag is an opener <TEXT> and not closer </TEXT>
        self.current_tag = ''  # a variable holding the current tag that is being parsed.
        self.is_header_now = None  # indicator for stating if the word that is parsed is between <HEADER> tags.
        # header tags are inside the yaml constants file.
        self.is_stemming = is_stemming
        self.stemmer = PorterStemmer()
        self.docno = 0  # the docno of the document
        self.is_docno_now = False  # var indicating if we are currently parsing the <docno> tag
        self.max_tf = 1  # save the tf of the word that has the maximum tf in the document.

    def parse_document(self, document):
        # loop over every character in the doc and decide what ot do with it
        try:
            for self.current_char in document:
                if self.is_xml_tag_now is not None:
                    # in case we're currently parsing an xml tag, i.e. between the <  >
                    self.parse_xml_tag()
                elif self.current_char == "<":
                    # if a new xml tag opener/closer pops up
                    if self.is_docno_now is True:
                        # if this tag was the document number, save it
                        self.docno = self.current_word
                    if self.current_word != '':
                        # if prior to the xml tag there was a word, e.g. hello</TEXT>, add it to the index
                        self.parse_word()
                    # if some how there are left overs in the temp string.
                    self.add_term_to_terms(self.temp_string)
                    self.init_all()
                    self.is_xml_tag_now = True
                    # we don't know yet if this is a closing xml tag </, this logic is tested the parse_xml_method
                    self.is_open_tag = True
                    self.current_tag = ''
                    continue
                elif self.current_tag == 'docno':
                    # when parsing docno tag, save only alphanumeric and dash chars
                    if self.current_char.isalpha() or self.current_char.isdigit() or self.current_char == '-':
                        self.current_word = self.current_word + self.current_char
                elif (self.current_char.isspace() and self.last_char == '.') or \
                        (self.current_word_category == Parse.CAPITAL_CATEGORY and self.current_char in ['\n', '\r']):
                    # if it's a new line or a new sentence, reset existing conditions
                    self.parse_word()
                    self.add_term_to_terms(self.temp_string)
                    self.init_all()
                    # if we are reading an xml Tag now
                elif self.is_number is True:
                    # when parsing a number
                    self.parse_char_when_is_number()
                else:
                    # when parsing chars when there are no categories
                    if self.current_word == '':
                        # when parsing the first character
                        if self.current_char.isdigit():
                            self.is_number = True
                        elif self.current_char.isupper():
                            self.is_capital = True
                        elif not self.current_char.isalpha():
                            continue
                        self.current_word += self.current_char
                        self.last_char = self.current_char
                    elif self.current_char.isalpha() or self.current_char.isdigit():
                        # no conditions at all, just add the letter
                        self.current_word += self.current_char
                        self.last_char = self.current_char
                    elif self.current_char == '.':
                        # a special case - we don't add dots to the word, but it's important to be aware of it.
                        self.last_char = self.current_char
                    else:
                        self.parse_word()
                        self.current_char = Parse.ENDING_CHAR
            if len(self.current_word) > 0:
                # special cases for the last words in each document
                self.parse_word()
            if len(self.temp_string) > 0:
                # special cases for the last words in each document
                self.add_term_to_terms(self.temp_string)
        except Exception as err:
            print (self.docno)
            print (err)
            traceback.print_exc(file=sys.stdout)

    def parse_xml_tag(self):
        # parse a string that is actually an xml tag -
        if self.current_char == " ":
            # if inside the tag there is a space, it implies that we now parse the tag features
            # I don't really care about features in the xml tag so I'm ignoring them
            self.is_xml_tag_now = False
        elif self.current_char == ">":
            # if we reached to a closing tag ">" , insert or remove from current tags
            self.is_xml_tag_now = None
            self.current_tag = self.current_tag.lower()
            if self.is_open_tag is True:
                # if there was no "/" at the start of the tag, add it to our tags dict
                self.tags.add(self.current_tag)
                if self.current_tag in self.constants['headers']:
                    self.is_header_now = True
                elif self.current_tag == 'docno':
                    self.is_docno_now = True
            else:
                # remove the tag.
                if self.current_tag in self.tags:
                    self.tags.remove(self.current_tag)
                if self.current_tag in self.constants['headers']:
                    self.is_header_now = False
                elif self.current_tag == 'docno':
                    self.is_docno_now = False
                self.current_tag == ''
        elif self.is_xml_tag_now is False:
            # we will reach this section in case we are parsing xml tag attributes, which we don't care about
            return
        elif self.current_tag == '' and self.current_char == '/':
            # if the tag is a closer tag - "</...>"
            self.is_open_tag = False
        else:
            self.current_tag = self.current_tag + self.current_char

    def parse_word(self):
        # parse a word
        try:
            if not self.last_char == Parse.ENDING_CHAR:
                # if last char was an ending char, we've already parsed. skip ahead !
                self.position = self.position + 1  # word position in text
                if len(self.current_word) == 0:
                    if self.temp_string != '':
                        self.add_term_to_terms(self.temp_string)
                elif self.current_word[-1] == '.':
                    # if sentence holds a dot in the end, remove it
                    self.current_word = self.current_word[:-1]
                elif self.is_number is True:
                    self.parse_word_when_is_number()
                elif self.current_word in self.constants['numbers']:
                    # transform a word number ("one") into a number "1"
                    self.parse_word_that_is_number()
                elif self.current_word in self.constants['big_numbers']:
                    # transform 'big numbers' like million into a number 1000000
                    self.parse_word_that_is_big_number()
                elif self.current_word in self.constants['percents']:
                    # if one of the "percent" words pop
                    self.parse_percent()
                elif self.current_word in self.constants['months']:
                    # if it's a month - parse it special
                    self.parse_month()
                elif self.is_capital is True:
                    # if it's a capital word
                    self.parse_capital()
                else:
                    self.parse_no_category()
                self.last_word_category = self.current_word_category
                self.init_vars()
        except Exception as err:
            template = "An exception of type {0} occurred. Arguments:{1}"
            message = template.format(type(err).__name__, err)
            print(message)
            traceback.print_exc(file=sys.stdout)
            print (self.docno)

    def parse_month(self):
        # pase a word that is a month "SEP" , "AUGUST" ..
        if self.last_word_category == Parse.NUMBER_DD_CATEGORY:
            # if a DD format was before the month, add them together
            self.current_word_category = Parse.MONTH_WITH_DAY_CATEGORY
            self.temp_string = self.temp_string + '/' + self.constants['months'][self.current_word]
        else:
            self.add_term_to_terms(self.temp_string)
            self.current_word_category = self.MONTH_ONLY_CATEGORY
            self.temp_string = self.current_word

    def parse_no_category(self):
        # parse without anything special
        self.current_word_category = Parse.NO_CATEGORY
        self.add_term_to_terms(self.temp_string)
        self.temp_string = ''
        self.add_term_to_terms(self.current_word)

    def parse_word_that_is_number(self):
        # parse a word that is actually a number (one, thirty ..)
        if self.last_word_category == Parse.NUMBER_WRITTEN_CATEGORY:
            # if we had a number before , e.g.  twenty two, when before we parsed twenty and now two
            new_num = self.constants['numbers'][self.current_word]
            if len(str(new_num)) < len(self.temp_string):
                self.temp_string = str(self.round_without_zeros(self.round_without_zeros(self.temp_string) + new_num))
                self.current_word_category = Parse.NUMBER_WRITTEN_CATEGORY
            else:
                # check for situation when you have something wicked like fifty fifty
                self.current_word = str(new_num)
                self.parse_no_category()
        else:
            self.current_word_category = Parse.NUMBER_WRITTEN_CATEGORY
            self.add_term_to_terms(self.temp_string)
            self.temp_string = str(self.constants['numbers'][self.current_word])

    def parse_word_that_is_big_number(self):
        # parse a word that is a hundered, thousands...
        multiplier = self.constants['big_numbers'][self.current_word]
        if self.last_word_category in (Parse.NUMBER_DD_CATEGORY, Parse.NUMBER_CATEGORY,
                                       Parse.NUMBER_WITH_DOT_CATEGORY, Parse.NUMBER_WRITTEN_CATEGORY):
            self.temp_string = str(self.round_without_zeros(self.round_without_zeros(self.temp_string) * multiplier))
        else:
            self.add_term_to_terms(self.temp_string)
            self.temp_string = str(self.constants['big_numbers'][self.current_word])
        self.current_word_category = Parse.NUMBER_WRITTEN_CATEGORY

    def parse_word_when_is_number(self):
        # parse a word when the boolean is_number indicator is on, i.e. the current token is a number
        if self.date_th is True:
            # parse something like 12th , 10th..
            self.parse_no_category()
        elif self.current_word_category == Parse.PERCENT_CATEGORY:
            # 12%, 12 percent
            self.parse_no_category()
        elif self.num_contains_slash is True:
            # 12/56 ..
            self.parse_num_with_slash()
        elif self.num_contains_dot is True:
            # 123.7856
            self. parse_num_with_dot()
        elif int(self.current_word) <= 99:
            # could be a DD or YY format or just a number
            self.parse_number_less_then_99()
        elif len(self.current_word) == 4:
            # could be year
            self.parse_number_size_four()
        else:
            self.parse_regular_number()

    def parse_num_with_dot(self):
        # parse number that had a dot in it
        self.current_word_category = Parse.NUMBER_WITH_DOT_CATEGORY
        self.current_word = str(self.round_without_zeros(self.current_word))
        if self.temp_string != '':
            self.add_term_to_terms(self.temp_string)
        self.temp_string = self.current_word

    def parse_num_with_slash(self):
        # parse number that had slash in it. could be date or a friction
        self.current_word_category = Parse.NUMBER_WITH_SLASH_CATEGORY
        self.add_term_to_terms(self.temp_string)
        self.temp_string = ''
        self.add_term_to_terms(self.current_word)

    def parse_number_less_then_99(self):
        # could be a YY, DD, or just a regular number
        if self.last_word_category == Parse.MONTH_WITH_DAY_CATEGORY:
            # if the last word that was parsed was something like 10 JANUARY
            self.parse_year_in_date()
        elif int(self.current_word) <= 31:
            # check if DD format
            if self.last_word_category == Parse.MONTH_ONLY_CATEGORY:
                # if we had a month token prior to this token. e.g. JULY before and now 26
                self.temp_string = str(self.add_zero_to_num_less_then_10(self.current_word))\
                                   + '/' + str(self.constants['months'][self.temp_string])
                self.current_word_category = Parse.MONTH_WITH_DAY_CATEGORY
            else:
                # the number is less then 31, so maybe the next token will be a month.
                self.current_word_category = Parse.NUMBER_DD_CATEGORY
                self.add_term_to_terms(self.temp_string)
                self.temp_string = self.add_zero_to_num_less_then_10(self.current_word)
        else:
            # nothing special about this number, go ahead and parse it
            self.parse_regular_number()

    def parse_number_size_four(self):
        # could be a YYYY format
        if self.last_word_category == Parse.MONTH_WITH_DAY_CATEGORY:
            # if we had a month & day before the YYYY
            self.parse_year_in_date()
        elif self.last_word_category == Parse.MONTH_ONLY_CATEGORY:
            # if we had a MM before the YYYY
            self.temp_string = self.constants['months'][self.temp_string]
            self.parse_year_in_date()
        else:
            self.parse_regular_number()

    def parse_year_in_date(self):
        # parsing a year, when prior to it there was a month or day + month
        if len(self.current_word) == 2:
            # if instead of 1991 we have 91
            self.current_word = '19'+ self.current_word
        self.temp_string = self.temp_string + '/' + self.current_word
        self.add_term_to_terms(self.temp_string)
        self.temp_string = ''
        self.current_word_category = Parse.NO_CATEGORY

    def parse_regular_number(self):
        # parse number has nothing special
        self.current_word_category = Parse.NUMBER_CATEGORY
        self.add_term_to_terms(self.temp_string)
        self.temp_string = self.current_word

    def parse_percent(self):
        # parse in case a percent symbol/word shows up
        if self.last_word_category in (Parse.NUMBER_DD_CATEGORY, Parse.NUMBER_CATEGORY,
                                       Parse.NUMBER_WITH_DOT_CATEGORY, Parse.NUMBER_WRITTEN_CATEGORY):
            # check if the last word was a number and make it one word
            self.temp_string = self.temp_string + ' ' + self.constants['percent']
            self.current_word = ''
        self.parse_no_category()

    def parse_capital(self):
        # parse a word that is capitalized
        if self.current_char == " ":
            # we only consider two trailing words to be parsed together if there is a space between them
            # so this if statement tells us whether this word should be considered as capitalized
            self.current_word_category = Parse.CAPITAL_CATEGORY
        if self.temp_string == self.current_word:
            # in case the same word repeats twice, like COIN COIN, don't consider it as two tokens
            self.add_term_to_terms(self.current_word)
            return
        if self.last_word_category == Parse.CAPITAL_CATEGORY:
            # if the last word was capitalized, parse both of them together and separately
            self.add_term_to_terms(self.current_word)
            if self.is_stemming is True:
                stem_term = Parse.stemmed_terms.get(self.current_word, False)
                if stem_term is False:
                    stem_term = self.stemmer.stem(self.current_word)
                    Parse.stemmed_terms[self.current_word] = stem_term
                self.current_word = stem_term
                # self.current_word = self.stemmer.stem(self.current_word)
            self.add_term_to_terms(self.temp_string + ' ' + self.current_word)
            self.temp_string = self.current_word
        else:
            # parse a capital word, save it in case another capital word will show up next
            self.add_term_to_terms(self.temp_string)
            self.add_term_to_terms(self.current_word)
            if self.current_word_category == Parse.CAPITAL_CATEGORY:
                if self.is_stemming is True:
                    stem_term = Parse.stemmed_terms.get(self.current_word, False)
                    if stem_term is False:
                        stem_term = self.stemmer.stem(self.current_word)
                        Parse.stemmed_terms[self.current_word] = stem_term
                    self.temp_string = stem_term
                    # self.temp_string = self.stemmer.stem(self.current_word)
                else:
                    self.temp_string = self.current_word

    def init_vars(self):
        # init vars after parsing a word
        self.last_word = self.current_word
        self.current_word_category = Parse.NO_CATEGORY
        self.is_number = None
        self.num_contains_dot = None
        self.current_word = ''
        self.num_contains_slash = None
        self.is_capital = None
        self.date_th = None

    def init_all(self):
        # init everything
        self.init_vars()
        self.last_word = ''
        self.last_word_category = Parse.NO_CATEGORY
        self.last_char = ''
        self.temp_string = ''

    def parse_char_when_is_number(self):
        # parse a char when we are currently parsing a token considered to be a number
        if self.current_char.isdigit():
            # if it's digit, simply continue
            pass
        elif self.current_char == '.':
            # if it's a dot, add it only in case this is the first dot
            if self.num_contains_dot is None:
                self.num_contains_dot = True
            else:
                return
        elif self.current_char == '/':
            # in case we are parsing a slash like 15/10
            self.num_contains_slash = True
            pass
        elif self.current_char == 't' and len(self.current_word) == 2:
            # check if it's the letter t and the number is only two digits
            self.date_th = True
        elif self.current_char == 'h' and self.date_th is True and self.last_char == 't' is True:
            # if it's the letter h and before it we had DDt
            self.current_word = self.current_word[0:2]
            self.date_th = False
            return
        elif self.current_char == "%":
            # parse a number that has a percent at the end
            if self.num_contains_slash is not True:
                self.current_word = str(self.round_without_zeros(self.current_word))
            self.current_word = self.current_word + ' ' + self.constants['percent']
            self.position = self.position + 1
            self.parse_no_category()
            self.current_char = Parse.ENDING_CHAR
            self.init_vars()
            return
        elif self.current_char.isalpha():
            # if we see a letter, it's not a number anymore
            self.is_number = False
        elif self.current_char == ',':
            # we don't add commas to numbers so skip ahead
            return
        else:
            # any other characters except for the above will be considered as a termination character
            self.parse_word()
            self.current_char = Parse.ENDING_CHAR
            return
        # at the end, add the char into the current string.
        self.current_word += self.current_char
        self.last_char = self.current_char

    def add_term_to_terms(self, term=None):
        # add a term to the terms list
        if term is None:
            return
        term = term.lower().strip()
        if term in self.stop_words or term == '':
            return
        if self.is_stemming is True and (not self.is_number):
            stem_term = Parse.stemmed_terms.get(term, False)
            if stem_term is False:
                stem_term = self.stemmer.stem(term)
                Parse.stemmed_terms[term] = stem_term
            term = stem_term
            #term = self.stemmer.stem(term)
        existing_term = self.terms.get(str(term),False)
        if existing_term is False:
            self.terms[str(term)] = Term.Term(name=str(term), is_header=self.is_header_now,
                                              first_location=self.position, docno=self.docno)
        else:
            existing_term.count += 1
            #
            if existing_term.count > self.max_tf:
                self.max_tf = existing_term.count

    def round_without_zeros(self, num):
        # round the number to the next close integer point, don't add .0 to whole numbers
        rounded = round(float(num), 2)
        return int(rounded) if rounded.is_integer() else rounded

    def add_zero_to_num_less_then_10(self, num):
        # if the number is 1, make it 01, to prevent mismatch in date format of DD/MM/YY
        return '0' + str(num) if len(num) == 1 else str(num)