# main file for IR course project
import ReadFile
import time
import traceback
import os
import Indexer
from Tkinter import *
import tkFileDialog
import tkMessageBox
from sys import stdout
from datetime import datetime
import CacheTerm
import TermDict
import shared_variables as globs
from DocnoParser import DocnoParser
import cPickle as Pickle
from Searcher import Searcher

STOP_WORDS_FILE_NAME = 'stop_words.txt'
TEMP_POSTING_PREFIX = 'temp_posting_'
POSTING_PREFIX = 'posting_'
STEMMING_PREFIX = 'stemmed_'
DICTIONARY_PREFIX = 'terms_dict'
CACHE_PREFIX = 'cache'
DOCUMENTS_PREFIX = 'documents_dict'


def gui():
    # run the main gui of the program
    global docs_path
    global postings_path
    global is_stemming
    global dict_cache_path
    global is_docno
    global is_expansion
    global manual_query_path
    global query_guies

    root = Tk()
    root.title('Information Retrieval BGU')

    query_guies = []
    # create all buttons and features of the program
    run_full_index_button = Button(root, text="Run Entire Index", command=run_index)
    run_full_index_button.grid(row=0, sticky='E')

    docs_label = Label(text='Corpus + Stop Words Directory')
    docs_label.grid(row=1, column=0)
    docs_path = StringVar(value='C:/')
    docs_entry = Entry(textvariable=docs_path, width=50)
    docs_entry.grid(row=1, column=1)
    doc_path_button = Button(text="Browse", command=browse_docs)
    doc_path_button.grid(row=1, column=2)

    postings_label = Label(text='Postings + Dictionary + Cache Directory')
    postings_label.grid(row=2, column=0)
    postings_path = StringVar(value='C:/')
    postings_entry = Entry(textvariable=postings_path, width=50)
    postings_entry.grid(row=2, column=1)
    postings_path_button = Button(text="Browse", command=browse_postings)
    postings_path_button.grid(row=2, column=2)

    dict_cache_path = StringVar(value='C:/')

    is_stemming = BooleanVar()
    stem_button = Checkbutton(root, text="Stem?", variable=is_stemming)
    stem_button.grid(row=3, columnspan=2)

    reset_button = Button(text="Reset", command=reset, fg='red')
    reset_button.grid(row=4, column=0)

    show_cache_button = Button(text="Show Cache", command=show_cache)
    show_cache_button.grid(row=5, column=0)

    show_dict_button = Button(text="Show Dictionary", command=show_dict)
    show_dict_button.grid(row=6, column=0)

    save_dict_cache_button = Button(text="Save Dictionary & Cache", command=save_dict_cache)
    save_dict_cache_button.grid(row=7, column=0)

    load_dict_cache_button = Button(text="Load Dictionary & Cache", command=load_dict_cache)
    load_dict_cache_button.grid(row=8, column=0)

    manual_query_label = Label(text='Manual Query')
    manual_query_label.grid(row=9, column=0)
    manual_query_path = StringVar(value='')
    manual_query_entry = Entry(textvariable=manual_query_path, width=50)
    manual_query_entry.grid(row=9, column=1)
    manual_query_button = Button(text="Run", command=run_manual_query)
    manual_query_button.grid(row=9, column=2)

    file_query_label = Label(text='File Query')
    file_query_label.grid(row=10, column=0)
    file_query_button = Button(text="Browse", command=run_file_query)
    file_query_button.grid(row=10, column=1)

    is_expansion = BooleanVar()
    is_expansion_button = Checkbutton(root, text="Expansion?", variable=is_expansion)
    is_expansion_button.grid(row=11, column=0)

    is_docno = BooleanVar()
    is_docno_button = Checkbutton(root, text="Docno?", variable=is_docno)
    is_docno_button.grid(row=11, column=1)

    reset_part_two_button = Button(text="Reset Part Two", fg='red', command=reset_part_two)
    reset_part_two_button.grid(row=12, column=0)

    quit_button = Button(text='QUIT', fg='red', command=root.destroy)
    quit_button.grid(row=13, column=0)

    root.mainloop()


