'''
Created on 13/mar/2015

@author: Fabio
'''
import firebase as fb
import config as cfg
import time

RECORD_STATUS_NEW = 0
RECORD_STATUS_RESERVED = 1
RECORD_STATUS_REGISTERED = 2

RECORD_STATUS_CONFIRMED = 4
RECORD_STATUS_REJECTED = 8
RECORD_STATUS_PROCESSED = 16

RECORD_STATUS_ERROR = 32
RECORD_STATUS_UNKNOWN = 64

def get_fb(path=None):
    url = cfg.FIREBASE_STORAGE_URL
    
    if path is not None:
        if url[-1] == "/":
            url = url[:-1]
        url += "/" + path
        
    if url[-1] <> "/":
        url += "/"
        
    f = fb.FirebaseApplication(url, None)

    return f

def get_app_fb(path=None):
    url = cfg.FIREBASE_STORAGE_URL + cfg.FIREBASE_DATA_URL + "/"
    
    if path is not None:
        if url[-1] == "/":
            url = url[:-1]
        url += "/" + path
        
    if url[-1] <> "/":
        url += "/"
        
    f = fb.FirebaseApplication(url, None)

    return f

class FirebaseDb(object):
    f = None
    f_root = None

    def __init__(self):
        self.f = get_app_fb("records")
        self.f_root = get_app_fb()
        
    def report_stats(self, stats):
        d_to_report = dict()
        v_to_report = vars(stats)
        for k in v_to_report.keys():
            d_to_report[k] = v_to_report[k]
            
        d_to_report["time"] = time.time()
        d_to_report["ctime"] = time.ctime(d_to_report["time"])
            
        self.f_root.put("stats", "execution", d_to_report)
    
    def add_banned_from(self, subreddit_name):
        self.f_root.post("info/banned", subreddit_name)
    
    def add_exception(self, record_id, exception):
        data_dict = dict()
        data_dict["time"] = time.ctime(time.time())
        data_dict["args"] = exception.args
        self.f.post("exceptions/" + record_id, data_dict)

    def get_config_safe(self, key=None, default=None):
        try:
            return self.get_config(key, default)
        except:
            return default
    
    def get_config(self, key=None, default=None):
        val = self.f_root.get("info", key)
        if val is None:
            val = default
        return val

    def delete_record(self, record_id, data=None):
        if data is None:
            data = 0
            
        self.f.delete("data", record_id)
        self.f.put("processed", record_id, data)
        self.f.delete("status", record_id)
        return True

    def check_already_processed(self, record_id):
        val = self.f.get("processed", record_id)
        if val is None:
            return False
        
        return True
    
    def get_records_status(self):
        return self.f.get("status", None)

    def get_record_status(self, record_id):
        val = self.f.get("status", record_id)
        if val is None:
            val = RECORD_STATUS_NEW
            
        return val
    
    def set_record_status(self, record_id, status):
        self.f.put("status", record_id, status)
        return True
        
    def get_record_data(self, record_id):
        return self.f.get("data", record_id)
        
    def set_record_data(self, record_id, data):
        self.f.put("data", record_id, data)
        return True
    
    # TODO use as base for other methods
    def set_record_generic(self, record_id, key, value):
        self.f.put(key, record_id, value)
        return True
    
    # TODO use as base for other methods
    def get_record_generic(self, record_id, key):
        return self.f.get(key, record_id)