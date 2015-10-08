'''
Created on 07/nov/2014

@author: Fabio
'''
import config as cfg
import time
import utils
import functools

DEBUG = 2
INFO = 4
WARNING = 16
CRITICAL = 64
FATAL = 128

def log_call(logger):
    def build_decorator(function):
        def core_decorator(*args, **kwargs):
            logger.log("[call] calling " + str(function.__name__), INFO)
            try:
                result = function(*args, **kwargs)
                logger.log("[call] done", INFO)
            except Exception as e:
                logger.log("[call] exception: " + str(e), CRITICAL)
                result = None
                raise e
            return result
        return functools.update_wrapper(core_decorator, function)
    return build_decorator

class Logger(object):
    '''
    classdocs
    '''

    base_path = ""
    echo_log = True
    
    def __init__(self, params=None):
        '''
        Constructor
        '''
        self.base_path = cfg.FOLDER_LOGS
    
    def test(self):
        utils.ensure_dir_exists(self.base_path)
        return True
        
    def get_level_textual(self, level):
        '''
        get textual representation of a log level
        '''
        if (level == INFO):
            return "info"
        elif (level == WARNING):
            return "warning"
        elif (level == CRITICAL):
            return "critical"
        elif (level == FATAL):
            return "fatal"
        elif (level == DEBUG):
            return "debug"
        else:
            return level

    def get_log_line(self, text, level_str):
        current_time = time.time()
        line = str(time.ctime(current_time)) + " "
        line += "[" + str(level_str) + "] " + text
        return line
    
    def get_level_path(self, level):
        path = self.base_path + "/" + self.get_level_textual(level) + ".log"
        utils.ensure_dir_exists(self.base_path)
        return path
    
    def log(self, text, level=None):
        if level is None:
            level = INFO
        
        level_str = self.get_level_textual(level)
        line = self.get_log_line(text, level_str)
        path = self.get_level_path(level)
        
        if self.echo_log:
            print line
        
        if False:
            fp = open(path, 'a')
            fp.write(line + "\r\n")
            fp.close()
            fp = open(self.get_level_path("all"), 'a')
            fp.write(line + "\r\n")
            fp.close()