def run_index():
    # run an entire index build
    global docs_path
    global postings_path
    global is_stemming
    global indexer
    global dict_cache_path
    try:
        # check validation conditions
        if (not check_corpus_directory(docs_path.get())) or (not check_postings_directory(postings_path.get())):
            return
        result = tkMessageBox.askquestion("Run Index",
                                          "Are you sure?\n dont worry if the GUI"
                                          " is stuck or not responding - it is working", icon='warning')
        if result != 'yes':
            return
        print ('START TIME - ' + time.strftime("%H:%M:%S"))
        start_time = datetime.now()
        # reset the current memory of the project
        if (globs.main_dictionary is not None) and (bool(globs.main_dictionary)):
            globs.main_dictionary.clear()
        if (globs.cache is not None) and (bool(globs.cache)):
            globs.cache.clear()
        if (globs.documents_dict is not None) and (bool(globs.documents_dict)):
            globs.documents_dict.clear()
        # start indexing
        globs.stop_words = load_stop_words(docs_path.get())
        indexer = Indexer.Indexer(postings_path.get(), is_stemming.get())
        read_file = ReadFile.ReadFile(get_corpus_dir(docs_path.get()),
                                      indexer, globs.constants, globs.stop_words, is_stemming.get())
        read_file.index_folder()
        globs.num_of_documents = len(read_file.documents_dict)
        globs.documents_dict = read_file.documents_dict
        del read_file
        indexer.unite_temp_postings()
        globs.main_dictionary = indexer.main_dict
        indexer.build_document_weight(globs.documents_dict)
        # in case want to print stats, uncomment this
        # with open('{}{}'.format('stats', 'stem' if is_stemming.get() else ''),'w') as my_stats_file:
        #    my_stats_file.write('term,tf,df\n'.format())
        #    for key,val in main_dictionary.iteritems():
        #        my_stats_file.write('{},{},{}\n'.format(key,val.tf,val.df))
        globs.cache = indexer.cache_dict
        dict_cache_path = postings_path
        print ('END TIME - ' + time.strftime("%H:%M:%S"))
        end_time = datetime.now()
        print_stats_at_end_of_indexing(end_time - start_time)
    except Exception as err:
        tkMessageBox.showinfo('ERROR', err)
        traceback.print_exc(file=stdout)


def print_stats_at_end_of_indexing(time_delta):
    # print the stats of the indexing session
    global indexer
    index_size = indexer.total_byte_size
    cache_size = len(str(globs.cache))
    tkMessageBox.showinfo('NICE',
                          '{} docs were indexed.\n{} is the size of index in bytes.\n{} is the cache size in bytes.'
                          '\n{} is the number of seconds it took for the indexing'
                          .format(globs.num_of_documents, index_size, cache_size, time_delta.seconds))


def get_corpus_dir(path):
    # return the directory of the corpus
    files = os.listdir(path)
    for file_name in files:
        corpus_dir = os.path.join(path, file_name)
        if os.path.isdir(corpus_dir):
            return corpus_dir


def check_corpus_directory(path):
    # check validation conditions for the corpus directory
    if (not check_if_directory(path)) or \
            (not check_if_stop_words_file_exists(path))\
            or (not check_if_one_dir(path)) or (not check_if_more_than_two_files(path)):
        return False
    return True


def check_postings_directory(path):
    # check validation conditions for the postings directory
    if not check_if_directory(path):
        return False
    return True


def check_if_directory(dir_path):
    # check if a path is a valid directory
    is_dir = os.path.isdir(dir_path)
    if not is_dir:
        tkMessageBox.showinfo('ERROR', 'stop_words & corpus directory - {} is not a valid directory'.format(dir_path))
    return is_dir


def check_if_stop_words_file_exists(stop_words_path):
    # check if the stop_words file exists in a given directory
    is_stop_words = os.path.isfile(os.path.join(stop_words_path, STOP_WORDS_FILE_NAME))
    if not is_stop_words:
        tkMessageBox.showinfo(
            'ERROR', '{} does not exist in {} directory'.format(STOP_WORDS_FILE_NAME, stop_words_path))
    return is_stop_words


def check_if_one_dir(path):
    # check if a directory exists in some path
    files = os.listdir(path)
    for one_file in files:
        if os.path.isdir(os.path.join(path, one_file)):
            return True
    tkMessageBox.showinfo(
        'ERROR', 'There is no directory in {}'.format(path))
    return False


def check_if_more_than_two_files(path):
    # check if there are more than two files
    files = os.listdir(path)
    count = 0
    for one_file in files:
        count += 1
        if count > 2:
            tkMessageBox.showinfo('ERROR', 'There is more than two files in {}'.format(path))
            return False
    return True


def browse_docs():
    # assign the documents/corpus path
    global docs_path
    docs_dir = tkFileDialog.askdirectory()
    if docs_dir is None or docs_dir == '':
        return
    docs_path.set(docs_dir)


def browse_postings():
    # assign the potsings path
    global postings_path
    postings_dir = tkFileDialog.askdirectory()
    if postings_dir is None or postings_dir == '':
        return
    postings_path.set(postings_dir)


