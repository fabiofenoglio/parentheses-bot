'''
Created on 12/mar/2015

@author: Fabio
'''
import unittest
import praw

import config as cfg
import test
from MarkupParser import MarkupParser
import helper, utils
from MailSender import MailSender
import firebase_db

class Test(unittest.TestCase):
    r = None
    comment_parser = None
    
    @classmethod
    def setUpClass(cls):
        return
        print "Creating Reddit connection as", cfg.REDDIT_USERNAME
        print "user agent", cfg.REDDIT_USER_AGENT
        cls.r = praw.Reddit(user_agent=cfg.REDDIT_USER_AGENT)
        cls.r.login(cfg.REDDIT_USERNAME, cfg.REDDIT_PASSWORD)
        cls.comment_parser = MarkupParser()

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        print cfg.CONSOLE_SEPARATOR
        print "running", self.id()

    def tearDown(self):
        pass

    def testHelperIsAscii(self):
        self.assertTrue(helper.is_ascii(test.resources.TEST_STRING_ASCII))
        self.assertFalse(helper.is_ascii(test.resources.TEST_STRING_UNICODE))

    def testFirebaseConnection(self):
        f = firebase_db.get_fb()
        self.assertEqual(str(f.get("sys/check_connection", None)), "1")
        
    def testFirebaseOperations(self):
        f = firebase_db.get_app_fb()
        print f.dsn
        try:
            print "read", f.get("info", None)
            f.put("unit_test", "test_token", "unit_test : " + cfg.PROGRAM_CODENAME+" " + cfg.PROGRAM_VERSION)
            f.delete("unit_test", "test_token")
        except Exception as e:
            self.fail(e)
        
    def testSendGridConnection(self):
        s = MailSender()
        self.assertTrue(s.test())
        
    @utils.skip(True)
    def testRedditConnection(self):
        self.assertTrue(self.r.is_logged_in())

    def testParseNeedDetector(self):
        for s in test.resources.TEST_STRINGS_SHOULD_NOT_BE_PARSED:
            self.assertFalse(helper.should_be_parsed(s))
        for s in test.resources.TEST_STRINGS_SHOULD_BE_PARSED:
            self.assertTrue(helper.should_be_parsed(s))

    def testParseabilityDetector(self):
        for s in test.resources.TEST_STRINGS_CAN_NOT_BE_PARSED:
            self.assertFalse(helper.can_be_parsed(s))
        for s in test.resources.TEST_STRINGS_CAN_BE_PARSED:
            self.assertTrue(helper.can_be_parsed(s))

    @utils.not_implemented
    def testHelperPostByMe(self):
        pass
    
    @utils.skip(True)
    def testParsing(self):
        parsed = self.comment_parser.parse(test.resources.TEST_STRING_PARSE)

        self.assertTrue("<blockquote>" not in parsed.no_blocks)
        self.assertTrue("</blockquote>" not in parsed.no_blocks)
        self.assertTrue("<code>" not in parsed.no_blocks)
        self.assertTrue("</code>" not in parsed.no_blocks)
        self.assertTrue("  " not in parsed.unspaced)
        
        for smile in test.resources.TEST_SMILES:
            self.assertTrue(smile not in parsed.no_smiles)
        
        self.assertTrue("  " not in parsed.parsable)
    
    @utils.skip(True)
    def testOnOwnPost(self):
        submission = self.r.get_submission(submission_id=test.resources.TEST_OWN_COMMENT_ID)
        parsed = self.comment_parser.parse(submission.selftext_html)
        self.assertEqual(parsed.get_unclosed_parenthesis_level(), 1)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()