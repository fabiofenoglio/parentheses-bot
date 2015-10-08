'''
Created on 07/nov/2014

@author: Fabio
'''
import config as cfg
import sendgrid

class MailSender(object):
    '''
    Sends emails using SendGrid service
    '''
    sg_username = ""
    sg_password = ""
    sg_dispatch_key = ""
    
    default_from_addr = ""
    default_from_name = ""
    default_reply_to = ""

    ___sg = None

    def __init__(self, params=None):
        '''
        Constructor
        '''
        self.sg_username = cfg.SG_USER
        self.sg_password = cfg.SG_PASSWORD
        self.default_from_addr = cfg.MAIL_OUT_FROM
        self.default_from_name = cfg.MAIL_OUT_FROM_NAME
        self.default_reply_to = cfg.MAIL_OUT_REPLY_TO
        self.sg_dispatch_key = cfg.SG_DISPATCH_KEY
        
        self.___sg = sendgrid.SendGridClient(self.sg_username, self.sg_password)
    
    def test(self):
        if self.___sg is None:
            self.___sg = sendgrid.SendGridClient(self.sg_username, self.sg_password)
            self.___sg = None
        return True
        
    def get_message(self, subject=None, to=None, html=None, text=None):
        m = sendgrid.Mail()
        m.add_unique_arg("dispatch-key", self.sg_dispatch_key)
        m.add_category(cfg.SG_MAIL_CATEGORIES)
        m.set_replyto(self.default_reply_to)
        m.set_from(self.default_from_name + " <" + self.default_from_addr + ">")
        
        if not (to is None):
            m.add_to(to)
            
        if not (html is None):
            m.set_html(html)
        
        if not (text is None):
            m.set_text(text)
        
        if subject is None:
            m.set_subject("Notizie dal server")
        else:
            m.set_subject(subject)
        return m
        
    def send_message(self, message):
        status, msg = self.___sg.send(message)
        if (status == 200):
            return True
        else:
            raise Exception("error sending mail: " + str(msg))