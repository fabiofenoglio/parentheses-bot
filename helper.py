'''
Created on 12/mar/2015

@author: Fabio
'''
import config as cfg
import re
from MarkupParser import MarkupParser

REGEX_BANNED_FROM = re.compile(ur'been banned from posting to /r/([^: ]*)')

def check_ban_message(message):
    if message.distinguished is None:
        return None
    
    if not "banned" in message.subject:
        return None
    
    try:
        if not "moderator" in message.distinguished:
            return None
        if not "banned" in message.body:
            return None
    except:
        return None
    
    parsed = MarkupParser().parse(message.body_html)
    match = re.search(REGEX_BANNED_FROM, parsed.parsable)
    
    if match is None:
        return None
    
    return match.groups()[0]

def should_be_parsed(raw_text):
    return "(" in raw_text

def can_be_parsed(raw_text):
    if (not is_ascii(raw_text)):
        return False
    
    return True

def is_correctly_formatted(comment):
    try:
        comment.body.upper()
        return True
    except:
        # print "body parse error:", vars(comment)
        return False

def comment_is_by_me(comment):
    return (comment.author.name.lower() == cfg.REDDIT_USERNAME.lower())

def estimate_complexity(raw_text):
    estimated = 0
    
    for c in raw_text:
        if (c.isalpha()):
            continue
        elif (c == ' '):
            continue
        elif (c in ['*', '^', ':', ';', ')', '(', '/', '\\', "'", '"']):
            estimated += 5
        elif (not is_ascii(c)):
            estimated += 10
        else:
            estimated += 2
            
    return estimated

def filter_object_properties(o, properties):
    new_o = dict()
    vs = vars(o)
    for k in vs.keys():
        if k not in properties:
            continue
        new_o[k] = vs[k]
    return new_o

def is_ascii(raw_text):
    try:
        raw_text.decode('ascii')
        return True
    except:
        return False