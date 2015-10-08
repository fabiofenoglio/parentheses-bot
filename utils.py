'''
Created on 07/nov/2014

@author: Fabio
'''
import os
import functools

def ensure_dir_exists(path):
    if os.path.isdir(path):
        return True
    
    os.makedirs(path)
    if os.path.isdir(path):
        return True
    
    raise Exception("directory " + str(path) + " does not exist")

def note(argument):
    def build_decorator(function):
        def core_decorator(*args, **kwargs):
            print "[ > note < ]", argument
            return function(*args, **kwargs)
        return functools.update_wrapper(core_decorator, function)
    return build_decorator

def warning(argument):
    def build_decorator(function):
        def core_decorator(*args, **kwargs):
            print "[ >> Warning << ]", argument
            return function(*args, **kwargs)
        return functools.update_wrapper(core_decorator, function)
    return build_decorator

def suppress(return_value=None, echo=True):
    def build_decorator(function):
        def core_decorator(*args, **kwargs):
            if echo:
                print "[ >> suppress << ] suppressing call to " + str(function.__name__) + ", returning " + str(return_value)
            return return_value
        return functools.update_wrapper(core_decorator, function)
    return build_decorator

def force_return(argument):
    def build_decorator(function):
        def core_decorator(*args, **kwargs):
            function(*args, **kwargs)
            return argument
        return functools.update_wrapper(core_decorator, function)
    return build_decorator

def should_return(value):
    def build_decorator(function):
        def core_decorator(*args, **kwargs):
            result = function(*args, **kwargs)
            if result <> value:
                print "[ >> Warning << ] should_return failed: returned " + str(result) + " != " + str(value)
            return result
        return functools.update_wrapper(core_decorator, function)
    return build_decorator

def safe(function):
    def core_decorator(*args, **kwargs):
        exc = None
        result = None
        try:
            result = function(*args, **kwargs)
        except Exception as e:
            exc = e
        return (exc is None, result, exc)
    return functools.update_wrapper(core_decorator, function)
    return core_decorator

def echo_call(function):
    def core_decorator(*args, **kwargs):
        print "[ > call < ] calling " + str(function.__name__)
        try:
            result = function(*args, **kwargs)
            print "[ > call < ] done"
        except Exception as e:
            print "[ > call < ] exception: " + str(e)
            result = None
            raise e
        return result
    return functools.update_wrapper(core_decorator, function)
    return core_decorator

def skip(argument):
    def build_decorator(function):
        def core_decorator(*args, **kwargs):
            print "[ >> Warning << ] Skipping call to function {}".format(function.__name__)
            return argument
        return functools.update_wrapper(core_decorator, function)
    return build_decorator

def dump_call(function):
    argnames = function.func_code.co_varnames[:function.func_code.co_argcount]
    fname = function.func_name

    def core_decorator(*args,**kwargs):
        print "[ > call < ] calling " + fname + "(" + ', '.join(
            '%s=%r' % entry
            for entry in zip(argnames,args) + kwargs.items()) + ")"
        try:
            result = function(*args, **kwargs)
            print "[ > call < ] done:", result
        except Exception as e:
            print "[ > call < ] exception: " + str(e)
            result = None
            raise e
        return result
    return functools.update_wrapper(core_decorator, function)

def deprecated(function):
    def core_decorator(*args, **kwargs):
        print "[ >> Warning << ] Call to deprecated function {}".format(function.__name__)
        return function(*args, **kwargs)
    return functools.update_wrapper(core_decorator, function)

def not_implemented(function):
    def core_decorator(*args, **kwargs):
        print "[ >> Warning << ] Call to non implemented function {}".format(function.__name__)
        return function(*args, **kwargs)
    return functools.update_wrapper(core_decorator, function)