def reset():
    # reset the memory and delete the postings dear
    global postings_path
    try:
        result = tkMessageBox.askquestion("Reset",
                                          "Are you sure you want to reset?\n", icon='warning')
        if result != 'yes':
            return
        if (globs.main_dictionary is not None) and (bool(globs.main_dictionary)):
            globs.main_dictionary.clear()
        if (globs.cache is not None) and (bool(globs.cache)):
            globs.cache.clear()
        if (globs.documents_dict is not None) and (bool(globs.documents_dict)):
            globs.documents_dict.clear()
        if check_postings_directory(postings_path.get()):
            for del_file in os.listdir(postings_path.get()):
                del_file_path = os.path.join(postings_path.get(), del_file)
                os.unlink(del_file_path)
        tkMessageBox.showinfo('OK', 'folder was deleted and memory has been reset')
    except Exception as err:
        tkMessageBox.showinfo('ERROR', err)
        traceback.print_exc(file=stdout)


def show_dict():
    # show main dictionary
    global term_name_listbox
    global tf_listbox
    try:
        if (globs.main_dictionary is None) or (not bool(globs.main_dictionary)):
            tkMessageBox.showinfo('ERROR', 'currently, no dictionary is loaded')
            return
        main_dict_gui = Toplevel()
        main_dict_gui.title("Main Dictionary")

        scrollbar = Scrollbar(main_dict_gui)
        scrollbar.pack(side=RIGHT, fill=Y)

        term_name_listbox = Listbox(main_dict_gui, yscrollcommand=scrollbar.set)
        term_name_listbox.insert(END, 'Term Name')
        tf_listbox = Listbox(main_dict_gui, yscrollcommand=scrollbar.set)
        tf_listbox.insert(END, 'Term Frequency')
        for term_name, term_dict_item in sorted(globs.main_dictionary.iteritems()):
            term_name_listbox.insert(END, str(term_name))
            tf_listbox.insert(END, str(term_dict_item.tf))
        term_name_listbox.pack(side=LEFT, fill=BOTH, expand=True)
        term_name_listbox.bind("<MouseWheel>", main_dictionary_mutual_mouse_wheel)
        tf_listbox.pack(side=LEFT, fill=BOTH, expand=True)
        tf_listbox.bind("<MouseWheel>", main_dictionary_mutual_mouse_wheel)

        scrollbar.config(command=main_dictionary_mutual_scroll)

    except Exception as err:
        tkMessageBox.showinfo('ERROR', err)
        traceback.print_exc(file=stdout)


def main_dictionary_mutual_scroll(*args):
    # force both listboxes to be scrolled together
    global term_name_listbox
    global tf_listbox
    term_name_listbox.yview(*args)
    tf_listbox.yview(*args)


def main_dictionary_mutual_mouse_wheel(event):
    # a function that will make the two term & tf lists scroll together by the mouse
    global term_name_listbox
    global tf_listbox
    term_name_listbox.yview("scroll", event.delta, "units")
    tf_listbox.yview("scroll", event.delta, "units")
    return "break"


def show_cache():
    # show the cache
    global cache_name_listbox
    global cache_info_listbox
    try:
        if (globs.cache is None) or (not bool(globs.cache)):
            tkMessageBox.showinfo('ERROR', 'currently, no cache is loaded')
            return
        cache_gui = Toplevel()
        cache_gui.title("Cache")

        scrollbar = Scrollbar(cache_gui)
        scrollbar.pack(side=RIGHT, fill=Y)

        cache_name_listbox = Listbox(cache_gui, yscrollcommand=scrollbar.set)
        cache_name_listbox.insert(END, 'Term Name')
        cache_info_listbox = Listbox(cache_gui, yscrollcommand=scrollbar.set)
        cache_info_listbox.insert(END, 'tf|is_header|first_location|docno')

        for term_name, term_cache_item in sorted(globs.cache.iteritems()):
            cache_name_listbox.insert(END, str(term_name))
            cache_info_listbox.insert(END, str(term_cache_item.doc_list[0:30]) + '...')
        cache_name_listbox.pack(side=LEFT, fill=BOTH, expand=True)
        cache_name_listbox.bind("<MouseWheel>", cache_mutual_mouse_wheel)
        cache_info_listbox.pack(side=LEFT, fill=BOTH, expand=True)
        cache_info_listbox.bind("<MouseWheel>", cache_mutual_mouse_wheel)

        scrollbar.config(command=cache_mutual_scroll)
    except Exception as err:
        tkMessageBox.showinfo('ERROR', err)
        traceback.print_exc(file=stdout)


