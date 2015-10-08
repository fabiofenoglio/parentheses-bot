'''
Created on 20/mar/2015

@author: Fabio
'''
import time

class Scheduler(object):
    # properties
    
    timestamps = None
    intervals = None
    
    def __init__(self):
        self.timestamps = dict()
        self.intervals = dict()
        
    def set_job_interval(self, key, interval, mark=True, desync=0):
        self.intervals[key] = interval
        if mark:
            if desync > 0:
                self.mark_job_execution(key, time.time() + desync)
            else:
                self.mark_job_execution(key)
        elif desync:
            self.mark_job_execution(key, time.time() - interval + desync)
        
    def mark_job_execution(self, key, at_time=None):
        if at_time is None:
            at_time = time.time()
        self.timestamps[key] = at_time
        
    def job_allowed(self, key):
        if not key in self.intervals:
            raise Exception("job interval not registered")
        
        if not key in self.timestamps:
            return True
        
        if ((time.time() - self.timestamps[key]) >= self.intervals[key]):
            return True
        
        return False