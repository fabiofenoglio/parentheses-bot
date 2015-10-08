'''
Created on 12/mar/2015

@author: Fabio
'''

class ParsedMarkup(object):

    def __init__(self):
        self.raw = ""
        self.html = ""
        self.no_blocks = ""
        self.no_tags = ""
        self.parsable = ""