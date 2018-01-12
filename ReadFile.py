# ReadFile Class - gets a path with folders and parses each document in each folder
import os
import re
import Document
import multiprocessing
import time
import Parse
from DocumentDict import DocumentDict
import shared_variables as globs


class ReadFile:

    def __init__(self, documents_path, indexer, constants, stop_words, is_stemming=False):
        # init function
        self.documents_path = documents_path
        self.constants = constants
        self.stop_words = stop_words
        self.is_stemming = is_stemming
        self.documents_dict = {}
        self.indexer = indexer

    def index_folder(self):
        # create temp postings files using multi processors
        b = multiprocessing.cpu_count()
        pool = multiprocessing.Pool(b)
        counter = 0
        file_num = 1
        # only load 10% to the memory, by calculating the number of directories in folder
        num_of_folders = len([dir_num for dir_num in os.listdir(self.documents_path)])
        memory_limit = int(num_of_folders/10) + 1
        for directory in os.listdir(self.documents_path):
            for doc_file_name in (os.listdir(os.path.join(self.documents_path, directory))):
                with open(os.path.join(self.documents_path, directory, doc_file_name), 'r') as doc_file_content:
                    # read the file and separate it by the <DOC> title
                    documents_raw = doc_file_content.read()
                    documents = re.findall(r'<DOC>(.*?)</DOC>', documents_raw, re.DOTALL)
                    if documents is not None:
                        # create a list of all documents, and multi process it
                        documents_to_process = \
                            [(doc, self.constants.copy(), self.stop_words.copy(),
                              self.is_stemming) for doc in documents]
                        term_docs = pool.map(mf_wrap, documents_to_process)

                        for term_doc in term_docs:
                            # add each term from each doc to the indexer dictionary
                            # TODO verify this path is correct
                            # self.documents_dict[term_doc.docno] = \
                            #     DocumentDict(term_doc.docno, term_doc.max_tf, term_doc.length, term_doc.num_of_words,
                            #                  os.path.join(self.documents_path, directory, doc_file_name))
                            self.documents_dict[term_doc.docno] = \
                                DocumentDict(term_doc.docno, term_doc.max_tf, term_doc.length, term_doc.num_of_words,
                                         os.path.join(directory, doc_file_name))
                            self.indexer.add_new_term_dict(term_doc.terms)
                            term_doc.terms.clear()
                            del term_doc
            counter = counter + 1
            if counter == memory_limit:
                # if we need to write the current file to disk and open a new one
                print ('START INDEXING - ' + time.strftime("%H:%M:%S"))
                self.indexer.flush_dictionary_to_disk_string(str(file_num))
                counter = 0
                file_num += 1
                print ('END INDEXING - ' + time.strftime("%H:%M:%S"))
        # at the end, write the last file to disk
        print ('START INDEXING LAST FILE - ' + time.strftime("%H:%M:%S"))
        self.indexer.flush_dictionary_to_disk_string(str(file_num))
        print ('END INDEXING LAST FILE - ' + time.strftime("%H:%M:%S"))
        pool.close()
        pool.join()
        Parse.Parse.stemmed_terms.clear()


def parse_doc(doc, constants, stop_words, is_stemming):
    new_doc = Document.Document(doc, constants, stop_words, is_stemming)
    new_doc.parse_document()
    return new_doc


def mf_wrap(args):
    return parse_doc(*args)
