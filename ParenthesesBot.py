'''
Created on 17/mar/2015

@author: Fabio
'''
import config as cfg
import helper
import firebase_db
from MarkupParser import MarkupParser
from OperatingStats import OperatingStats
import praw
import template
import ProcessingResult

class ParenthesesBot(object):
    f = None
    r = None
    parser = None
    
    stat = None
    
    COMMENT_DB_DATA_PROPERTIES = None
    
    def __init__(self, params=None):
        self.f = firebase_db.FirebaseDb()
        self.r = praw.Reddit(user_agent=cfg.REDDIT_USER_AGENT)
        self.parser = MarkupParser()
        self.stat = OperatingStats()
        self.COMMENT_DB_DATA_PROPERTIES = ["id", "subreddit_id", "link_id"]
        
    def login(self):
        self.r.login(cfg.REDDIT_USERNAME, cfg.REDDIT_PASSWORD)
        
    def register_comment(self, comment):
        self.stat.unbalanced += 1
        
        # Check already processed
        if self.f.check_already_processed(comment.id):
            return ProcessingResult.ALREADY_PROCESSED
        
        # Check status
        status = self.f.get_record_status(comment.id)
        if status <> firebase_db.RECORD_STATUS_NEW:
            self.stat.already_registered += 1
            return ProcessingResult.ALREADY_REGISTERED
        
        # Register on firebase and send data
        self.f.set_record_status(comment.id, firebase_db.RECORD_STATUS_RESERVED)
        self.f.set_record_data(comment.id, self.build_comment_db_data(comment))
        
        if cfg.AUTO_CONFIRM:
            self.f.set_record_status(comment.id, firebase_db.RECORD_STATUS_CONFIRMED)
        else:
            self.f.set_record_status(comment.id, firebase_db.RECORD_STATUS_REGISTERED)
        
        self.stat.registered += 1
        return ProcessingResult.REGISTERED
        
    def analyze_comment(self, comment, stats=True):
        # Primary analisys
        if stats:
            self.stat.analyzed += 1
        
        if not helper.is_correctly_formatted(comment):
            return ProcessingResult.BAD_FORMAT
        
        if not helper.should_be_parsed(comment.body):
            return ProcessingResult.NOT_NEEDED
        
        if not helper.can_be_parsed(comment.body):
            return ProcessingResult.NOT_PARSABLE
        
        # Parse comment
        parsed = self.parser.parse(comment.body_html)   
        if stats:
            self.stat.parsed += 1     
        
        # Check complexity
        if cfg.CHECK_COMPLEXITY:
            complexity = helper.estimate_complexity(parsed.parsable)
            if complexity > cfg.MAX_COMPLEXITY:
                if stats:
                    self.stat.too_complex += 1
                return ProcessingResult.TOO_COMPLEX
        
        # Check unmatched parenthesis
        if not self.parser.detect_unbalance(parsed.parsable):
            return ProcessingResult.CORRECTLY_CLOSED

        # Check subreddit ban
        if str(comment.subreddit) in cfg.BANNED_FROM:
            return ProcessingResult.BANNED_FROM_SUBREDDIT

        # Check author
        if helper.comment_is_by_me(comment):
            return ProcessingResult.OWN_COMMENT
        
        if comment.author.name in cfg.IGNORE_USERS:
            return ProcessingResult.AUTHOR_BLOCKED
        
        if comment.author.name.lower().endswith("bot"):
            return ProcessingResult.AUTHOR_BLOCKED

        # Found unmatched
        return ProcessingResult.UNBALANCED

    def build_comment_db_data(self, comment):
        vs = helper.filter_object_properties(comment, self.COMMENT_DB_DATA_PROPERTIES)
        vs["subreddit"] = str(comment.subreddit)
        vs["sub_url"] = str(comment.submission.url)
        vs["sub_perma"] = str(comment.submission.permalink)
        return vs
    
    def send_comment(self, comment_id):
        c_data = self.f.get_record_data(comment_id)
        c_url = c_data["sub_perma"] + "" + c_data["id"]
        comments = self.r.get_submission(c_url).comments
        
        if not len(comments):
            self.stat.comment_aborted += 1
            self.f.delete_record(comment_id, firebase_db.RECORD_STATUS_CONFIRMED)
            return ProcessingResult.CORRECTION_ABORTED

        comment = comments[0]

        if self.analyze_comment(comment, stats=False) <> ProcessingResult.UNBALANCED:
            self.stat.comment_aborted += 1
            self.f.delete_record(comment_id, firebase_db.RECORD_STATUS_CONFIRMED)
            return ProcessingResult.CORRECTION_ABORTED
        
        self.f.set_record_status(comment.id, firebase_db.RECORD_STATUS_PROCESSED)
        
        try:
            comment.reply(self.get_corrective_test(comment))
            self.stat.commented += 1
            self.f.delete_record(comment_id, firebase_db.RECORD_STATUS_CONFIRMED)
        except Exception as e:
            self.f.set_record_status(comment.id, firebase_db.RECORD_STATUS_ERROR)
            self.f.add_exception(comment.id, e)
            return ProcessingResult.ERROR
        
        return ProcessingResult.CORRECTED
    
    def get_corrective_test(self, comment):
        c_text = ")"
        
        tmpl = template.load("correction")
        tmpl["correction_text"] = c_text
        tmpl["xkcd_link_text"] = cfg.COMMENT_XKCD_COMIC_LINK_TEXT
        tmpl["xkcd_link"] = cfg.COMMENT_XKCD_COMIC_LINK
        tmpl["bottom_text"] = cfg.COMMENT_BOTTOM_TEXT
        tmpl["pre_link_text"] = cfg.COMMENT_PRE_LINK_TEXT
        
        return tmpl.built()