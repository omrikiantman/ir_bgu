#main file for IR course project
from ReadFile import ReadFile
import Parse
import Term
def main():
    try:
        check_me = ReadFile(r'C:\Users\Omri\PycharmProjects\ir_bgu\tests\corpus')
        docs = check_me.global_documents
        root = docs[0]
        print root.text
        print root.tokens.text
        print root.tokens.tokens
    except Exception as err:
        template = "An exception of type {0} occurred. Arguments:{1}"
        message = template.format(type(err).__name__, err)
        print(message)

def tests():
    parsi = Parse.Parse()
    parsi.parse_document("1234\n 12.1  ")
    #a = Term.Term()
    #print a

def catchMe():
    a = 0
    b = 0
    a/b

def catchyou():
    catchMe()

if __name__ == '__main__':
    tests()
    #main()