def cache_mutual_scroll(*args):
    # force both list boxes to be scrolled together
    global cache_name_listbox
    global cache_info_listbox
    cache_name_listbox.yview(*args)
    cache_info_listbox.yview(*args)


def cache_mutual_mouse_wheel(event):
    # a function that will make the two term & cache_info lists scroll together
    global cache_name_listbox
    global cache_info_listbox
    cache_name_listbox.yview("scroll", event.delta, "units")
    cache_info_listbox.yview("scroll", event.delta, "units")
    return "break"


def save_dict_cache():
    # save the cache and terms dictionary to disk
    global indexer
    global dict_cache_path
    try:
        if not check_dictionaries_loaded():
            return
        dict_cache_path.set(tkFileDialog.askdirectory())
        if (dict_cache_path.get() is None) or (dict_cache_path.get() == ''):
            return
        write_cache_dict_to_disk()
        write_main_dict_to_disk()
        write_documents_dict_to_disk()

        tkMessageBox.showinfo('NICE', 'write finished successfully')
    except Exception as err:
        tkMessageBox.showinfo('ERROR', err)
        traceback.print_exc(file=stdout)


def check_dictionaries_loaded():
    if (globs.cache is None) or (globs.main_dictionary is None) or (globs.documents_dict is None):
        tkMessageBox.showinfo('ERROR', 'cache is None -  {}.\nmain dictionary is None - {}'
                                       '.\ndocuments_dict is None - {}'
                              .format(globs.cache is None,
                                      globs.main_dictionary is None, globs.documents_dict is None))
        return False
    return True


def write_documents_dict_to_disk():
    global dict_cache_path
    global is_stemming
    dict_path = os.path.join(dict_cache_path.get(),
                             STEMMING_PREFIX if is_stemming.get() is True else '') + DOCUMENTS_PREFIX
    with open(dict_path, 'wb') as dict_file:
        Pickle.dump(globs.documents_dict, dict_file)
        Pickle.dump(len(globs.documents_dict), dict_file)


def write_main_dict_to_disk():
    # write main terms dictionary to disk
    global dict_cache_path
    global is_stemming
    dict_path = os.path.join(dict_cache_path.get(),
                             STEMMING_PREFIX if is_stemming.get() is True else '') + DICTIONARY_PREFIX
    with open(dict_path, 'w') as dict_file:
        for key, val in globs.main_dictionary.iteritems():
            dict_file.write('{}:{}\n'.format(key, val))


def write_cache_dict_to_disk():
    # write the cache dictionary to disk
    global dict_cache_path
    global is_stemming
    dict_path = os.path.join(dict_cache_path.get(),
                             STEMMING_PREFIX if is_stemming.get() is True else '') + CACHE_PREFIX
    with open(dict_path, 'w') as dict_file:
        for key, val in globs.cache.iteritems():
            dict_file.write('{}:{}\n'.format(key, val))


def load_dict_cache():
    global dict_cache_path
    try:
        dict_cache_path.set(tkFileDialog.askdirectory())
        # TODO verify that a path was chosen
        if (dict_cache_path.get() is None) or (dict_cache_path.get() == ''):
            return
        if (globs.main_dictionary is not None) and (bool(globs.main_dictionary)):
            globs.main_dictionary.clear()
        if (globs.cache is not None) and (bool(globs.cache)):
            globs.cache.clear()
        if (globs.documents_dict is not None) and (bool(globs.documents_dict)):
            globs.documents_dict.clear()
        # the utils is hardcoded due to a clarification stated in the forum
        globs.stop_words = load_stop_words('utils')
        cache_path = os.path.join(dict_cache_path.get(),
                                  STEMMING_PREFIX if is_stemming.get() is True else '') + CACHE_PREFIX
        globs.cache = CacheTerm.create_cache_from_disk(cache_path)
        dict_path = os.path.join(dict_cache_path.get(),
                                 STEMMING_PREFIX if is_stemming.get() is True else '') + DICTIONARY_PREFIX
        globs.main_dictionary = TermDict.create_main_dictionary_from_disk(dict_path, globs.cache.keys())
        documents_dict_path = os.path.join(dict_cache_path.get(),
                                           STEMMING_PREFIX if is_stemming.get() is True else '') + DOCUMENTS_PREFIX
        with open(documents_dict_path, 'rb') as fp:
            globs.documents_dict = Pickle.load(fp)
            globs.num_of_documents = Pickle.load(fp)
        # TODO make sure the documents dict is included in all of the exams
        tkMessageBox.showinfo('OK', 'cache & dictionary loaded')
    except Exception as err:
        tkMessageBox.showinfo('ERROR', err)
        traceback.print_exc(file=stdout)


