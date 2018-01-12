import yaml
import os

global main_dictionary
global num_of_documents
global stop_words
global constants
global documents_dict
global cache
global average_doc_size
global results_files


def init_globs():
    global main_dictionary
    global num_of_documents
    global stop_words
    global constants
    global documents_dict
    global cache
    global average_doc_size
    global average_doc_size_two
    global results_files
    cache = None
    documents_dict = None
    main_dictionary = None
    num_of_documents = None
    stop_words = None
    constants = yaml.load(file(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'utils', 'constants.yml'), 'r'))
    average_doc_size = 0
    results_files = []