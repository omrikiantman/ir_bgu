from collections import defaultdict
import os
import PostingFile
from TermDict import TermDict
from sys import stdout
import CacheTerm
import Term
import traceback
from string import  ascii_lowercase
import shared_variables as globs
from math import log
import time


class Indexer:
    TEMP_POSTING_PREFIX = 'temp_posting_'
    POSTING_PREFIX = 'posting_'
    STEMMING_PREFIX = 'stemmed_'
    DICTIONARY_PREFIX = 'terms_dict'
    CACHE_PREFIX = 'cache'
    DOCUMENTS_PREFIX = 'documents_dict'
    MAX_TERMS_IN_CACHE = 10000
    SIZE_OF_CACHE = 0.15

    def __init__(self, root_path, is_stemming):
        # init function
        self.temp_parsing_terms_dict = defaultdict(list)
        self.root_path = root_path
        self.is_stemming = is_stemming
        self.main_dict = {}
        self.cache_dict = {}
        self.total_byte_size = 0

    def add_new_term_dict(self, terms):
        # given a dictionary of terms from a new doc, append it to the existing dictionary
        for term_name, term_object in terms.iteritems():
            self.temp_parsing_terms_dict[term_name].append(term_object)

    def flush_dictionary_to_disk_string(self, file_num):
        # write the temp_posting file to disk, reset the current temp_dictionary
        if not bool(self.temp_parsing_terms_dict):
            return
        path = os.path.join(self.root_path,
                            Indexer.STEMMING_PREFIX if self.is_stemming is True else '')\
               + Indexer.TEMP_POSTING_PREFIX + str(file_num) + '.txt'
        with open(path, 'w') as post_file:
            dummy = [post_file.write('{}:{}\n'.format(term_name, term))
                     for term_name, term in sorted(self.temp_parsing_terms_dict.iteritems())]
        self.temp_parsing_terms_dict.clear()
        self.temp_parsing_terms_dict = defaultdict(list)

    def unite_temp_postings(self):
        # unite all the temp postings file and create the inverted index, main dictionary, and cache
        temp_postings_files = []
        print ('START UNITE_TEMP_POSTING - ' + time.strftime("%H:%M:%S"))
        try:
            # open all postings file, read only the first line
            for file_num, posting_file_path in enumerate(os.listdir(self.root_path)):
                prefix = Indexer.STEMMING_PREFIX if self.is_stemming is True else ''
                prefix = prefix + Indexer.TEMP_POSTING_PREFIX
                if posting_file_path.startswith(prefix):
                    temp_postings_files.append(PostingFile.PostingFile(os.path.join(self.root_path, posting_file_path),
                                                                       file_num))
            # find the smallest letter, open the first file by it
            last_letter = smallest_letter = temp_postings_files[0].term_name[0]
            # we have 27 postings file, one for each letter and one for the numbers
            postings_path = os.path.join(self.root_path,
                                         Indexer.STEMMING_PREFIX
                                         if self.is_stemming is True else '') + Indexer.POSTING_PREFIX
            filename = postings_path + str(smallest_letter if smallest_letter.isalpha() else '0')
            filename = filename + '.txt'
            current_writing_file = open(filename, 'w')
            # as long as there are open postings files, i.e. there are terms in the file, keep reading them
            while len(temp_postings_files) > 0:
                # find the smallest word from each file
                smallest_word = temp_postings_files[0].term_name
                postings = temp_postings_files[0].postings
                for posting_file in temp_postings_files[1:]:
                    if posting_file.term_name < smallest_word:
                        smallest_word = posting_file.term_name
                        postings = posting_file.postings
                    elif posting_file.term_name == smallest_word:
                        postings = postings + posting_file.postings
                # read next term for each posting, if the file has ended, remove it from the queue
                for posting_file in temp_postings_files:
                    # a smarter way could maybe be to make an array of files that holds the smallest word
                    if posting_file.term_name == smallest_word:
                        if not posting_file.read_next_term_string():
                            temp_postings_files.remove(posting_file)
                # check if a new file should be opened
                smallest_letter = smallest_word[0]
                if (last_letter != smallest_letter) and (smallest_letter.isalpha()):
                    # if to open a new file
                    self.total_byte_size = self.total_byte_size + current_writing_file.tell()
                    current_writing_file.close()
                    filename = postings_path + smallest_letter + '.txt'
                    current_writing_file = open(filename, 'w')
                    last_letter = smallest_letter
                # sort postings file, calculate tf & df
                sorted_postings = sorted(postings, reverse=True)
                df = len(sorted_postings)
                tf = sum(term.count for term in postings)
                # write to postings file
                postings_text = str(sorted_postings)
                # the 1 & -1 is for removing the brackerts
                postings_row = smallest_word + ':' + postings_text[1:len(postings_text) - 1] + '\n'
                postings_row_bytes = len(postings_row)
                # add to dictionary (tf, df , pointer)
                self.main_dict[smallest_word] = TermDict(smallest_word,
                                                         df, tf, current_writing_file.tell(), postings_row_bytes)
                current_writing_file.write(postings_row)
            self.total_byte_size = self.total_byte_size + current_writing_file.tell()
            current_writing_file.close()
            self.total_byte_size = self.total_byte_size + len(str(self.main_dict))
            # create cache
            self.create_cache()

        except Exception as err:
            print(err)
            traceback.print_exc(file=stdout)
        finally:
            # no matter what, close the temp_postings_files eventually
            for posting_file in temp_postings_files:
                posting_file.file.close()

    def create_cache(self):
        # create the cache from the main program
        print ('START CACHE - ' + time.strftime("%H:%M:%S"))
        posting_file = None
        try:
            # pick 10,000 meaningful words, logic is in the TermDict __cmp__
            temp_cache_dict = {term.name: term for term in
                               sorted(self.main_dict.values(), reverse=True)[0:Indexer.MAX_TERMS_IN_CACHE]}
            # decide on the maximum size of each term in the cache
            cache_size_element = int((Indexer.SIZE_OF_CACHE*self.total_byte_size)/(Indexer.MAX_TERMS_IN_CACHE))
            posting_file_prefix = os.path.join(self.root_path,
                                               Indexer.STEMMING_PREFIX if self.is_stemming is True else '')\
                                  + Indexer.POSTING_PREFIX
            # sort the cache dict, so we will know from which postings file to read
            terms_sorted = [(key, value) for (key, value) in sorted(temp_cache_dict.items())]
            last_active_letter = ''
            for term_name, term_dict in terms_sorted:
                dict_term = self.main_dict[term_name]
                dict_term.is_cache = True
                # find the first letter of the term_name, to know which postings file to read
                file_suffix = (term_name[0] if term_name[0][0].isalpha() else '0')
                if file_suffix != last_active_letter:
                    # if we need to read a new postings file
                    if posting_file is not None:
                        posting_file.close()
                    posting_file_path = posting_file_prefix + file_suffix + '.txt'
                    posting_file = open(posting_file_path)
                # find the position from where we need to read
                posting_file.seek(term_dict.pointer + len(term_name+':'))
                # check if the posting file is bigger than the limit
                if term_dict.bytes <= cache_size_element:
                    line = posting_file.read(term_dict.bytes - len(term_name+':'+'\n'))
                    remaining_bytes = 0
                    pointer = 0
                else:
                    # if it is, read until you reach a comma new line or space
                    line = posting_file.read(cache_size_element - len(term_name+':'+'\n'))
                    last_char = line[len(line) - 1]
                    pointer = term_dict.pointer + cache_size_element
                    remaining_bytes = term_dict.bytes - cache_size_element
                    while True and last_char not in (',', '\n', ' ', '\r'):
                        last_char = posting_file.read(1)
                        if last_char in (',', '\n', ' ', '\r'):
                            break
                        else:
                            line = line + last_char
                            pointer += 1
                            remaining_bytes -= 1
                temp_list = [terms.split('|') for terms in line.split(", ")]
                # if the last element is comma or space, remove it
                temp_list = temp_list if len(temp_list[len(temp_list) - 1]) > 3 else temp_list[0:len(temp_list) - 1]
                doc_list = [Term.Term(name=term_name, count=tf, is_header=is_header,
                                      docno=docno, first_location=first_location)
                            for tf, is_header, first_location, docno in temp_list]
                self.cache_dict[term_name] = CacheTerm.CacheTerm(term_name, pointer, remaining_bytes, doc_list)
        except Exception as err:
            print(err)
            traceback.print_exc(file=stdout)

        finally:
            if posting_file is not None:
                posting_file.close()

    def build_document_weight(self, documents_dict):
        print ('START build_document_weight - ' + time.strftime("%H:%M:%S"))
        file_names = '0' + ascii_lowercase
        num_of_documents = globs.num_of_documents
        for letter in file_names:
            posting_file_path = ''.join([os.path.join(self.root_path,
                                                       Indexer.STEMMING_PREFIX if self.is_stemming is True else ''),
                                          Indexer.POSTING_PREFIX, letter, '.txt'])
            posting_file = PostingFile.PostingFile(posting_file_path, letter, False)
            file_not_closed = True
            while file_not_closed:
                df = len(posting_file.postings)
                for term in posting_file.postings:
                    document =  documents_dict[term.docno]
                    document.weight += (term.get_tf_value()/document.max_tf)\
                                       * log(float(num_of_documents)/float(df), 2)
                file_not_closed = posting_file.read_next_term_string()

