# main file for IR course project
import ReadFile
import yaml
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
    global constants
    global dict_cache_path

    constants = yaml.load(file(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'utils', 'constants.yml'), 'r'))

    root = Tk()
    root.title('Information Retrieval BGU')

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

    quit_button = Button(text='QUIT', fg='red', command=root.destroy)
    quit_button.grid(row=9, column=0)

    root.mainloop()


def run_index():
    # run an entire index build
    global docs_path
    global postings_path
    global is_stemming
    global indexer
    global constants
    global main_dictionary
    global cache
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
        if ('main_dictionary' in globals()) and (main_dictionary is not None) and (bool(main_dictionary)):
            main_dictionary.clear()
        if ('cache' in globals()) and (cache is not None) and (bool(cache)):
            cache.clear()
        # start indexing
        stop_words = load_stop_words(docs_path.get())
        indexer = Indexer.Indexer(postings_path.get(), is_stemming.get())
        read_file = ReadFile.ReadFile(get_corpus_dir(docs_path.get()),
                                      indexer, constants, stop_words, is_stemming.get())
        read_file.index_folder()
        num_of_documents = len(read_file.documents_dict)
        del read_file
        indexer.unite_temp_postings()
        main_dictionary = indexer.main_dict
        # in case want to print stats, uncomment this
        # with open('{}{}'.format('stats', 'stem' if is_stemming.get() else ''),'w') as my_stats_file:
        #    my_stats_file.write('term,tf,df\n'.format())
        #    for key,val in main_dictionary.iteritems():
        #        my_stats_file.write('{},{},{}\n'.format(key,val.tf,val.df))
        cache = indexer.cache_dict
        print ('END TIME - ' + time.strftime("%H:%M:%S"))
        end_time = datetime.now()
        print_stats_at_end_of_indexing(end_time - start_time, num_of_documents)
    except Exception as err:
        tkMessageBox.showinfo('ERROR', err)
        traceback.print_exc(file=stdout)


def print_stats_at_end_of_indexing(time_delta, num_of_documents):
    # print the stats of the indexing session
    global indexer
    global cache
    index_size = indexer.total_byte_size
    cache_size = len(str(cache))
    tkMessageBox.showinfo('NICE',
                          '{} docs were indexed.\n{} is the size of index in bytes.\n{} is the cache size in bytes.'
                          '\n{} is the number of seconds it took for the indexing'
                          .format(num_of_documents, index_size, cache_size, time_delta.seconds))


def get_corpus_dir(path):
    # return the directory of the corpus
    files = os.listdir(path)
    for file in files:
        corpus_dir = os.path.join(path, file)
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
        tkMessageBox.showinfo('ERROR', '{} is not a valid directory'.format(dir_path))
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
    docs_path.set(tkFileDialog.askdirectory())


def browse_postings():
    # assign the potsings path
    global postings_path
    postings_path.set(tkFileDialog.askdirectory())


def reset():
    # reset the memory and delete the postings dear
    global cache
    global main_dictionary
    global postings_path
    try:
        result = tkMessageBox.askquestion("Reset",
                                          "Are you sure you want to reset?\n", icon='warning')
        if result != 'yes':
            return
        if ('main_dictionary' in globals()) and (main_dictionary is not None) and (bool(main_dictionary)):
            main_dictionary.clear()
        if ('cache' in globals()) and (cache is not None) and (bool(cache)):
            cache.clear()
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
    global main_dictionary
    global term_name_listbox
    global tf_listbox
    try:
        if ('main_dictionary' not in globals()) or (main_dictionary is None) or (not bool(main_dictionary)):
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
        for term_name, term_dict_item in sorted(main_dictionary.iteritems()):
            term_name_listbox.insert(END, str(term_name))
            tf_listbox.insert(END, str(term_dict_item.tf))
        term_name_listbox.pack(side=LEFT, fill=BOTH,expand=True)
        term_name_listbox.bind("<MouseWheel>", main_dictionary_mutual_mouse_wheel)
        tf_listbox.pack(side=LEFT, fill=BOTH,expand=True)
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
    global cache
    global cache_name_listbox
    global cache_info_listbox
    try:
        if ('cache' not in globals()) or (cache is None) or (not bool(cache)):
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

        for term_name, term_cache_item in sorted(cache.iteritems()):
            cache_name_listbox.insert(END, str(term_name))
            cache_info_listbox.insert(END, str(term_cache_item.doc_list[0:30]) + '...')
        cache_name_listbox.pack(side=LEFT, fill=BOTH,expand=True)
        cache_name_listbox.bind("<MouseWheel>", cache_mutual_mouse_wheel)
        cache_info_listbox.pack(side=LEFT, fill=BOTH,expand=True)
        cache_info_listbox.bind("<MouseWheel>", cache_mutual_mouse_wheel)

        scrollbar.config(command=cache_mutual_scroll)
    except Exception as err:
        tkMessageBox.showinfo('ERROR', err)
        traceback.print_exc(file=stdout)


