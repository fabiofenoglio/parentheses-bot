'''
Created on 08/nov/2014

@author: Fabio
'''
import config as cfg

def load(tmpl_name):
    '''
    Loads a Template instance from the templates folder
    
    sample:
    
    import template
    tmpl = template.load("template-name")
    # this will create a Template instance and load FOLDER_TEMPLATES/template-name.tmpl
    '''
    file_path = cfg.FOLDER_TEMPLATES + "/" + tmpl_name + ".tmpl"
    obj = Template()
    obj.load(file_path)
    return obj

class Template(object):
    '''
    Loads a template from file and fills custom fields
    with provided data
    
    sample:
    
    tmpl = Template()
    tmpl.load("/path/template-file.html")
    
    
    tmpl.set_replace("main_content", "what to insert in the template")
    # totally equivalent to:
    tmpl["main_content"] = "what to insert in the template"
    
    # render the template
    print tmpl.built()
    '''
    ___template_content = ""
    ___replace_dict = None
    ___need_rebuild = True
    ___built = ""

    def __init__(self, file_path=None, params=None):
        '''
        Constructor
        '''
        self.___replace_dict = dict()
        if not (file_path is None):
            self.load(file_path)
    
        self.___need_rebuild = True
    
    def load(self, file_path):
        r_handle = open(file_path, 'r')
        self.___template_content = r_handle.read()
        r_handle.close()
        self.___need_rebuild = True
        
    def set_replace(self, key, value):
        self.___replace_dict[key] = value
        self.___need_rebuild = True
        
    def built(self):
        if self.___need_rebuild:
            self.___rebuild()
            
        return self.___built
    
    def ___rebuild(self):
        self.___built = self.___template_content
        
        for k in self.___replace_dict.keys():
            self.___built = self.___built.replace(self.___get_placeholder(k), self.___replace_dict[k])
        
        self.___need_rebuild = False

    def ___get_placeholder(self, key):
        return "@___" + key.upper() + "___@"

    def __getitem__(self, key):
        return self.___replace_dict[key]
    def __setitem__(self, key, value):
        self.set_replace(key, value)
    def __len__(self):
        return len(self.___replace_dict.keys())
    def __delitem__(self, key):
        del self.___replace_dict[key]
        self.___need_rebuild = True    
    def __str__(self):
        return self.built()