def load_stop_words(path):
    # input a path and create a stop words set
    path = os.path.join(path, STOP_WORDS_FILE_NAME)
    stop_words_temp = set()
    with open(path, 'r') as stop_words_file:
        for word in stop_words_file:
            stop_words_temp.add(''.join(char for char in word if char.isalpha()))
    return stop_words_temp


def run_manual_query():
    # parse a manual query - could be a docno or a query
    # TODO verify that main dictionary is loaded
    global is_docno
    global manual_query_path
    global docs_path
    global is_expansion
    query = manual_query_path.get().strip()
    if not bool(query):
        tkMessageBox.showinfo('ERROR', 'the manual query field is empty')
        return
    if not check_dictionaries_loaded():
        return

    if is_docno.get():
        run_docno(query)
        return

    if is_expansion.get():
        run_expansion()
        return

    queries_gui([run_one_query(query)])


def run_one_query(query, num_of_docs=50):
    global is_stemming
    global dict_cache_path
    start_time = datetime.now()
    searcher = Searcher(query, is_stemming.get(), dict_cache_path.get())
    ranked_documents = searcher.search_query()
    elapsed_time = (datetime.now() - start_time).seconds
    return ranked_documents[:num_of_docs], query, elapsed_time


def queries_gui(queries_results):
    global query_guies
    query_gui = Toplevel()
    query_guies.append(query_gui)
    query_gui.title("Query GUI")

    scrollbar_docno = Scrollbar(query_gui)
    scrollbar_docno.pack(side=RIGHT, fill=Y)

    results_text = Text(query_gui, yscrollcommand=scrollbar_docno.set, height=20, width=140)

    scrollbar_docno.config(command=results_text.yview)
    for i, (ranked_documents, query ,elapsed_time) in enumerate(queries_results):
        results_text.insert(END,
                            '\n{}.Query - \"{}\". {} documents returned in {} seconds\nDocnos:'
                            .format(i+1, query, len(ranked_documents), elapsed_time))
        for j, document in enumerate(ranked_documents):
            if j % 10 == 0:
                results_text.insert(END,'\n')
            results_text.insert(END, '{} '.format(document.docno))

    results_text.pack(side=LEFT, fill=BOTH, expand=True)
    save_results_button = Button(query_gui, text="Save", command=lambda: save_results(queries_results), fg='blue')
    save_results_button.pack()


def save_results(queries_results):
    print "save_results"
    print queries_results


def run_docno(docno):
    global is_stemming
    document = globs.documents_dict.get(docno.upper(), False)
    if document is False:
        tkMessageBox.showinfo('ERROR', 'no such docno - {}'.format(docno))
        return
    docno_parser = DocnoParser(docno, document.file_name, is_stemming.get(), document.max_tf)
    if not (docno_parser.load_docno()):
        tkMessageBox.showinfo('ERROR', 'something went wrong'.format(docno))
        return
    top_5_sentences = docno_parser.find_top_5_sentences()
    docno_gui = Toplevel()
    docno_gui.title("Top 5 Sentences in Docno {}".format(docno))

    scrollbar_docno = Scrollbar(docno_gui)
    scrollbar_docno.pack(side=RIGHT, fill=Y)

    docno_text = Text(docno_gui, yscrollcommand=scrollbar_docno.set, height=20, width=100)
    docno_text.insert(END, 'Sentences Ranking for docno - {}\n'.format(docno))

    scrollbar_docno.config(command=docno_text.yview)
    for i, sentence_with_rank in enumerate(sorted(top_5_sentences, key=lambda tup: tup[2])):
        sentence = re.sub(' +', ' ', sentence_with_rank[0])
        docno_text.insert(END, "{}. Score:{}\n {}\n".format(i+1, sentence_with_rank[1], sentence))

    docno_text.pack(side=LEFT, fill=BOTH, expand=True)


def run_file_query():
    print 'file query'
    filename = tkFileDialog.askopenfilename()
    print (filename)


def run_expansion():
    print 'expansion'


def reset_part_two():
    global query_guies
    print 'reset_part_two'
    if not check_dictionaries_loaded():
        return
    # TODO - add are you sure reset..
    # TODO - verify query guies is not empty
    for gui in query_guies:
        gui.destroy()
    query_guies = []


if __name__ == '__main__':
    globs.init_globs()
    gui()

# TODO - in report & labs, download nltk punkt like this - import nltk, nltk.download('punkt')
# TODO - install wikipedia open source