def cache_mutual_scroll(*args):
    # force both listboxes to be scrolled together
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
    global cache
    global main_dictionary
    global indexer
    global dict_cache_path
    try:
        if (cache is None) or (main_dictionary is None):
            tkMessageBox.showinfo('ERROR', 'cache is None -  {}.\nmain dictionary is None - {}'
                                  .format(cache is None, main_dictionary is None))
            return
        dict_cache_path.set(tkFileDialog.askdirectory())
        if (dict_cache_path.get() is None) or (dict_cache_path.get() == ''):
            return
        write_cache_dict_to_disk()
        write_main_dict_to_disk()
        tkMessageBox.showinfo('NICE', 'write finished successfully')
    except Exception as err:
        tkMessageBox.showinfo('ERROR', err)
        traceback.print_exc(file=stdout)


def write_main_dict_to_disk():
    # write main terms dictionary to disk
    global dict_cache_path
    global is_stemming
    global main_dictionary
    dict_path = os.path.join(dict_cache_path.get(),
                             STEMMING_PREFIX if is_stemming.get() is True else '') + DICTIONARY_PREFIX
    with open(dict_path, 'w') as dict_file:
        for key, val in main_dictionary.iteritems():
            dict_file.write('{}:{}\n'.format(key, val))


def write_cache_dict_to_disk():
    # write the cache dictionary to disk
    global dict_cache_path
    global is_stemming
    global cache
    dict_path = os.path.join(dict_cache_path.get(),
                                 STEMMING_PREFIX
                                 if is_stemming.get() is True else '') + CACHE_PREFIX
    with open(dict_path, 'w') as dict_file:
        for key, val in cache.iteritems():
            dict_file.write('{}:{}\n'.format(key,val))


def load_dict_cache():
    global cache
    global main_dictionary
    global dict_cache_path
    try:
        dict_cache_path.set(tkFileDialog.askdirectory())
        if (dict_cache_path.get() is None) or (dict_cache_path.get() == ''):
            return
        if ('main_dictionary' in globals()) and (main_dictionary is not None) and (bool(main_dictionary)):
            main_dictionary.clear()
        if ('cache' in globals()) and (cache is not None) and (bool(cache)):
            cache.clear()
        cache_path = os.path.join(dict_cache_path.get(),
                                 STEMMING_PREFIX
                                 if is_stemming.get() is True else '') + CACHE_PREFIX
        cache = CacheTerm.create_cache_from_disk(cache_path)
        dict_path = os.path.join(dict_cache_path.get(),
                                 STEMMING_PREFIX
                                 if is_stemming.get() is True else '') + DICTIONARY_PREFIX
        main_dictionary = TermDict.create_main_dictionary_from_disk(dict_path, cache.keys())

        tkMessageBox.showinfo('OK', 'cache & dictionary loaded')
    except Exception as err:
        tkMessageBox.showinfo('ERROR', err)
        traceback.print_exc(file=stdout)


def load_stop_words(path):
    # input a path and create a stop words set
    path = os.path.join(path,STOP_WORDS_FILE_NAME)
    stop_words_temp = set()
    with open(path,'r') as stop_words_file:
        for word in stop_words_file:
            stop_words_temp.add(''.join(char for char in word if char.isalpha()))
    return stop_words_temp


if __name__ == '__main__':
    gui()



