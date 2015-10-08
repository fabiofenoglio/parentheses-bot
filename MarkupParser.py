'''
Created on 12/mar/2015

@author: Fabio
'''
from ParsedMarkup import ParsedMarkup
import HTMLParser
import re

class MarkupParser(object):
    REGEX_REMOVE_QUOTE = re.compile(ur'<blockquote>(\s|\S)*?</blockquote>')
    REGEX_REMOVE_CODE = re.compile(ur'<code>(\s|\S)*?</code>')
    REGEX_DETECT_OPENING = re.compile(ur'([a-zA-Z ]{3,} *| {3,}|\n{2,}|^|[a-zA-Z]{2,}\. +)\(\s*[a-zA-Z]{3,}', re.MULTILINE)
    REGEX_REMOVE_TAGS = re.compile(ur'<(?:[^>]*)>')
    REGEX_REMOVE_SPACES = re.compile(ur'[ ]{2,}')
    REGEX_REMOVE_NL = re.compile(ur'[\n]{2,}')
        
    html_parser = None

    def __init__(self):
        self.html_parser = HTMLParser.HTMLParser()
        
    def parse(self, comment_html):
        obj = ParsedMarkup()
        obj.raw = comment_html
        obj.html = self.unescape(obj.raw)
        obj.no_blocks = self.remove_quote_and_code(obj.html)
        obj.no_tags = self.unescape(self.remove_html_tags(obj.no_blocks))
        obj.parsable = obj.no_tags
        return obj
        
    def unescape(self, str_to_unescape):
        return self.html_parser.unescape(str_to_unescape)
        
    def remove_quote_and_code(self, str_to_replace, replace = ""):
        if "<blockquote>" in str_to_replace:
            str_to_replace = re.sub(self.REGEX_REMOVE_QUOTE, replace, str_to_replace) 
        if "<code>" in str_to_replace:
            str_to_replace = re.sub(self.REGEX_REMOVE_CODE, replace, str_to_replace)
        return str_to_replace
    
    def remove_html_tags(self, text):
        text = text.replace("<p>", "\n")
        text = text.replace("</p>", "\n")
        text = text.replace("<li>", "\n")
        text = text.replace("</li>", "\n")
        text = re.sub(self.REGEX_REMOVE_TAGS, "", text)
        text = re.sub(self.REGEX_REMOVE_SPACES, "  ", text)
        text = re.sub(self.REGEX_REMOVE_NL, "\n\n", text)
        
        return text
    
    def remove_spacing(self, str_to_replace, replace=" "):
        return re.sub(self.REGEX_REMOVE_SPACING, replace, str_to_replace)

    def detect_unbalance(self, text):
        # Search last open parenthesis
        last_index = text.rfind("(")
        if last_index == -1:
            return False
        
        last_string = text[last_index:]
        pre_string = text[:last_index]
        
        pre_string_index = pre_string.rfind("(")
        if pre_string_index:
            pre_string = pre_string[pre_string_index+1:]
        
        if len(pre_string) < 5:
            return False
        
        match_search_string = pre_string + last_string
        match_result = re.search(self.REGEX_DETECT_OPENING, match_search_string) 
        
        if (match_result is None):
            return False
        
        if not ")" in last_string:
            return True