#parses a document
import xml.etree.ElementTree as ET, Parse
class Document():
    def __init__(self,content):
        self.xml = ET.fromstring(content)
        text = self.xml.find('TEXT')
        self.text = text.text if text is not None else None
        #TODO modify tokens so it will really be tokens
        self.tokens = Parse.Parse(self.text)
