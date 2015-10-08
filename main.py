'''
Created on 12/mar/2015

@author: Fabio
'''
import config as cfg
import praw
import time
from ParenthesesBot import ParenthesesBot
import firebase_db
import logger, helper
import ProcessingResult
from Scheduler import Scheduler

# TODO: check for EDIT on past and thank if corrected

def run():
    run_main()

def run_main():
    if cfg.RUNNING_ON_HEROKU:
        print "Starting in HEROKU mode"
        
    lg = logger.Logger()
    
    print "logging in reddit"
    bot = ParenthesesBot()
    bot.login()
    
    subreddit = bot.r.get_subreddit("+".join(cfg.WATCHED_SUBREDDITS))
    
    sc = Scheduler()
    sc.set_job_interval("poster", cfg.TIMING_POSTER_CYCLE)
    sc.set_job_interval("check_config", cfg.TIMING_CONFIG_CHECK)
    sc.set_job_interval("report_stats", cfg.TIMING_REPORT_STATS)
    sc.set_job_interval("check_inbox", cfg.TIMING_CHECK_INBOX)

    while True:
        
        try:
            print "Starting cycle"
            run_mainloop(bot, subreddit, lg, sc)
                    
        except Exception as e:
            lg.log(str(e), logger.CRITICAL)
            time.sleep(cfg.TIMING_ERROR_RESTART)
    
    return

def run_mainloop(bot, subreddit, lg, sc):
    comments = praw.helpers.comment_stream(bot.r, subreddit, cfg.SUBMISSION_PER_REQUEST, 0)

    for comment in comments:
        # Check new comment
        if cfg.RUN_SEARCHER:
            try:
                if bot.analyze_comment(comment) == ProcessingResult.UNBALANCED:
                    bot.register_comment(comment)
                    
            except Exception as e:
                lg.log(str(e), logger.CRITICAL)
        
        # Report stats
        if sc.job_allowed("report_stats"):
            try:
                bot.f.report_stats(bot.stat)
            except Exception as e:
                lg.log(str(e), logger.CRITICAL)
            sc.mark_job_execution("report_stats")
            
        # Check if something to send (timed)
        if sc.job_allowed("poster"):
            if cfg.RUN_POSTER:
                try:
                    run_s0_poster(bot, lg)
                except Exception as e:
                    lg.log(str(e), logger.CRITICAL)
                    
            sc.mark_job_execution("poster")
        
        # Check remote config
        if sc.job_allowed("check_config"):
            try:
                run_s1_config(bot, sc, lg)
            except Exception as e:
                lg.log(str(e), logger.CRITICAL)
                                    
            sc.mark_job_execution("check_config")
            
        # Check inbox
        if sc.job_allowed("check_inbox"):
            try:
                run_s2_inbox(bot, lg)
            except Exception as e:
                lg.log(str(e), logger.CRITICAL)
                
            sc.mark_job_execution("check_inbox")

def run_s2_inbox(bot, lg):
    for msg in bot.r.get_unread(limit=cfg.MAX_MESSAGES_PER_CHECK):
        mark_as_read = False
        
        # Check if ban message
        banned_from = helper.check_ban_message(msg)
        if banned_from is not None:
            lg.log("banned from /r/" + banned_from, logger.INFO)
            if not banned_from in cfg.BANNED_FROM:
                cfg.BANNED_FROM.append(banned_from)
                msg.mark_as_read()
                bot.f.add_banned_from(banned_from)

        if mark_as_read:
            msg.mark_as_read()
            
def run_s1_config(bot, sc, lg):
    try:
        c = bot.f.get_config()
    except Exception as e:
        lg.log(str(e), logger.CRITICAL)
        return False
    
    if "banned" in c:
        cfg.BANNED_FROM = c["banned"].values()
        
    if "ignore_users" in c:
        cfg.IGNORE_USERS = c["ignore_users"].values()
    
    if "poster_sleep_time" in c:
        sc.set_job_interval("poster", int(c["poster_sleep_time"]), mark=False)
    
    if "run_poster" in c:
        cfg.RUN_POSTER = c["run_poster"]
        
    if "run_searcher" in c:
        cfg.RUN_SEARCHER = c["run_searcher"]
    
    return True
    
def run_s0_poster(bot, lg, max_comments=1):
    # check for confirmations/rejections
    statuses = bot.f.get_records_status()

    if statuses is None:
        return False
    
    for comment_id in statuses.keys():
        status = statuses[comment_id]
        if status == firebase_db.RECORD_STATUS_CONFIRMED:
            if max_comments > 0:
                max_comments -= 1
                try:
                    bot.send_comment(comment_id)
                except Exception as e:
                    lg.log(str(e), logger.CRITICAL)
                    bot.f.add_exception(comment_id, e)
                    bot.f.set_record_status(comment_id, firebase_db.RECORD_STATUS_ERROR)

        elif status == firebase_db.RECORD_STATUS_REJECTED:
            bot.stat.rejected += 1
            bot.f.delete_record(comment_id, firebase_db.RECORD_STATUS_REJECTED)

    return True

if __name__ == '__main__':
    run()