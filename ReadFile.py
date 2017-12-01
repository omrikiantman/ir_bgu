# ReadFile Class - gets a path with folders and parses each document in each folder
import os
import re
import Document


class ReadFile:
    global_documents = []

    def __init__(self, path):
        # init function
        self.path = path
        for directory in os.listdir(path):
            for doc_file_name in (os.listdir(os.path.join(path, directory))):
                with open(os.path.join(path, directory, doc_file_name), 'r') as doc_file_content:
                    documents_raw = doc_file_content.read()
                    documents = re.findall(r'<DOC>(.*?)</DOC>', documents_raw, re.DOTALL)
                    if documents is not None:
                        for doc in documents:
                            doc = "<DOC>" + doc + "</DOC>"
                            ReadFile.global_documents.append(Document.Document(doc))
