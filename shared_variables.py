import yaml
import os

global main_dictionary
global num_of_documents
global stop_words
global constants
global documents_dict
global cache

def init_globs():
    global main_dictionary
    global num_of_documents
    global stop_words
    global constants
    global documents_dict
    global cache
    cache = None
    documents_dict = None
    main_dictionary = None
    num_of_documents = None
    stop_words = None
    constants = yaml.load(file(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'utils', 'constants.yml'), 'r'))